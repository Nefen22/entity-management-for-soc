# Entity Management for SOC (v2.0.0)

A high-performance Security Operations Center (SOC) investigation platform designed to ingest security events from multiple log sources, parse and structure them via fallback pipelines (including Large Language Models), and map them into a multi-tenant Entity Graph. 

The platform leverages **Neo4j** for graph relationship traversal, **MongoDB** for persistent document metadata (accounts, raw events, audit logs), and **Redis** for in-memory caching of threat intelligence enrichment.

---

## 🚀 Project Overview

Security analysts face enormous challenges when investigating alerts across disparate systems (SIEM, EDR, Cloud, Alerts). This platform provides a centralized, multi-tenant workspace where security logs are normalized, converted into graph topologies, enriched with external threat intelligence, and explored interactively.

---

## ✨ Features

- **Parser Fallback Pipeline**: Config-driven structured parsing, AI/LLM unstructured parsing, and regex fallback parsing.
- **AI-Powered Event Normalization**: Sanitizes and structures free-text logs into Canonical Events using Gemini 2.5 Flash.
- **Graph Traversal & Pathfinding**: Run multi-hop traversals and shortest path algorithms using Neo4j and Cytoscape.js.
- **Threat Intelligence Enrichment**: Automatic and manual IP (GeoIP, AbuseIPDB) and FileHash (VirusTotal with local Mock fallback) enrichment with a Redis-backed TTL cache.
- **Tenant-Scoped Isolation**: Labels and restricts query execution contexts per tenant.
- **MongoDB Audit Trail**: Full creation/update changelogs with before-and-after state logs.
- **Fine-Grained RBAC**: Role-based access controls validating JWT credentials against database-seeded roles.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[Security Events / Alerts] --> B[Parser Layer]
    B --> C[Service Layer]
    F[FastAPI API] --> C
    C --> D[Repository Layer]
    D --> E[(Neo4j Graph Database)]
    D --> J[(MongoDB Document Database)]
    D --> K[(Redis Cache)]

    G[Frontend / Cytoscape.js] --> F
    H[Auth Layer] --> F
    I[Testing Suite] --> F
```

1. **Frontend**: Cytoscape.js & Vanilla JS rendering dark-mode security topologies.
2. **API Layer**: FastAPI asynchronous endpoints.
3. **Parsers**: `JsonParser`, `LLMParser` (Gemini Flash), and `AlertParser` (regex).
4. **Data Stores**: Neo4j (property graphs), MongoDB (metadata/audit), Redis (caching).

---

## 🛠️ Tech Stack

- **Core**: HTML5, Vanilla CSS, Vanilla JS
- **Framework**: FastAPI (Python 3.12)
- **Graph Visualization**: Cytoscape.js
- **Databases**: Neo4j 5.x, MongoDB 7.x
- **Caching**: Redis 7.x
- **Containerization**: Docker Compose

---

## 📁 Folder Structure

```text
entity-management-for-soc/
├── backend/
│   ├── api/            # API routing submodules (auth, tenants, graph, logs)
│   ├── auth/           # JWT, hashing, and role checks
│   ├── database/       # DB initialization & seeding configs
│   ├── enrichment/     # GeoIP, AbuseIPDB, and VirusTotal providers
│   ├── models/         # Pydantic schemas & DB models
│   ├── parsers/        # Log extraction parsing engine
│   ├── repositories/   # Neo4j and MongoDB drivers
│   ├── services/       # Core business logic orchestrators
│   ├── test/           # Unit & Integration pytest suite
│   └── main.py         # Application entry point
├── frontend/           # Static web assets (HTML, CSS, JS)
├── docs/               # System documentation folder
└── docker-compose.yml  # Multi-container stack configuration
```

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file in the root directory:

```env
# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secret_password123

# MongoDB Configuration
MONGODB_URI=mongodb://root:secret_password123@mongodb:27017/?authSource=admin
MONGODB_DATABASE=soc_db

# Redis Caching
REDIS_HOST=redis
REDIS_PORT=6379

# External API Keys
GEMINI_API_KEY=your_gemini_key_here
ABUSEIPDB_API_KEY=your_abuseipdb_key_here
VIRUSTOTAL_API_KEY=your_vt_key_here

# System Flags
RESET_DB=true
INIT_DB=true
SEED_NAME=DEFAULT
JWT_SECRET_KEY=generate_a_random_jwt_key_here
```

---

## 🐳 Running with Docker Compose

To build and run all services:

```bash
docker compose up --build -d
```

### Services Mapping

- **Frontend Application**: [http://localhost](http://localhost)
- **FastAPI API & Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)
- **Mongo Express**: [http://localhost:8081](http://localhost:8081)

---

## 🔑 Default Accounts

Seeded during startup:

- **Admin Account**:
  - Username: `admin` / Password: `admin123`
  - Permissions: `graph:view`, `graph:ingest`, `graph:enrichment`
- **Analyst Account**:
  - Username: `user` / Password: `user123`
  - Permissions: `graph:view`, `graph:enrichment`

---

## ⚡ Demo Workflow

1. Open the UI at [http://localhost/login.html](http://localhost/login.html).
2. Authenticate as `admin`.
3. Select tenant `acme` or `google` in the header dropdown.
4. Go to **Entities** to check existing nodes.
5. In **Graph Explorer**, view relationships and double-click nodes to fetch n-hops.
6. Run GeoIP and VirusTotal enrichment on entities.
7. Paste an unstructured log in **Ingest** to test LLM parsing fallback.
8. Go to **Audit Logs** to view audit diffs.

---

## 📡 REST APIs

### Authentication
- `POST /api/auth/login`: Issue bearer access token.
- `GET /api/auth/me`: Resolve current identity permissions.

### Tenant Scoped Graph & Logs
- `POST /api/tenants/{tenant}/graphs/ingest`: Ingest structured log JSON.
- `POST /api/tenants/{tenant}/graphs/ingest/batch`: Ingest array list of log JSONs.
- `GET /api/tenants/{tenant}/entities`: Search, filter, and paginate nodes.
- `POST /api/tenants/{tenant}/entities/{entity_type}/values/{entity_value}/enrich`: Enrich node details.
- `GET /api/tenants/{tenant}/logs/audit`: Retrieve paginated Audit Log history.

---

## 🩺 Health Check Endpoints

- `GET /health`: Liveness ping (`status: healthy`).
- `GET /health/live`: Service status check (`status: alive`).
- `GET /health/ready`: Checks connections to MongoDB, Neo4j, and Redis.

---

## 🛡️ Multi-Tenant Support
Multi-tenancy is enforced on two levels:
1. **API Middleware**: Validates if the user's JWT token contains authorization for `{tenant}` before route execution.
2. **Database Schema**: Neo4j entities are labeled `Tenant_{tenant}`. Cypher queries are automatically bound to this prefix scope.

---

## 📝 Entity & Relationship Schema

### Entity Types
- `User`, `Host`, `IP`, `Domain`, `URL`, `FileHash`, `Process`, `Email`, `CloudResource`, `CVE`

### Edge Fields
- `first_seen`, `last_seen`, `count`, `evidence` (MongoDB event ID reference)

---

## 🧠 LLM Parser Variable Substitution

The LLM Parser (using Google Gemini 2.5 Flash) uses placeholder encoding for security IOC values:
1. Extracts IPs, domains, and hashes via regex.
2. Substitutes values with placeholders (`<ips_0>`, etc.) before calling the model.
3. Transmits clean log structures to the LLM to structure them.
4. Restores values into the final structured schema returned to the ingest pipeline.

---

## 🕵️ Audit Logs

Modifications trigger MongoDB updates recorded in `audit_logs` collections, containing before/after diff states:

```json
{
  "tenant": "acme",
  "timestamp": "2026-07-11 18:42:00.123456",
  "action": "UPDATE",
  "entity_type": "IP",
  "entity_id": "104.21.43.11",
  "change": {
    "before": "{\"country\": null}",
    "after": "{\"country\": \"US\", \"abuse_score\": 0, \"asn\": 13335}"
  }
}
```

---

## 🧪 Testing

The pytest suite includes 129 tests passing inside docker.

### Run tests in Docker:
```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

---

## 🔮 Future Work

- Apache Kafka ingestion pipelines.
- PDF Investigation report exports.
- Local model running configurations (e.g. Ollama).

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.