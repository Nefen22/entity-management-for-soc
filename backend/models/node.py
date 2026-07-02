from pydantic import BaseModel, field_serializer

class Node(BaseModel):
    id: str
    type: str | list
    properties: dict