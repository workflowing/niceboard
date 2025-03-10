# src/niceboard/resources/companies.py
from typing import Any, Dict, List, Optional

from ..resource import Resource


class Companies(Resource):
    def list(self) -> List[Dict[str, Any]]:
        """List all companies."""
        response = self._make_request("GET", "companies")
        return response.json().get("results", {}).get("companies", [])

    def get(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific company by ID."""
        response = self._make_request("GET", f"companies/{company_id}")
        return response.json().get("results", {}).get("company")

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new company.

        Args:
            name (str): Company name
            **kwargs: Optional fields (site_url, twitter_handle, linkedin_url, etc.)
        """
        payload = {"name": name}

        if kwargs.get("logo"):
            payload["logo"] = kwargs["logo"]

        payload.update({k: v for k, v in kwargs.items() if v is not None})

        response = self._make_request("POST", "companies", data=payload)
        return response.json()

    def delete(self, company_id: int) -> Dict[str, Any]:
        """
        Delete a specific company by ID.

        Args:
            company_id (int): ID of the company to delete

        Returns:
            Dict[str, Any]: Response from the API
        """
        response = self._make_request("DELETE", f"companies/{company_id}")
        return response.json()
