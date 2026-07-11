# Interactive Demo Guide

This guide describes how to run and demonstrate the core features of the Entity Management for SOC platform.

---

## 1. Startup & Services Configuration

To spin up the environment, run:

```bash
docker compose up --build
```

### Services Map

| Service Name | Default Port | Storage Type / Responsibility |
| --- | --- | --- |
| **`api`** | `8000` | FastAPI Backend API containing ingestion workflows. |
| **`frontend`** | `80` | Nginx web server displaying HTML/JS/Cytoscape.js. |
| **`neo4j`** | `7474` (HTTP) / `7687` (Bolt) | Property Graph Database storing entities and relationships. |
| **`mongodb`** | `27017` | Document Database storing accounts, events, and audit logs. |
| **`redis`** | `6379` | In-memory cache for IP and FileHash enrichment TTLs. |
| **`mongo-express`** | `8081` | Web admin GUI interface for inspecting MongoDB. |

---

## 2. Authentication & Demo Accounts

The system seeds default roles and user accounts during MongoDB startup.

| Username | Password | Role | Permissions |
| --- | --- | --- | --- |
| **`admin`** | `admin123` | Administrator | `graph:view`, `graph:ingest`, `graph:enrichment` |
| **`user`** | `user123` | Analyst | `graph:view`, `graph:enrichment` |

- **Administrator**: Full read/write access. Can ingest new logs, traverse graphs, trigger enrichments, and view audit trails.
- **Analyst**: Read-only graph traversal and enrichment triggers. Cannot upload or ingest raw events (the ingestion UI is hidden and backend APIs block ingestion).

---

## 3. Demo Datasets & Tenants

During startup, the system configures tenant label maps:
- **Tenants available**: `google`, `acme`, `internal`.
- **Sample files**: The backend maps seed files:
  - `google` -> `datasets/sample_google.json`
  - `acme` -> `datasets/sample_acme.json`
  - `internal` -> `datasets/sample_internal.json`

### Ingestion Workflows
- **Auto-Ingest (Seed)**: When the environment variable `INIT_DB=true` is set, the system automatically imports seed data for the configured tenants.
- **Manual Ingest**: Ingest single security events or batch payloads via the UI / Ingest tab (admin role required) or directly through REST APIs.

---

## 4. Suggested 13-Step Live Demo Scenario

Follow this walkthrough to demonstrate all functionalities of the platform:

1. **Access Login Page**: Open `http://localhost/login.html` (or `http://localhost` if redirected) and observe the sleek dark UI.
2. **Authenticate as Admin**: Login using `admin` / `admin123`.
3. **Select Tenant**: Use the dropdown header selector to load tenant `acme`'s graph data.
4. **Inspect Entity List**: Navigate to the **Entities** tab to view the list of extracted nodes. Observe columns for type, value, and tenant tags.
5. **Filter Entities**: Filter for `IP` type to isolate local and external IP addresses.
6. **Open Entity Detail**: Click on an IP (e.g. `192.168.1.1` or `104.21.43.11`) to inspect its metadata and edge count statistics.
7. **View Graph Visualization**: Click **Explore Graph** (or go to the **Graph Explorer** tab) to render Cytoscape.js. Drag nodes, double click to expand edges, and change hops parameters.
8. **Demonstrate Enrichment**: On the entity page for an external IP, click **Enrich**. View loaded GeoIP details (country, organization) and AbuseIPDB score. Click it again to show it loads instantly from **Redis Cache**.
9. **Show Evidence Links**: Select a relationship edge in the graph or entity view to inspect its `evidence` event ID (ULID format).
10. **View Raw Event**: Navigate to the raw event search box, enter the evidence ULID, and inspect the original unstructured/structured JSON payload fetched from MongoDB.
11. **Check Audit Logs**: Navigate to the **Audit Logs** tab. Observe the tabular changes listing `CREATE` and `UPDATE` events containing before/after property diffs.
12. **Demonstrate LLM Parsing fallback**: Go to the **Ingest** tab. Paste an unstructured log message (e.g. `"Warning: outbound connection to malicious domain google-update.com from host APP-SERVER"`). Submit it, then check the graph to verify that `google-update.com` and `APP-SERVER` were extracted using Gemini 2.5 Flash.
13. **Verify Health Endpoints**: In another browser tab, open `http://localhost:8000/health/ready` to verify database status codes (`neo4j: ok`, `mongodb: ok`, `redis: ok`).
