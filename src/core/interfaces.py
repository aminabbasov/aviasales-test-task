from abc import ABCMeta, abstractmethod
from typing import Any, BinaryIO

import lxml.etree as ET
from fastapi import UploadFile


class XMLParser(metaclass=ABCMeta):
    def __init__(self, xml_file: UploadFile) -> None:
        self.XML: Any = self.parse(xml_file.file)

    @abstractmethod
    def parse(self, xml: BinaryIO) -> ET._Element:
        ...


class XMLDataProcessor(metaclass=ABCMeta):
    def __init__(self, parser: XMLParser) -> None:
        self.parser: XMLParser = parser

    @abstractmethod
    def all_itineraries(self) -> list[ET._Element]:
        ...

    @abstractmethod
    def specified_itineraries(
        self, source: str, destination: str, *, direct: bool = False, transit: bool = False
    ) -> list[ET._Element]:
        ...

    @abstractmethod
    def optimal_itinerary(self) -> ET._Element | list[ET._Element]:
        ...

    @abstractmethod
    def most_expensive_itinerary(self) -> ET._Element | list[ET._Element]:
        ...

    @abstractmethod
    def cheapest_itinerary(self) -> ET._Element | list[ET._Element]:
        ...

    @abstractmethod
    def longest_itinerary(self) -> ET._Element | list[ET._Element]:
        ...

    @abstractmethod
    def shortest_itinerary(self) -> ET._Element | list[ET._Element]:
        ...


class XMLDiffProcessor(metaclass=ABCMeta):
    def __init__(self, parser: XMLParser) -> None:
        self.parser: XMLParser = parser

    @abstractmethod
    def is_roundtrip(self) -> bool:
        ...

    @abstractmethod
    def unique_itineraries(self, return_itineraries: bool) -> set[tuple[str, ...]]:
        ...

    @abstractmethod
    def ticket_types(self) -> set[str]:
        ...
