from pydantic import BaseModel
from .edge_parser import EdgePaser, Vertex

class BaseParser(BaseModel):
    user: str | None = None
    ip: str | None = None
    host: str | None = None
    domain: str | None = None
    file_hash: str | None = None
    source_type: str
    evidence: str
    def get_relationship(self):
        relationships = []
        if self.user and self.host:
            relationships.append(EdgePaser(src=Vertex(type="User", key="username", value=self.user),
                                           dest=Vertex(type="Host", key="hostname", value=self.host),
                                           connect_type="LOGGED_IN",
                                           evidence=self.evidence))
        if self.host and self.ip:
            relationships.append(EdgePaser(src=Vertex(type="Host", key="hostname", value=self.host),
                                           dest=Vertex(type="IP", key="value", value=self.ip),
                                           connect_type="CONNECTED_TO",
                                           evidence=self.evidence))
        if self.host and self.domain:
            relationships.append(EdgePaser(src=Vertex(type="Host", key="hostname", value=self.host),
                                           dest=Vertex(type="Domain", key="name", value=self.domain),
                                           connect_type="CONNECTED_TO",
                                           evidence=self.evidence))
        if self.file_hash and self.host:
            relationships.append(EdgePaser(src=Vertex(type="FileHash", key="hash_value", value=self.file_hash),
                                           dest=Vertex(type="Host", key="hostname", value=self.host),
                                           connect_type="EXECUTED_ON",
                                           evidence=self.evidence))
        return relationships
# class EdgePaser(BaseModel):
#     source: str
#     source_type: str
#     dest: str
#     dest_type: str
#     connect_type: str
#     evidence: str