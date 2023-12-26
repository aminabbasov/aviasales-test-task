from pathlib import Path
from io import BytesIO

import pytest
from fastapi import UploadFile


BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def rsvia3xml():
    with open(BASE_DIR / "src" / "RS_Via-3.xml", "rb") as f:
        content = f.read()
    return ("RS_Via-3.xml", content, "text/xml")


@pytest.fixture
def rsviaowxml():
    with open(BASE_DIR / "src" / "RS_ViaOW.xml", "rb") as f:
        content = f.read()
    return ("RS_ViaOW.xml", content, "text/xml")


@pytest.fixture
def faviconico():
    with open(BASE_DIR / "src" / "favicon.ico", "rb") as f:
        content = f.read()
    return ("favicon.ico", content, "image/x-icon")


@pytest.fixture
def uploadfile():
    def inner(data):
        return UploadFile(filename=data[0], file=BytesIO(data[1]), headers={"content-type": data[2]})

    return inner
