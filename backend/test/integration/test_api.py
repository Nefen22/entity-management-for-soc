from database.constraints import TENANT_DATABASE

TENANT = 'phishing'

def test_root(api):
    r = api.get("/")
    assert r.status_code == 200

def test_get_tenants(api):
    r = api.get("/api/tenants")
    assert r.status_code == 200
    assert TENANT in r.json()["data"]

def test_get_all_entities(api):
    r = api.get(f"/api/tenants/{TENANT}/entities/lists")

    assert r.status_code == 200

    data = r.json()["data"]
    # Có User
    assert any(e["type"] == "User" and e["id"] == "hr.manager" for e in data)

    # Có Host
    assert any(e["type"] == "Host" and e["id"] == "DESKTOP-HR01" for e in data)

    # Có Domain
    assert any(e["type"] == "Domain" and e["id"] == "filetransfer.io" for e in data)


def test_get_label(api):
    r = api.get(f"/api/tenants/{TENANT}/entities/lists?type=User")

    assert r.status_code == 200

    users = r.json()["data"]

    ids = {u["id"] for u in users}

    assert "hr.manager" in ids
    assert "administrator" in ids

def test_get_entity(api):
    r = api.get(
        f"/api/tenants/{TENANT}/entities/types/User/values/hr.manager"
    )

    assert r.status_code == 200

    entity = r.json()["data"]

    assert entity["id"] == "hr.manager"
    assert entity["type"] == "User"

def test_graph_one_hop(api):
    r = api.get(
        f"/api/tenants/{TENANT}/graphs/entities/types/User/values/hr.manager?hop=1"
    )

    assert r.status_code == 200

    graph = r.json()["data"]

    assert len(graph["nodes"]) > 1
    assert len(graph["edges"]) > 0

def test_graph_two_hop(api):
    r = api.get(
        f"/api/tenants/{TENANT}/graphs/entities/types/User/values/hr.manager?hop=2"
    )

    assert r.status_code == 200

    graph = r.json()["data"]

    ids = {n["id"] for n in graph["nodes"]}

    assert "powershell.exe" in ids
    assert "cmd.exe" in ids
    assert "198.51.100.23" in ids

def test_get_types(api):
    r = api.get(f"/api/tenants/{TENANT}/graphs/get-types")

    assert r.status_code == 200

    types = r.json()["data"]

    assert "User" in types
    assert "Host" in types
    assert "IP" in types
    assert "Domain" in types


def test_filter_relationship(api):
    r = api.get(
        f"/api/tenants/{TENANT}/graphs/filter-relationships?label=Host"
    )
    assert r.status_code == 200

    rels = r.json()["data"]
    assert len(rels) > 0


def test_clusters(api):
    r = api.get(f"/api/tenants/{TENANT}/graphs/clusters")

    assert r.status_code == 200

    clusters = r.json()["data"]

    assert len(clusters["nodes"]) > 0
    assert len(clusters["edges"]) > 0


def test_cluster_entities(api):
    r = api.get(
        f"/api/tenants/{TENANT}/graphs/clusters/types/User"
    )

    assert r.status_code == 200

    data = r.json()["data"]
    ids = {e["id"] for e in data}

    assert "hr.manager" in ids

def test_ip_enrichment(api):
    r = api.post(
        f"/api/tenants/{TENANT}/enrichments/types/ips/values/104.21.43.11"
    )

    assert r.status_code == 200

    data = r.json()["data"]["properties"]

    assert "asn" in data
    
def test_hash_enrichment(api):
    r = api.post(
        f"/api/tenants/{TENANT}/enrichments/types/file-hashes/values/e99a18c428cb38d5f260853678922e03"
    )

    assert r.status_code == 200

    data = r.json()["data"]

    assert isinstance(data, dict)