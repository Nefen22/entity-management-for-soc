from pydantic import BaseModel, Field
from .edge_parser import EdgePaser, Vertex
from database.constraints import MAPPING_ENTITIES_TYPE, MAPPING_RELATIONSHIPS


def clean(lst):
    if type(lst) is list:
        return [v for v in lst if v]
    return [lst] if lst else []

class BaseParser(BaseModel):
    nodes: list[Vertex] | None = None
    edges: list[dict] | None = None
    source_type: str  | None = None
    evidence: str | None = None
    
    def split_nodes_edges(self, event: dict, include:dict):
        type_n_nodes = {}
        edges = []
        time = event.get("timestamp")
        parser_nodes=include["nodes"]
        parser_edges=include["edges"]
        for k, v_lst in parser_nodes.items():
            for v in v_lst:
                if event.get(v):
                    type_n_nodes[v] = Vertex(type=MAPPING_ENTITIES_TYPE[k], value=event.get(v))
        type_n_nodes = {k:v for k,v in type_n_nodes.items() if v != None}
        for rels in parser_edges:
            try:
                (type_n_nodes[rels[0]].type,type_n_nodes[rels[1]].type)
            except:
                continue
            edges.append({"source": type_n_nodes[rels[0]],
                "target": type_n_nodes[rels[1]],
                "type": MAPPING_RELATIONSHIPS[(type_n_nodes[rels[0]].type,
                                                type_n_nodes[rels[1]].type)],
                "time": time})
        lst_nodes = []
        for k,v in type_n_nodes.items():
            lst_nodes.append(v)
        self.nodes = lst_nodes
        self.edges = edges
        return lst_nodes, edges

    def get_nodes(self):
        return self.nodes

    def get_relationship(self):
        relationships = [EdgePaser(src=edge["source"], dest=edge["target"], connect_type=edge["type"], evidence=self.evidence, time=str(edge["time"])) for edge in self.edges]
        
        return relationships