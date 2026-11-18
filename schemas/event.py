from typing import Annotated, Any
from pydantic import BaseModel, StringConstraints, ConfigDict
from datetime import datetime

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class EventCreate(BaseModel):
    event_type: NonEmptyStr
    payload: dict[str,Any]
    model_config = ConfigDict(extra='forbid')

class EventResponse(BaseModel):
    id: str
    event_type: str
    created_at: datetime
    model_config = ConfigDict(extra='forbid')