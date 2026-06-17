from pydantic import BaseModel

class APIResponse(BaseModel):
    message: str
    data: dict | list | None = None