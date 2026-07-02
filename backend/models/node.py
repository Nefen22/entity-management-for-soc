from pydantic import BaseModel, field_serializer

class Node(BaseModel):
    id: str
    label: str | list
    properties: dict