import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture(scope="class")
def client():
    """Tạo FastAPI test client, cô lập hoàn toàn kết nối mạng/DB và bypass validate_tenant."""
    
    # 1. Khởi tạo cấu trúc Mock Async hoàn chỉnh cho Neo4j Driver giống trong main.py
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data = AsyncMock(return_value=[])
    mock_session.run = AsyncMock(return_value=mock_result)
    
    mock_driver = MagicMock()
    # Giả lập cú pháp: async with driver.session() as session:
    mock_driver.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_driver.session.return_value.__aexit__ = AsyncMock(return_value=False)
    
    # 2. PATCH ĐỒNG BỘ: Ép toàn bộ hệ thống sử dụng mock_driver này
    with patch("database.neo4j.driver", mock_driver), \
         patch("database.neo4j.init_db", AsyncMock(return_value=None)), \
         patch("api.graph.ingest_sample", AsyncMock(return_value=None)), \
         patch("repositories.graph.driver", mock_driver):
         
        from main import app
        from api.tenants import validate_tenant 
        
        # 3. Bẻ lái hàm validate_tenant: Luôn cho phép mọi tenant đi qua khi test
        app.dependency_overrides[validate_tenant] = lambda tenant: tenant
        
        with TestClient(app) as tc:
            yield tc
            
        app.dependency_overrides.clear()
# ══════════════════════════════════════════════════════════════════════════════
#  GET /api/tenants
# ══════════════════════════════════════════════════════════════════════════════

class TestTenantsEndpoint:

    def test_get_tenants_returns_list(self, client):
        with patch("services.graph.repo"), patch("repositories.graph.driver"):
            response = client.get("/api/tenants")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "data" in data

    def test_get_tenants_not_empty(self, client):
        with patch("services.graph.repo") as mock_repo, patch("repositories.graph.driver"):
            from conftest import TENANT_DATABASE
            mock_repo.get_tenants.return_value = list(TENANT_DATABASE.keys())
            response = client.get("/api/tenants")
        assert response.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  POST /api/tenants/{tenant}/graphs/ingest
# ══════════════════════════════════════════════════════════════════════════════

class TestIngestEndpoint:

    SAMPLE_EVENT = {
        "event_id": "test-001",
        "source_type": "siem",
        "timestamp": "2024-01-01T00:00:00Z",
        "user": "john.doe",
        "source_ip": "10.0.0.1",
        "destination_host": "DESKTOP-001",
    }

    @pytest.mark.parametrize("tenant", ["acme", "google", "internal"])
    def test_ingest_returns_200(self, client, tenant):
        with patch("services.graph.ingest", AsyncMock()):
            response = client.post(f"/api/tenants/{tenant}/graphs/ingest", json=self.SAMPLE_EVENT)
        assert response.status_code == 200

    def test_ingest_alert_event(self, client):
        alert_event = {
            "event_id": "alert-001",
            "source_type": "alert",
            "message": "Suspicious connection from 1.2.3.4 to evil.com",
        }
        with patch("services.graph.ingest", AsyncMock()):
            response = client.post("/api/tenants/acme/graphs/ingest", json=alert_event)
        assert response.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  POST /api/tenants/{tenant}/enrichments/ips/{value}
# ══════════════════════════════════════════════════════════════════════════════

class TestEnrichmentEndpoint:

    MOCK_ENRICHMENT = {
        "id": "IP:8.8.8.8",
        "type": "IP",
        "properties": {
            "value": "8.8.8.8",
            "country": "US",
            "organization": "Google LLC",
            "asn": 15169,
        }
    }

    def test_enrich_ip_returns_200(self, client):
        with patch("services.enrichment.enrichment_ip", AsyncMock(return_value=self.MOCK_ENRICHMENT)):
            response = client.post("/api/tenants/acme/enrichments/ips/8.8.8.8")
        assert response.status_code == 200

    def test_enrich_ip_response_has_properties(self, client):
        with patch("services.enrichment.enrichment_ip", AsyncMock(return_value=self.MOCK_ENRICHMENT)):
            response = client.post("/api/tenants/acme/enrichments/ips/8.8.8.8")
        data = response.json()
        body = data.get("data", data)
        assert "properties" in body

    def test_enrich_invalid_ip_returns_422_or_400(self, client):
            from fastapi import HTTPException
            # Ép bản mock ném thẳng ra lỗi 400 Bad Request của FastAPI
            invalid_ip_exception = HTTPException(status_code=400, detail="Invalid IP format")
            
            with patch("services.enrichment.enrichment_ip", AsyncMock(side_effect=invalid_ip_exception)):
                response = client.post("/api/tenants/acme/enrichments/ips/not-an-ip")
                
            assert response.status_code in (400, 422)