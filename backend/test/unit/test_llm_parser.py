import json
import pytest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from parsers.llm_parser import LLMParser, encode_entity
from parsers.edge_parser import Vertex, EdgePaser


# ---------------------- Helpers ----------------------

def make_vertex(value: str):
    return Vertex(
        type="User",
        value=value
    )


def make_edge(src: str, dest: str):
    return EdgePaser(
        src=make_vertex(src),
        dest=make_vertex(dest),
        connect_type="CONNECTED_TO",
        evidence="evt-1",
        time="2026-07-01T00:00:00Z"
    )


# ---------------------- encode_entity ----------------------

def test_encode_entity_replaces_detected_entities_with_placeholders():
    message = "connection from 1.2.3.4 and 5.6.7.8"
    fake_extract = {"IP": ["1.2.3.4", "5.6.7.8"]}

    with patch("parsers.llm_parser.extract_enitty", return_value=fake_extract):
        encoded, entity_search = encode_entity(message)

    assert encoded == "connection from <IP_0> and <IP_1>"
    assert entity_search == {
        "<IP_0>": "1.2.3.4",
        "<IP_1>": "5.6.7.8"
    }


def test_encode_entity_returns_original_when_nothing_extracted():
    message = "just a plain log line"

    with patch("parsers.llm_parser.extract_enitty", return_value={}):
        encoded, entity_search = encode_entity(message)

    assert encoded == message
    assert entity_search == {}


# ---------------------- normalize_data ----------------------

def test_normalize_data_uses_message_key_only_when_present():
    event = {"message": "hello", "extra": "ignored"}

    with patch(
        "parsers.llm_parser.encode_entity",
        return_value=("encoded", {})
    ) as mock_encode, patch(
        "parsers.llm_parser.LLM_Client.parse",
        return_value=[{"a": 1}]
    ):
        LLMParser.normalize_data(event)

    called_message_arg = mock_encode.call_args[0][0]
    assert json.loads(called_message_arg) == {"message": "hello"}


def test_normalize_data_uses_full_event_when_no_message_key():
    event = {"foo": "bar"}

    with patch(
        "parsers.llm_parser.encode_entity",
        return_value=("encoded", {})
    ) as mock_encode, patch(
        "parsers.llm_parser.LLM_Client.parse",
        return_value=[{"a": 1}]
    ):
        LLMParser.normalize_data(event)

    called_message_arg = mock_encode.call_args[0][0]
    assert json.loads(called_message_arg) == {"foo": "bar"}


def test_normalize_data_uses_string_event_directly():
    event = "raw string event"

    with patch(
        "parsers.llm_parser.encode_entity",
        return_value=("encoded", {})
    ) as mock_encode, patch(
        "parsers.llm_parser.LLM_Client.parse",
        return_value=[]
    ):
        LLMParser.normalize_data(event)

    called_message_arg = mock_encode.call_args[0][0]
    assert json.loads(called_message_arg) == event


def test_normalize_data_returns_llm_result_on_success():
    event = {"message": "hello"}
    fake_result = [{"parsed": True}]

    with patch(
        "parsers.llm_parser.encode_entity",
        return_value=("encoded", {"a": "b"})
    ), patch(
        "parsers.llm_parser.LLM_Client.parse",
        return_value=fake_result
    ):
        result = LLMParser.normalize_data(event)

    assert result == fake_result


def test_normalize_data_raises_runtime_error_when_llm_client_fails():
    event = {"message": "hello"}

    with patch(
        "parsers.llm_parser.encode_entity",
        return_value=("encoded", {})
    ), patch(
        "parsers.llm_parser.LLM_Client.parse",
        side_effect=Exception("boom")
    ):
        with pytest.raises(RuntimeError) as exc_info:
            LLMParser.normalize_data(event)

    assert "Không thể phân tích dữ liệu" in str(exc_info.value)


# ---------------------- from_event ----------------------

def _make_json_parser_result(nodes, edges):
    result = MagicMock()
    result.nodes = nodes
    result.edges = edges
    return result


def test_from_event_builds_nodes_and_edges_and_uses_provided_source_type_timestamp():
    event = {
        "message": "hello",
        "source_type": "wazuh",
        "timestamp": "2026-07-01T00:00:00Z",
        "event_id": "evt-1",
    }

    canonical = [{"foo": "bar"}]

    fake_result = _make_json_parser_result(
        nodes=[make_vertex("node1")],
        edges=[make_edge("node1", "node2")]
    )

    with patch.object(
        LLMParser,
        "normalize_data",
        return_value=canonical
    ), patch(
        "parsers.llm_parser.JsonParser.from_event",
        return_value=fake_result
    ) as mock_json_parser:

        parsed = LLMParser.from_event(event)

    assert parsed.source_type == "wazuh"
    assert parsed.evidence == "evt-1"

    assert len(parsed.nodes) == 1
    assert parsed.nodes[0].value == "node1"

    assert len(parsed.edges) == 1
    assert parsed.edges[0].src.value == "node1"
    assert parsed.edges[0].dest.value == "node2"

    passed_ele = mock_json_parser.call_args[0][0]
    assert passed_ele["source_type"] == "wazuh"
    assert passed_ele["timestamp"] == "2026-07-01T00:00:00Z"


def test_from_event_defaults_source_type_and_timestamp_when_missing():
    event = {"message": "hello"}

    canonical = [{"foo": "bar"}]

    fake_result = _make_json_parser_result(
        nodes=[make_vertex("admin")],
        edges=[]
    )

    with patch.object(
        LLMParser,
        "normalize_data",
        return_value=canonical
    ), patch(
        "parsers.llm_parser.JsonParser.from_event",
        return_value=fake_result
    ) as mock_json_parser:

        parsed = LLMParser.from_event(event)

    passed_ele = mock_json_parser.call_args[0][0]

    assert passed_ele["source_type"] == "canonical"
    assert passed_ele["timestamp"]

    assert parsed.source_type is None
    assert parsed.evidence is None

    assert parsed.nodes[0].value == "admin"


def test_from_event_raises_404_when_no_nodes_extracted():
    event = {"message": "hello"}

    canonical = [{"foo": "bar"}]

    fake_result = _make_json_parser_result(
        nodes=[],
        edges=[]
    )

    with patch.object(
        LLMParser,
        "normalize_data",
        return_value=canonical
    ), patch(
        "parsers.llm_parser.JsonParser.from_event",
        return_value=fake_result
    ):
        with pytest.raises(HTTPException) as exc_info:
            LLMParser.from_event(event)

    assert exc_info.value.status_code == 404


def test_from_event_aggregates_nodes_edges_across_multiple_canonical_items():
    event = {"message": "hello"}

    canonical = [
        {"a": 1},
        {"b": 2}
    ]

    result1 = _make_json_parser_result(
        nodes=[make_vertex("n1")],
        edges=[make_edge("n1", "n2")]
    )

    result2 = _make_json_parser_result(
        nodes=[make_vertex("n2")],
        edges=[make_edge("n2", "n3")]
    )

    with patch.object(
        LLMParser,
        "normalize_data",
        return_value=canonical
    ), patch(
        "parsers.llm_parser.JsonParser.from_event",
        side_effect=[result1, result2]
    ):
        parsed = LLMParser.from_event(event)

    assert len(parsed.nodes) == 2
    assert parsed.nodes[0].value == "n1"
    assert parsed.nodes[1].value == "n2"

    assert len(parsed.edges) == 2
    assert parsed.edges[0].src.value == "n1"
    assert parsed.edges[1].src.value == "n2"