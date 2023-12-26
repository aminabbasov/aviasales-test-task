from src.api.processors import ViaComDiffProcessor, ViaComParser


def test_unique_itineraries_with_return_itineraries(rsvia3xml, uploadfile):
    parser = ViaComParser(uploadfile(rsvia3xml))
    processor = ViaComDiffProcessor(parser)
    response = processor.unique_itineraries(return_itineraries=True)
    assert isinstance(response, set)
