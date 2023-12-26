from collections.abc import Callable
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, BinaryIO

import lxml.etree as ET

from core.interfaces import XMLDataProcessor, XMLDiffProcessor, XMLParser
from core.normalizers import ExponentialMovingAverage


class ViaComParser(XMLParser):
    def parse(self, xml: BinaryIO) -> ET._Element:
        return ET.parse(xml).getroot()


class ViaComRoundtripMixin:
    def roundtrip(self, parser: ViaComParser) -> bool:
        return True if parser.XML.find("PricedItineraries/Flights/ReturnPricedItinerary") else False  # noqa: SIM210


class ViaComDataProcessor(XMLDataProcessor, ViaComRoundtripMixin):
    parser: ViaComParser

    def all_itineraries(self) -> list[ET._Element]:
        return self._all_itineraries()

    def specified_itineraries(
        self, source: str, destination: str, *, direct: bool = False, transit: bool = False
    ) -> list[ET._Element]:
        return self._specified_itineraries(source, destination, direct, transit)

    def optimal_itinerary(self) -> ET._Element | list[ET._Element]:
        return self._find_best_value_ininerary(
            finder=self._optimal_itinerary, comparator=lambda current_optimal, best: current_optimal <= best
        )

    def most_expensive_itinerary(self) -> ET._Element | list[ET._Element]:
        return self._find_best_value_ininerary(
            finder=self._itinerary_price, comparator=lambda current_price, best: current_price > best
        )

    def cheapest_itinerary(self) -> ET._Element | list[ET._Element]:
        return self._find_best_value_ininerary(
            finder=self._itinerary_price, comparator=lambda current_price, best: current_price < best
        )

    def longest_itinerary(self) -> ET._Element | list[ET._Element]:
        return self._find_best_value_ininerary(
            finder=self._interary_duration, comparator=lambda current_time, best: current_time > best
        )

    def shortest_itinerary(self) -> ET._Element | list[ET._Element]:
        return self._find_best_value_ininerary(
            finder=self._interary_duration, comparator=lambda current_time, best: current_time < best
        )

    def _find_best_value_ininerary(
        self,
        finder: Callable[[Any], Any],
        comparator: Callable[[Any, Any], bool],
    ) -> Any | list[Any]:
        selected_itinerary = []
        best_value = None

        for itinerary in self._all_itineraries():
            current_value = finder(itinerary)

            if best_value is None or comparator(current_value, best_value):
                selected_itinerary = [itinerary]
                best_value = current_value
            elif current_value == best_value:
                selected_itinerary.append(itinerary)

        return selected_itinerary if len(selected_itinerary) > 1 else selected_itinerary[0]

    def _all_itineraries(self) -> list[ET._Element]:
        return self.parser.XML.xpath("PricedItineraries/Flights")

    def _specified_itineraries(self, source: str, destination: str, direct: bool, transit: bool) -> list[ET._Element]:
        if transit:
            request = 'PricedItineraries/Flights[.//Source="{0}" and .//Destination="{1}" {2}]'
        else:
            request = 'PricedItineraries/Flights[.//Flight[1]/Source="{0}" and .//Flight[last()]/Destination="{1}" {2}]'

        direct_flights_filter = """
        and
        (
            (
                ./ReturnPricedItinerary
                and
                count(./OnwardPricedItinerary/Flights/Flight) = 1
                and
                count(./ReturnPricedItinerary/Flights/Flight) = 1
            )
            or
            (
                count(./OnwardPricedItinerary/Flights/Flight) = 1
            )
        )
        """

        filter_condition = direct_flights_filter if direct else ""
        return self.parser.XML.xpath(request.format(source, destination, filter_condition))

    def _optimal_itinerary(
        self,
        itinerary: ET._Element,
        *,
        price_weight: Decimal = Decimal("0.7"),
        duration_weight: Decimal = Decimal("0.3"),
        ema_alpha: Decimal = Decimal("0.1"),
    ) -> Decimal:
        price = self._itinerary_price(itinerary)
        delta = self._interary_duration(itinerary)
        duration = Decimal(str(round(delta.total_seconds() / 3600, 2)))

        self.price_normalizer = getattr(self, "price_normalizer", ExponentialMovingAverage(alpha=ema_alpha))
        self.duration_normalizer = getattr(self, "duration_normalizer", ExponentialMovingAverage(alpha=ema_alpha))

        self.price_normalizer.update(price)
        price = self.price_normalizer.normalize(price)

        self.duration_normalizer.update(duration)
        price = self.duration_normalizer.normalize(duration)

        return price_weight * price + duration_weight * duration  # Weighted sum model

    def _itinerary_price(self, itinerary: ET._Element) -> Decimal:
        return sum(  # type: ignore
            [
                Decimal(price.text)  # type: ignore
                for price in itinerary.find("Pricing").iterfind('ServiceCharges[@ChargeType="TotalAmount"]')  # type: ignore
            ]
        )

    def _get_itinerary_duration(self, flights: list[ET._Element]) -> timedelta:
        first_flight = flights[0]
        last_flight = flights[-1]

        start_datetime = datetime.strptime(first_flight.find("DepartureTimeStamp").text, r"%Y-%m-%dT%H%M")  # type: ignore
        end_datetime = datetime.strptime(last_flight.find("ArrivalTimeStamp").text, r"%Y-%m-%dT%H%M")  # type: ignore

        return end_datetime - start_datetime

    def _onward_itinerary_duration(self, itinerary: ET._Element) -> timedelta:
        flights = itinerary.find("OnwardPricedItinerary/Flights").getchildren()  # type: ignore
        return self._get_itinerary_duration(flights)

    def _return_itinerary_duration(self, itinerary: ET._Element) -> timedelta:
        flights = itinerary.find("ReturnPricedItinerary/Flights").getchildren()  # type: ignore
        return self._get_itinerary_duration(flights)

    def _interary_duration(self, itinerary: ET._Element) -> timedelta:
        onward_delta = self._onward_itinerary_duration(itinerary)
        if self.roundtrip(self.parser):
            return_delta = self._return_itinerary_duration(itinerary)
            return return_delta + onward_delta
        return onward_delta


class ViaComDiffProcessor(XMLDiffProcessor, ViaComRoundtripMixin):
    parser: ViaComParser

    def is_roundtrip(self) -> bool:
        return self.roundtrip(self.parser)

    def ticket_types(self) -> set[str]:
        pricing = self.parser.XML.xpath(
            ".//PricedItineraries/Flights[1]/Pricing/ServiceCharges[@ChargeType='TotalAmount']"
        )
        return set(price.get("type") for price in pricing)

    def unique_itineraries(self, return_itineraries: bool) -> set[tuple[str, ...]]:
        unique = set()

        for itinerary in self.parser.XML.xpath("//Flights"):
            onward_sources = itinerary.xpath(".//OnwardPricedItinerary/Flights/Flight/Source/text()")
            onward_destinations = itinerary.xpath(".//OnwardPricedItinerary/Flights/Flight/Destination/text()")
            onward_result = tuple(
                f"{source}-{destination}"
                for source, destination in zip(onward_sources, onward_destinations, strict=True)
            )
            unique.add(onward_result)

            if return_itineraries:
                return_sources = itinerary.xpath(".//ReturnPricedItinerary/Flights/Flight/Source/text()")
                return_destinations = itinerary.xpath(".//ReturnPricedItinerary/Flights/Flight/Destination/text()")
                return_result = tuple(
                    f"{source}-{destination}"
                    for source, destination in zip(return_sources, return_destinations, strict=True)
                )
                unique.add(return_result)

        unique.discard(tuple())
        return unique


# breakpoint()
