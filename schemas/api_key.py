from pydantic import BaseModel, ConfigDict

class ApiKeyResponse(BaseModel):
    api_key: str
    model_config = ConfigDict(extra='forbid')