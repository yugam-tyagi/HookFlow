from typing import Annotated
from pydantic import BaseModel, StringConstraints, ConfigDict

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class ClientCreate(BaseModel):
    name: NonEmptyStr
    model_config = ConfigDict(extra='forbid')