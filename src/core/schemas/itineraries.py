from decimal import Decimal
from typing import TypeAlias

from pydantic import ConfigDict, Field, field_serializer, field_validator
from pydantic_xml import BaseXmlModel, attr, element

from core.types import datetime


currency: TypeAlias = str  # noqa: UP040


class Carrier(BaseXmlModel, tag="Carrier"):
    id_: str = attr(name="id", alias="id")
    carrier: str


class Flight(BaseXmlModel, tag="Flight"):
    model_config = ConfigDict(populate_by_name=True)

    carrier: Carrier
    flight_number: int = element(tag="FlightNumber")
    source: str = element(tag="Source")
    destination: str = element(tag="Destination")
    departure_time_stamp: datetime = element(tag="DepartureTimeStamp")
    arrival_time_stamp: datetime = element(tag="ArrivalTimeStamp")
    class_: str = element(tag="Class", alias="class")
    number_of_stops: int = element(tag="NumberOfStops")
    fare_basis: str = element(tag="FareBasis")
    warning_text: str | None = element(tag="WarningText", default=None)
    ticket_type: str = element(tag="TicketType")

    @field_validator("departure_time_stamp", "arrival_time_stamp", mode="before")
    def datetime_converter(cls, v: str) -> datetime:
        return datetime.strptime(v, r"%Y-%m-%dT%H%M")

    @field_validator("fare_basis", mode="before")
    def fare_basis_stripper(cls, v: str) -> str:
        return v.strip()


class ServiceCharges(BaseXmlModel, tag="ServiceCharges"):
    model_config = ConfigDict(populate_by_name=True)

    type_: str = attr(name="type", alias="type")
    charge_type: str = attr(name="ChargeType")
    service_charges: Decimal

    @field_serializer("service_charges")
    def decimal_to_str(self, service_charges):
        return str(service_charges)


class Pricing(BaseXmlModel, tag="Pricing"):
    currency: str = attr(name="currency")
    service_charges: list[ServiceCharges]


class Flights(BaseXmlModel, tag="Flights"):
    flights: list[Flight]


class OnwardPricedItinerary(BaseXmlModel, tag="OnwardPricedItinerary"):
    onward_priced_itinerary: Flights


class ReturnPricedItinerary(BaseXmlModel, tag="ReturnPricedItinerary"):
    return_priced_itinerary: Flights


class Itinerary(BaseXmlModel, tag="Flights"):
    flights: tuple[OnwardPricedItinerary, ReturnPricedItinerary | None]
    pricing: Pricing


class ListItineraries(BaseXmlModel, tag="PricedItineraries"):
    priced_itineraries: list[Itinerary] | None = Field(default=None)
