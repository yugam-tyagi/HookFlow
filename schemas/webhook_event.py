from pydantic import BaseModel, ConfigDict, StringConstraints
from datetime import datetime
from typing import Annotated, Any

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class WebhookEventPayload(BaseModel):
    id: NonEmptyStr
    type: NonEmptyStr
    created_at: datetime
    data: dict[str,Any]
    model_config = ConfigDict(extra='forbid')