from collections import deque
from collections.abc import Generator
from dataclasses import dataclass
from itertools import islice
from typing import Literal, TypeAlias, TypedDict
from uuid import uuid4

from fastapi import UploadFile

from api.processors import ViaComDiffProcessor, ViaComParser
from core.services import BaseService


class InvalidValueError(ValueError):
    pass


class FileDiff(TypedDict):  # PEP 589
    roundtrip: bool
    ticket_types: set[str]
    routes: set[tuple[str, ...]]


filename: TypeAlias = dict[str, FileDiff]  # noqa: UP040


@dataclass(init=False)
class ViaComComparator(BaseService):
    files: tuple[UploadFile, ...]
    itineraries: Literal["all", "diff"] = "diff"

    def __init__(self, *files: UploadFile, itineraries: Literal["all", "diff"] = "diff") -> None:
        self.files: tuple[UploadFile, ...] = files
        self.parsers: tuple[ViaComParser, ...] = tuple(ViaComParser(file) for file in files)
        self.processors: tuple[ViaComDiffProcessor, ...] = tuple(ViaComDiffProcessor(parser) for parser in self.parsers)
        self.itineraries = itineraries

    def act(self) -> dict[str, filename]:
        match self.itineraries:
            case "all":
                return self.show_all()
            case "diff":
                return self.show_diff()
            case _:
                raise InvalidValueError("Invalid value for 'itineraries': %s." % self.itineraries)

    def show_all(self) -> dict[str, filename]:
        response: filename = dict()

        for index, processor in enumerate(self.processors):
            diff: FileDiff = {
                "roundtrip": processor.is_roundtrip(),
                "ticket_types": processor.ticket_types(),
                "routes": processor.unique_itineraries(self.return_itineraries),
            }
            response[self.files[index].filename or str(uuid4())] = diff

        return {"files": response}

    def show_diff(self) -> dict[str, filename]:
        response: filename = dict()

        for index, (processor, itinerary) in enumerate(zip(self.processors, self._get_diff_itineraries(), strict=True)):
            diff: FileDiff = {
                "roundtrip": processor.is_roundtrip(),
                "ticket_types": processor.ticket_types(),
                "routes": itinerary,
            }
            response[self.files[index].filename or str(uuid4())] = diff

        return {"files": response}

    def _get_diff_itineraries(self) -> Generator[set[tuple[str, ...]], None, None]:
        itineraries = deque([processor.unique_itineraries(self.return_itineraries) for processor in self.processors])
        for _ in range(len(itineraries)):
            yield itineraries[0].difference(*list(islice(itineraries, 1, None)))
            itineraries.rotate(-1)

    @property
    def return_itineraries(self) -> bool:
        return all(processor.is_roundtrip() is not False for processor in self.processors)
