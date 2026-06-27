```mermaid
flowchart TD

A[Security Events] --> B[Parser Layer]
B --> C[Service Layer]
C --> D[Repository Layer]
D --> E[(Neo4j)]

F[FastAPI API] --> C
F --> D

G[Frontend / Cytoscape] --> F
```