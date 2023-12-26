import pytest

from src.api.services import ViaComComparator, InvalidValueError


def test_invalid_interaries_flag(rsvia3xml, rsviaowxml, uploadfile):
    with pytest.raises(InvalidValueError):
        ViaComComparator(uploadfile(rsvia3xml), uploadfile(rsviaowxml), itineraries="Я летал меня катали")()
