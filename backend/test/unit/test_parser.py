"""
Unit tests for parser layer.
- BaseParser.split_nodes_edges
- JsonParser.from_event (SIEM / EDR / Cloud)
- AlertParser.from_event (regex-based)

Không cần DB, không cần Neo4j — toàn bộ dependency được mock bởi conftest.
"""
import sys, types, pytest
from conftest import MAPPING_ENTITIES_KEY
from unittest.mock import MagicMock

from parsers.base_parser   import BaseParser
from parsers.json_parser   import JsonParser
from parsers.alert_parser  import AlertParser
from parsers.edge_parser   import Vertex


# ══════════════════════════════════════════════════════════════════════════════
#  BaseParser.split_nodes_edges
# ══════════════════════════════════════════════════════════════════════════════

class TestBaseParserSplitNodesEdges:

    def _make_parser(self):
        """Dummy BaseParser instance."""
        return BaseParser(nodes=[], edges=[], source_type="test", evidence="")

    def test_extracts_nodes_from_include(self):
        event = {
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "john.doe",
            "destination_host": "DESKTOP-001",
            "source_ip": "10.0.0.1",
        }
        from conftest import SIEM_INCLUDE
        parser = self._make_parser()
        nodes, edges = parser.split_nodes_edges(event, SIEM_INCLUDE)

        values = {n.value for n in nodes}
        assert "john.doe" in values
        assert "DESKTOP-001" in values
        assert "10.0.0.1" in values

    def test_skips_missing_fields(self):
        event = {"timestamp": "2024-01-01T00:00:00Z", "user": "admin"}
        from conftest import SIEM_INCLUDE
        parser = self._make_parser()
        nodes, _ = parser.split_nodes_edges(event, SIEM_INCLUDE)
        # Chỉ có user — destination_host và source_ip không có trong event
        assert len(nodes) == 1
        assert nodes[0].value == "admin"

    def test_creates_edge_for_known_relationship(self):
        event = {
            "timestamp": "2024-01-01T00:00:00Z",
            "source_ip": "192.168.1.1",
            "destination_host": "SERVER-01",
        }
        from conftest import SIEM_INCLUDE
        parser = self._make_parser()
        _, edges = parser.split_nodes_edges(event, SIEM_INCLUDE)

        assert len(edges) == 1
        assert edges[0]["type"] == "CONNECTED_TO"
        assert edges[0]["source"].value == "192.168.1.1"
        assert edges[0]["target"].value == "SERVER-01"

    def test_no_edge_when_relationship_not_in_mapping(self):
        """IP → Domain không có trong MAPPING_RELATIONSHIPS → không tạo edge."""
        event = {
            "timestamp": "2024-01-01T00:00:00Z",
            "source_ip": "1.2.3.4",
            "destination_domain": "example.com",
        }
        from conftest import CLOUD_INCLUDE
        # CLOUD_INCLUDE không có edge IP→Domain
        parser = self._make_parser()
        _, edges = parser.split_nodes_edges(event, CLOUD_INCLUDE)
        # source_host missing → không có node Host → không có edge
        assert all(e["type"] != "" for e in edges)

    def test_stores_timestamp_on_edge(self):
        event = {
            "timestamp": "2024-06-01T09:00:00Z",
            "user": "alice",
            "destination_host": "WS-002",
        }
        from conftest import SIEM_INCLUDE
        parser = self._make_parser()
        _, edges = parser.split_nodes_edges(event, SIEM_INCLUDE)

        login_edge = next((e for e in edges if e["type"] == "LOGGED_IN"), None)
        assert login_edge is not None
        assert login_edge["time"] == "2024-06-01T09:00:00Z"


# ══════════════════════════════════════════════════════════════════════════════
#  JsonParser.from_event
# ══════════════════════════════════════════════════════════════════════════════

class TestJsonParserFromEvent:

    def test_siem_extracts_user_host_ip(self):
        event = {
            "event_id": "evt-001",
            "source_type": "siem",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "john.doe",
            "source_ip": "203.0.113.45",
            "destination_host": "DESKTOP-001",
        }
        parser = JsonParser.from_event(event, "siem")

        values = {n.value for n in parser.nodes}
        assert "john.doe" in values
        assert "203.0.113.45" in values
        assert "DESKTOP-001" in values

    def test_siem_creates_connected_to_edge(self):
        event = {
            "event_id": "evt-002",
            "source_type": "siem",
            "timestamp": "2024-01-01T00:00:00Z",
            "source_ip": "1.2.3.4",
            "destination_host": "HOST-01",
        }
        parser = JsonParser.from_event(event, "siem")
        edge_types = {e["type"] for e in parser.edges}
        assert "CONNECTED_TO" in edge_types

    def test_edr_extracts_all_fields(self):
        event = {
            "event_id": "evt-003",
            "source_type": "edr",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "admin",
            "destination_host": "FILE-SERVER-01",
            "destination_ip": "185.220.101.45",
            "destination_domain": "malicious.ru",
            "file_hash": "44d88612fea8a8f36de82e1278abb02f",
            "process_name": "powershell.exe",
            "parent_process": "explorer.exe",
        }
        parser = JsonParser.from_event(event, "edr")

        values = {n.value for n in parser.nodes}
        assert "admin" in values
        assert "FILE-SERVER-01" in values
        assert "185.220.101.45" in values
        assert "powershell.exe" in values
        assert "explorer.exe" in values

    def test_edr_parent_spawned_child_edge(self):
        event = {
            "event_id": "evt-004",
            "source_type": "edr",
            "timestamp": "2024-01-01T00:00:00Z",
            "destination_host": "HOST-01",
            "parent_process": "services.exe",
            "process_name": "cmd.exe",
        }
        parser = JsonParser.from_event(event, "edr")
        edge_types = {e["type"] for e in parser.edges}
        assert "SPAWNED" in edge_types

    def test_cloud_extracts_host_ip(self):
        event = {
            "event_id": "evt-005",
            "source_type": "cloud",
            "timestamp": "2024-01-01T00:00:00Z",
            "source_host": "ip-10-0-1-25.ec2.internal",
            "destination_ip": "0.0.0.0",
        }
        parser = JsonParser.from_event(event, "cloud")

        values = {n.value for n in parser.nodes}
        assert "ip-10-0-1-25.ec2.internal" in values
        assert "0.0.0.0" in values

    def test_unsupported_source_raises_value_error(self):
        event = {"event_id": "evt-999", "source_type": "unknown"}
        with pytest.raises(ValueError, match="Unsupported log source"):
            JsonParser.from_event(event, "unknown_source")

    def test_evidence_set_from_event_id(self):
        event = {
            "event_id": "evt-42",
            "source_type": "siem",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "bob",
            "destination_host": "WS-001",
        }
        parser = JsonParser.from_event(event, "siem")
        assert parser.evidence == "evt-42"

    def test_empty_event_returns_no_nodes(self):
        event = {"event_id": "evt-empty", "source_type": "siem", "timestamp": "2024-01-01T00:00:00Z"}
        parser = JsonParser.from_event(event, "siem")
        assert parser.nodes == []
        assert parser.edges == []

    def test_get_relationship_returns_edge_parsers(self):
        event = {
            "event_id": "evt-rel",
            "source_type": "siem",
            "timestamp": "2024-01-01T00:00:00Z",
            "user": "carol",
            "destination_host": "SERVER-02",
        }
        parser = JsonParser.from_event(event, "siem")
        rels = parser.get_relationship()

        assert len(rels) > 0
        assert rels[0].connect_type == "LOGGED_IN"
        assert rels[0].src.value == "carol"
        assert rels[0].dest.value == "SERVER-02"


# ══════════════════════════════════════════════════════════════════════════════
#  AlertParser.from_event (regex-based)
# ══════════════════════════════════════════════════════════════════════════════

class TestAlertParser:

    def test_extracts_ip_from_message(self):
        event = {
            "event_id": "alert-001",
            "source_type": "alert",
            "message": "Suspicious login from 203.0.113.10 to host DESKTOP-001",
        }
        parser = AlertParser.from_event(event)
        values = {n.value for n in parser.nodes}
        assert "203.0.113.10" in values

    def test_extracts_domain_from_message(self):
        event = {
            "event_id": "alert-002",
            "source_type": "alert",
            "message": "Connection to 198.1.1.1 detected",
        }
        parser = AlertParser.from_event(event)
        values = {n.value for n in parser.nodes}
        assert "198.1.1.1" in values

    def test_extracts_file_hash_md5(self):
        event = {
            "event_id": "alert-003",
            "source_type": "alert",
            "message": "File hash 44d88612fea8a8f36de82e1278abb02f found on host",
        }
        parser = AlertParser.from_event(event)
        values = {n.value for n in parser.nodes}
        assert "44d88612fea8a8f36de82e1278abb02f" in values

    def test_extracts_multiple_entities(self):
        event = {
            "event_id": "alert-004",
            "source_type": "alert",
            "message": "IP 1.2.3.4 connected to evil-download.com, hash 44d88612fea8a8f36de82e1278abb02f",
        }
        parser = AlertParser.from_event(event)
        values = {n.value for n in parser.nodes}
        assert "1.2.3.4" in values
        assert "evil-download.com" in values
        assert "44d88612fea8a8f36de82e1278abb02f" in values

    def test_empty_message_returns_no_nodes(self):
        event = {"event_id": "alert-empty", "source_type": "alert", "message": ""}
        parser = AlertParser.from_event(event)
        assert parser.nodes == []

    def test_no_false_positive_private_ip(self):
        """192.168.x.x vẫn là IP hợp lệ về mặt regex."""
        event = {
            "event_id": "alert-005",
            "source_type": "alert",
            "message": "Login from 192.168.1.100",
        }
        parser = AlertParser.from_event(event)
        values = {n.value for n in parser.nodes}
        assert "192.168.1.100" in values

    def test_node_types_are_correct(self):
        event = {
            "event_id": "alert-006",
            "source_type": "alert",
            "message": "Alert: 10.0.0.5 contacted google.com",
        }
        parser = AlertParser.from_event(event)
        types = {n.type for n in parser.nodes}
        assert "IP" in types
        assert "Domain" in types