### 1. Core graph relationships

```mermaid
graph LR
User -->|LOGGED_IN| Host
Host -->|CONNECTED_TO| IP
Host -->|REQUESTED| URL
URL -->|BELONGS_TO| Domain
Domain -->|RESOLVES_TO| IP
```

---

### 2. Execution and malware context

```mermaid
graph LR
Process -->|RUNS_ON| Host
Process -->|LOADED| FileHash
FileHash -->|EXECUTED_ON| Host
URL -->|DOWNLOADS| FileHash
```

---

### 3. Threat intelligence context

```mermaid
graph LR
CVE -->|AFFECTS| Host
CVE -->|AFFECTS| Process
Domain -->|HOSTS| URL
URL -->|EXPLOITS| CVE
```

---

### 4. Metadata stores

The implementation uses two metadata stores in addition to Neo4j:

- MongoDB `users` collection for authentication accounts
- MongoDB `roles` collection for role-to-permission mappings
- MongoDB `events` collection for raw event payloads
- MongoDB `audit_logs` collection for audit trail entries

Each audit log entry stores the tenant, timestamp, action, entity type, entity id, and change payload. Evidence references the original event via `event_id`, and the raw event is retrieved from MongoDB when needed.
