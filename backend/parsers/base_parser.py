from pydantic import BaseModel, Field
from .edge_parser import EdgePaser, Vertex
from backend.database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_RELATIONSHIPS


def clean(lst):
    if type(lst) is list:
        return [v for v in lst if v]
    return [lst] if lst else []

class BaseParser(BaseModel):
    nodes: list[Vertex]
    edges: list[dict]
    source_type: str  
    evidence: str
    
    def split_nodes_edges(self, event: dict, include:dict):
        nodes = []
        for k, v_lst in include.items():
            nodes+= list(map(lambda v: Vertex(type=MAPPING_ENTITIES_TYPE[k], value=event.get(v) if event.get(v) else None), v_lst))
        nodes=[node for node in nodes if node.value != None]
        edges = [{"source": s_node,
                   "target": t_node,
                   "type": MAPPING_RELATIONSHIPS[s_node.type][t_node.type] if s_node.type in MAPPING_RELATIONSHIPS.keys() and t_node.type in MAPPING_RELATIONSHIPS[s_node.type].keys() else ""}
                   for s_node in nodes for t_node in nodes]
        edges=[edge for edge in edges if edge["type"] != ""]
        return nodes, edges

    def get_nodes(self):
        return self.nodes

    def get_relationship(self):
        relationships = [EdgePaser(src=edge["source"], dest=edge["target"], connect_type=edge["type"], evidence=self.evidence) for edge in self.edges]
        
        return relationships