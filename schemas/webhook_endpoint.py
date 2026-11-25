from pydantic import BaseModel, HttpUrl, ConfigDict, StringConstraints
from datetime import datetime
from typing import Annotated

EventName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class WebhookEndpointCreate(BaseModel):
    url: HttpUrl
    subscribed_events: list[EventName] = []
    model_config = ConfigDict(extra="forbid")

class WebhookEndpointResponse(BaseModel):
    id: str
    url: HttpUrl
    subscribed_events: list[EventName] = []
    active: bool
    created_at: datetime
    signing_secret: str | None = None
    model_config = ConfigDict(extra="forbid")