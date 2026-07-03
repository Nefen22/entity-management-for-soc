```mermaid
flowchart TD

A[Security Events] --> B[Parser Layer]
B --> C[Service Layer]
F[FastAPI API] --> C
C --> D[Repository Layer]
D --> E[(Neo4j)]

G[Frontend / Cytoscape] --> F
```