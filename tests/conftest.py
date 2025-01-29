# tests/conftest.py
import pytest
from niceboard import Client


@pytest.fixture
def client():
    return Client(api_key="test_key")


@pytest.fixture
def mock_session(mocker):
    return mocker.patch("requests.Session")
