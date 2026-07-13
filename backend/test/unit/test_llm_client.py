import json
import pytest
from unittest.mock import MagicMock, patch

from parsers.llm_client import LLM_Client


def _make_response(text):
    resp = MagicMock()
    resp.text = text
    return resp


def test_parse_returns_parsed_json_with_entities_decoded():
    encode_entity = {"<IP_0>": "1.2.3.4"}
    raw_response_text = json.dumps({"summary": "attack from <IP_0>"})

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(raw_response_text)

    with patch.object(LLM_Client, "_client", mock_client), \
         patch("parsers.llm_client.Prompt.event_to_prompt", return_value="user prompt"):
        result = LLM_Client.parse({"message": "hi"}, encode_entity)

    assert result == {"summary": "attack from 1.2.3.4"}


def test_parse_calls_generate_content_with_expected_arguments():
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(json.dumps({}))

    with patch.object(LLM_Client, "_client", mock_client), \
         patch("parsers.llm_client.Prompt.event_to_prompt", return_value="user prompt") as mock_prompt:
        LLM_Client.parse({"message": "hi"}, {})

    mock_prompt.assert_called_once_with({"message": "hi"})
    _, kwargs = mock_client.models.generate_content.call_args
    assert kwargs["model"] == LLM_Client.MODEL
    assert kwargs["contents"] == "user prompt"
    assert kwargs["config"].response_mime_type == "application/json"
    assert kwargs["config"].temperature == 0.1


def test_parse_raises_when_response_is_not_valid_json():
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response("not-json-at-all")

    with patch.object(LLM_Client, "_client", mock_client), \
         patch("parsers.llm_client.Prompt.event_to_prompt", return_value="user prompt"):
        with pytest.raises(json.JSONDecodeError):
            LLM_Client.parse({"message": "hi"}, {})


def test_parse_replaces_multiple_encoded_entities():
    encode_entity = {"<IP_0>": "1.2.3.4", "<Domain_0>": "evil.com"}
    raw_response_text = json.dumps({"src": "<IP_0>", "domain": "<Domain_0>"})

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(raw_response_text)

    with patch.object(LLM_Client, "_client", mock_client), \
         patch("parsers.llm_client.Prompt.event_to_prompt", return_value="user prompt"):
        result = LLM_Client.parse({"message": "hi"}, encode_entity)

    assert result == {"src": "1.2.3.4", "domain": "evil.com"}


def test_parse_returns_unmodified_json_when_no_entities_to_decode():
    raw_response_text = json.dumps({"summary": "no entities here"})

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(raw_response_text)

    with patch.object(LLM_Client, "_client", mock_client), \
         patch("parsers.llm_client.Prompt.event_to_prompt", return_value="user prompt"):
        result = LLM_Client.parse({"message": "hi"}, {})

    assert result == {"summary": "no entities here"}