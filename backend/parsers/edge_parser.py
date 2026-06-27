from pydantic import BaseModel
import datetime


class Vertex(BaseModel):
    type: str
    value: str | None = None

class EdgePaser(BaseModel):
    src: Vertex
    dest: Vertex
    connect_type: str
    evidence: str
    time: str