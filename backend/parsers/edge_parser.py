from pydantic import BaseModel

class Vertex(BaseModel):
    type: str
    key: str
    value: str

class EdgePaser(BaseModel):
    src: Vertex
    dest: Vertex
    connect_type: str
    evidence: str