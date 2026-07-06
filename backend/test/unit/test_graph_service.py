
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mocks import constraints
from database.constraints import TENANT_DATABASE

class TestClusters:

    @pytest.mark.asyncio
    async def test_clusters_formats_nodes_correctly(self):
        fake_repo_result = {
            "nodes": [
                {"label": ["acme", "IP"], "count": 12},
                {"label": ["acme", "Host"], "count": 8},
            ],
            "edges": []
        }

        with patch(
            "services.graph.repo.clusters",
            AsyncMock(return_value=fake_repo_result)
            
        ),patch("services.graph.TENANT_DATABASE", constraints.TENANT_DATABASE):
            from services.graph import clusters
            result = await clusters("acme")

        assert len(result["nodes"]) == 2
        assert result["nodes"][0]["entity_type"] == "IP"

    @pytest.mark.asyncio
    async def test_clusters_formats_edges_correctly(self):
        fake_repo_result = {
            "nodes": [
                {"label": ["acme", "Host"], "count": 3},
                {"label": ["acme", "IP"],   "count": 5},
            ],
            "edges": [
                {"source_label": ["acme", "Host"], "target_label": ["acme", "IP"],
                 "rel_type": "CONNECTED_TO", "count": 7}
            ]
        }

        with patch("services.graph.repo") as mock_repo, \
             patch("services.graph.TENANT_DATABASE", constraints.TENANT_DATABASE):
            mock_repo.clusters = AsyncMock(return_value=fake_repo_result)
            from services.graph import clusters
            result = await clusters("acme")

        assert len(result["edges"]) == 1
        edge = result["edges"][0]
        assert edge["source"] == "Host"
        assert edge["target"] == "IP"
        assert edge["type"] == "CONNECTED_TO"
        assert edge["count"] == 7


# ══════════════════════════════════════════════════════════════════════════════
#  entities_types_in_cluster()
# ══════════════════════════════════════════════════════════════════════════════

class TestEntitiesInCluster:

    @pytest.mark.asyncio
    async def test_returns_entity_list_with_id(self):
        fake_records = [
            {"node": {"value": "8.8.8.8"}, "label": ["acme", "IP"], "count": 3},
            {"node": {"value": "1.1.1.1"}, "label": ["acme", "IP"], "count": 1},
        ]

        with patch("services.graph.repo") as mock_repo, \
             patch("services.graph.TENANT_DATABASE", constraints.TENANT_DATABASE), \
             patch("services.graph.MAPPING_ENTITIES_KEY", constraints.MAPPING_ENTITIES_KEY):
            mock_repo.entities_types_in_cluster = AsyncMock(return_value=fake_records)
            from services.graph import entities_types_in_cluster
            result = await entities_types_in_cluster("acme", "IP")

        assert len(result) == 2
        ids = {r["id"] for r in result}
        assert "8.8.8.8" in ids
        assert "1.1.1.1" in ids


# ══════════════════════════════════════════════════════════════════════════════
#  get_types() và filter_relationship()
# ══════════════════════════════════════════════════════════════════════════════

class TestGetTypesAndFilterRelationship:

    @pytest.mark.asyncio
    async def test_get_types_returns_label_list(self):
        fake_records = [
            {"label": ["acme", "IP"]},
            {"label": "Host"},
        ]
        with patch("services.graph.repo") as mock_repo, \
             patch("services.graph.TENANT_DATABASE", constraints.TENANT_DATABASE):
            mock_repo.get_types = AsyncMock(return_value=fake_records)
            from services.graph import get_types
            result = await get_types("acme", None)

        assert "IP" in result
        assert "Host" in result

    @pytest.mark.asyncio
    async def test_filter_relationship_returns_rel_list(self):
        fake_records = [
            {"relationshipType": ["CONNECTED_TO"]},
            {"relationshipType": "LOGGED_IN"},
        ]
        with patch("services.graph.repo") as mock_repo:
            mock_repo.filter_relationship = AsyncMock(return_value=fake_records)
            from services.graph import filter_relationship
            result = await filter_relationship("acme", "Host")

        assert "CONNECTED_TO" in result
        assert "LOGGED_IN" in result


# ══════════════════════════════════════════════════════════════════════════════
#  ingest() routing — alert vs json parser
# ══════════════════════════════════════════════════════════════════════════════

class TestIngestRouting:

    @pytest.mark.asyncio
    async def test_ingest_alert_uses_alert_parser(self):
        event = {
            "timestamp": "2026-06-03T15:10:00Z",
            "event_id": "a-001",
            "source_type": "alert",
            "message": "Suspicious IP 1.2.3.4 detected",
        }
        with (
                patch("services.graph.post_entity", AsyncMock()),
                patch("services.graph.check_existed_logs", AsyncMock()),
                patch("services.graph.repo.post_relationship", AsyncMock()),
                patch("services.graph.AlertParser") as mock_alert,
                patch("services.graph.JsonParser") as mock_json,
            ):
            mock_parser = MagicMock()
            mock_json.from_event.side_effect = ValueError()
            mock_parser.get_relationship.return_value = []
            mock_parser.get_nodes.return_value = []
            mock_alert.from_event.return_value = mock_parser

            from services.graph import ingest
            await ingest("acme", event)

        mock_alert.from_event.assert_called_once_with(event)
        mock_json.from_event.assert_called_once_with(event, "alert")

    @pytest.mark.asyncio
    async def test_ingest_siem_uses_json_parser(self):
        event = {
            "event_id": "s-001",
            "source_type": "siem",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "bob",
            "destination_host": "WS-001",
        }
        with (
                patch("services.graph.post_entity", AsyncMock()),
                patch("services.graph.check_existed_logs", AsyncMock()),
                patch("services.graph.repo.post_relationship", AsyncMock()),
                patch("services.graph.AlertParser") as mock_alert,
                patch("services.graph.JsonParser") as mock_json,
            ):
            mock_parser = MagicMock()
            mock_parser.get_relationship.return_value = []
            mock_parser.get_nodes.return_value = []
            mock_json.from_event.return_value = mock_parser

            from services.graph import ingest
            await ingest("acme", event)

        mock_json.from_event.assert_called_once_with(event, "siem")
        mock_alert.from_event.assert_not_called()