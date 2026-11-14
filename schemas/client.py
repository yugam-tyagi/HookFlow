from typing import Annotated
from pydantic import BaseModel, StringConstraints, ConfigDict
from datetime import datetime

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class ClientCreate(BaseModel):
    name: NonEmptyStr
    model_config = ConfigDict(extra='forbid')

class ClientResponse(BaseModel):
    name: NonEmptyStr
    id: str
    active: bool
    created_at: datetime
    model_config = ConfigDict(extra='forbid')