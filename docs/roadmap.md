# Project Roadmap

This document chronicles completed milestones and future enhancements planned for the Entity Management for SOC platform.

---

## 1. Version 1.0.0 (Core Entity Graph Platform)
- [x] **Entity Extraction**: Support for 10 basic entity types (IP, Host, User, URL, FileHash, Domain, CVE, Email, Process, CloudResource).
- [x] **Neo4j Graph Database Integration**: Graph indexing and query traversals.
- [x] **Cytoscape Visualizer**: Basic frontend rendering of security topologies.
- [x] **Enrichment Mocking**: Basic lookup mechanics for GeoIP.
- [x] **Config-driven JSON Parsing**: Core parsing schemas.

---

## 2. Version 2.0.0 (Production Features & Integration)
- [x] **MongoDB Persistence**: Storing raw event logs and system audit trails inside document collections rather than transient JSONL files.
- [x] **Role-Based Access Control (RBAC)**: Fine-grained permissions (`graph:ingest`, `graph:view`, `graph:enrichment`) verified at the API routing layer.
- [x] **Multi-Tenant Isolation**: Scoped querying using Neo4j database labels (`Tenant_{tenant}`) combined with JWT user permission validations.
- [x] **Redis Caching Layer**: Decreasing third-party API lookups by storing enrichment payloads for 1 hour.
- [x] **LLM Parser Variable Substitution**: Regex replacement of real values with variables (`<ips_0>`) before API ingestion to minimize token usage and enhance privacy.
- [x] **Dynamic Readiness Probes**: Dynamic readiness health check `/health/ready` verifying connection states of Neo4j, MongoDB, and Redis.
- [x] **Robust Integration Suite**: Pytest framework testing all routing wrappers under a mocked database docker workspace.
- [x] **Threat Intel Alerts**: Integration of automatic maliciousness flags and threat classification tags based on AbuseIPDB scores and VirusTotal malware families.

---

## 3. Future Roadmap

### Ingestion & Scaling
- [ ] **Apache Kafka / RabbitMQ Streams**: Real-time event ingestion directly from messaging buses.
- [ ] **Log Parsing Expansion**: Native parsing modules for Windows Event Log (EVTX), Linux Syslog, Sysmon, and Zeek.

### AI & Threat Intelligence
- [ ] **Retrieval-Augmented Generation (RAG)**: Connect the LLM Parser with local vulnerability databases (NVD) to contextualize entity warnings.
- [ ] **Graph Neural Networks (GNN)**: Build automated lateral movement identification and malicious path traversal scoring.

### Operations & DevOps
- [ ] **Kubernetes Deployment**: Helm charts for deployment orchestration.
- [ ] **Prometheus & Grafana**: Service metrics monitoring and visualization.
