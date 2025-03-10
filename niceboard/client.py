# src/niceboard/client.py
import os
from typing import Optional, Union

from requests import Session

from .resources import Categories, Companies, Jobs, JobTypes, Locations


class Client:
    def __init__(
        self,
        api_key: Optional[str] = os.getenv("NICEBOARD_API_KEY"),
        base_url: Optional[str] = os.getenv("NICEBOARD_BASE_URL"),
    ):
        """
        Initialize the Niceboard client.

        Args:
            api_key (str): The API key for authentication (required)
            base_url (str): Base URL for the API (optional)
        """
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url or "https://api.niceboard.co"

    @property
    def session(self) -> Session:
        """Create an authenticated session."""
        session = Session()
        session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json"}
        )
        return session

    @property
    def companies(self) -> Companies:
        """Access companies resource."""
        return Companies(
            session=self.session, base_url=self.base_url, api_key=self.api_key
        )

    @property
    def jobs(self) -> Jobs:
        """Access jobs resource."""
        return Jobs(session=self.session, base_url=self.base_url, api_key=self.api_key)

    @property
    def locations(self) -> Locations:
        """Access locations resource."""
        return Locations(
            session=self.session, base_url=self.base_url, api_key=self.api_key
        )

    @property
    def categories(self) -> Categories:
        """Access categories resource."""
        return Categories(
            session=self.session, base_url=self.base_url, api_key=self.api_key
        )

    @property
    def job_types(self) -> JobTypes:
        """Access job types resource."""
        return JobTypes(
            session=self.session, base_url=self.base_url, api_key=self.api_key
        )
