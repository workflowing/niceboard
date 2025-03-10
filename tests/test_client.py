# tests/test_client.py
import pytest

from niceboard import Client


def test_client_initialization():
    client = Client(api_key="test_key", base_url="https://base_url")
    assert client.api_key == "test_key"
    assert client.base_url == "https://base_url"


def test_client_requires_api_key():
    with pytest.raises(ValueError, match="api_key is required"):
        Client(api_key=None)


def test_client_session_headers(mock_client):
    session = mock_client.session
    assert session.headers["Accept"] == "application/json"
    assert session.headers["Content-Type"] == "application/json"
