from pydantic import BaseModel

class Vertex(BaseModel):
    type: str
    value: str | None = None

class EdgePaser(BaseModel):
    src: Vertex
    dest: Vertex
    connect_type: str
    evidence: str