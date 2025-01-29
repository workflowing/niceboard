# tests/test_client.py
import pytest
from niceboard import Client


def test_client_initialization():
    client = Client(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "https://jobs.auditfriendly.co/api/v1/"


def test_client_requires_api_key():
    with pytest.raises(ValueError, match="api_key is required"):
        Client(api_key=None)


def test_client_session_headers(client):
    session = client.session
    assert session.headers["Accept"] == "application/json"
    assert session.headers["Content-Type"] == "application/json"
