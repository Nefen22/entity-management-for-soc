from pydantic import BaseModel, Field
from .edge_parser import EdgePaser, Vertex

def clean(lst):
    if type(lst) is list:
        return [v for v in lst if v]
    return [lst] if lst else []

class BaseParser(BaseModel):
    nodes: list[Vertex]
    edges: list[dict]
    source_type: str  
    evidence: str
    
    def get_nodes(self):
        return self.nodes

    def get_relationship(self):
        # edges = {
        #     "source":
        #     "target":
        #     "type" :
        # }
        relationships = [EdgePaser(src=edge["source"], dest=edge["target"], connect_type=edge["type"], evidence=self.evidence) for edge in self.edges]
        
        return relationships