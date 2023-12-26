from typing import TypeAlias

from pydantic import BaseModel


filename: TypeAlias = str  # noqa: UP040


class Diff(BaseModel):
    roundtrip: bool | None = None
    ticket_types: list[str] | None = None
    routes: list[list[str]] | None = None


class ListItinerariesDiff(BaseModel):
    files: dict[filename, Diff] | None = None
