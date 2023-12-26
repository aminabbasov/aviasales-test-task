from datetime import datetime as _datetime
from typing import Annotated

from pydantic import PlainSerializer


datetime = Annotated[
    _datetime,
    PlainSerializer(lambda dt: dt.strftime(r"%Y-%m-%dT%H%M"), return_type=str),
]
