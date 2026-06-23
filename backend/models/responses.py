from pydantic import BaseModel, field_serializer
from datetime import datetime

class APIResponse(BaseModel):
    message: str
    data: dict | list | None = None
