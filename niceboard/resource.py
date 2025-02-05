# src/niceboard/resource.py
from requests import Session
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import os


class Resource:
    def __init__(
        self,
        session: Session,
        base_url: str,
        api_key: str,
    ):
        """
        Initialize a resource with session and configuration.

        Args:
            session (Session): Request session to use
            base_url (str): Base URL for the API
            api_key (str): API key for authentication
        """
        self.session = session
        self.base_url = base_url
        self.api_key = api_key

    @property
    def base_job_url(self) -> str:
        """Get the base URL for job listings."""
        base_url = os.getenv("NICEBOARD_BASE_URL")
        domain = "/".join(base_url.split("/")[:3])
        return f"{domain}/job"

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=10))
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make an API request with retry logic."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}?key={self.api_key}"
        try:
            response = self.session.request(
                method, url, json=data, params=params, timeout=10
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logging.error(f"Request failed: {str(e)}")
            raise
