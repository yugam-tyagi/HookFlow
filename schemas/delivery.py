from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DeliveryTrackingResponse(BaseModel):
    delivery_id: str
    endpoint_id: str
    status: str
    attempt_count: int
    http_status: int | None = None
    response_body: str | None = None
    error_message: str | None = None
    next_attempt_at: datetime | None = None
    completed_at: datetime | None = None
    model_config = ConfigDict(extra='forbid')