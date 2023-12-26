from fnmatch import fnmatch
from typing import Literal

import lxml.etree as ET
from fastapi import APIRouter, HTTPException, UploadFile

from api.processors import ViaComDataProcessor, ViaComParser
from api.services import ViaComComparator
from core.schemas.differences import ListItinerariesDiff
from core.schemas.itineraries import ListItineraries


router = APIRouter()


async def xml_file_validator(xml_file):
    if not fnmatch(xml_file.filename, "*.xml"):
        raise HTTPException(status_code=400, detail="Only XML files are allowed.")


async def get_pydantic_model_from_xml(answer: ET._Element | list[ET._Element]) -> ListItineraries:
    response = ListItineraries().to_xml_tree()

    if isinstance(answer, list):
        for itinerary in answer:
            response.append(itinerary)  # type: ignore
    else:
        response.append(answer)  # type: ignore

    response = ListItineraries.from_xml(ET.tostring(response))  # type: ignore
    return response  # type: ignore


@router.post("/itineraries/all")
async def all_itineraries(xml_file: UploadFile) -> ListItineraries:
    await xml_file_validator(xml_file)
    print(xml_file.content_type)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).all_itineraries()
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/specified")
async def specified_itineraries(
    xml_file: UploadFile, source: str, destination: str, direct: bool = False, transit: bool = False
) -> ListItineraries:
    await xml_file_validator(xml_file)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).specified_itineraries(
        source, destination, direct=direct, transit=transit
    )
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/optimal")
async def optimal_itinerary(xml_file: UploadFile) -> ListItineraries:
    await xml_file_validator(xml_file)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).optimal_itinerary()
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/most_expensive")
async def most_expensive_itinerary(xml_file: UploadFile) -> ListItineraries:
    await xml_file_validator(xml_file)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).most_expensive_itinerary()
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/cheapest")
async def cheapest_itinerary(xml_file: UploadFile) -> ListItineraries:
    await xml_file_validator(xml_file)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).cheapest_itinerary()
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/longest")
async def longest_itinerary(xml_file: UploadFile) -> ListItineraries:
    await xml_file_validator(xml_file)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).longest_itinerary()
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/shortest")
async def shortest_itinerary(xml_file: UploadFile) -> ListItineraries:
    await xml_file_validator(xml_file)
    parser = ViaComParser(xml_file)
    answer = ViaComDataProcessor(parser=parser).shortest_itinerary()
    response = await get_pydantic_model_from_xml(answer)
    return response


@router.post("/itineraries/difference")
async def itineraries_difference(
    first_xml_file: UploadFile, second_xml_file: UploadFile, itineraries: Literal["all", "diff"] = "diff"
):
    await xml_file_validator(first_xml_file)
    await xml_file_validator(second_xml_file)
    compared = ViaComComparator(first_xml_file, second_xml_file, itineraries=itineraries)()
    response = ListItinerariesDiff().model_validate(compared)
    return response
