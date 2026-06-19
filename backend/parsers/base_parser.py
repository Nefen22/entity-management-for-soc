from pydantic import BaseModel, Field
from .edge_parser import EdgePaser, Vertex

def clean(lst):
    if type(lst) is list:
        return [v for v in lst if v]
    return [lst] if lst else []

class BaseParser(BaseModel):
    user: list[str] = Field(default_factory=list)
    ip: list[str] = Field(default_factory=list)
    host: list[str] = Field(default_factory=list)
    domain:list[str] = Field(default_factory=list)
    file_hash: list[str] = Field(default_factory=list)
    source_type: str  
    evidence: str
    
    def get_nodes(self):
        return {
            "users": self.user,
            "ips": self.ip,
            "hosts": self.host,
            "domains": self.domain,
            "file_hashes": self.file_hash
        } 

    def get_relationship(self):
        relationships = []
        for user in self.user:
            for host in self.host:
                relationships.append(EdgePaser(src=Vertex(type="User", key="username", value=user),
                                            dest=Vertex(type="Host", key="hostname", value=host),
                                            connect_type="LOGGED_IN",
                                            evidence=self.evidence))
        for host in self.host:
            for ip in self.ip:
                relationships.append(EdgePaser(src=Vertex(type="Host", key="hostname", value=host),
                                            dest=Vertex(type="IP", key="value", value=ip),
                                            connect_type="CONNECTED_TO",
                                            evidence=self.evidence))
        for host in self.host:
            for domain in self.domain:
                relationships.append(EdgePaser(src=Vertex(type="Host", key="hostname", value=host),
                                            dest=Vertex(type="Domain", key="name", value=domain),
                                            connect_type="CONNECTED_TO",
                                            evidence=self.evidence))
        for file_hash in self.file_hash:
            for host in self.host:
                relationships.append(EdgePaser(src=Vertex(type="FileHash", key="hash_value", value=file_hash),
                                            dest=Vertex(type="Host", key="hostname", value=host),
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