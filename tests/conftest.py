# tests/conftest.py
import os
import pytest
from dotenv import load_dotenv
from niceboard import Client

load_dotenv()


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests with real API",
    )


@pytest.fixture
def api_key():
    """Get API key from environment or use test key"""
    return os.getenv("NICEBOARD_API_KEY", "test_key")


@pytest.fixture
def mock_client():
    """Client with mock API key for unit tests"""
    return Client(api_key="test_key", base_url="https://api.niceboard.com")


@pytest.fixture
def client():
    """Create a real client instance with API key from environment"""
    api_key = os.getenv("NICEBOARD_API_KEY")
    base_url = os.getenv("NICEBOARD_BASE_URL")
    if not api_key:
        pytest.skip("NICEBOARD_API_KEY environment variable not set")
    return Client(api_key=api_key, base_url=base_url)


@pytest.fixture
def mock_session(mocker):
    """Mock session for testing API calls"""
    mock = mocker.patch("niceboard.client.Session")
    mock.return_value.headers = {}
    return mock
