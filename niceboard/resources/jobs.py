# src/niceboard/resources/jobs.py
from typing import Dict, Any, List, Optional
from ..resource import Resource
from urllib.parse import urlencode


class Jobs(Resource):
    def list(
        self, company: Optional[str] = None, page: int = 1, limit: int = 30, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List jobs with optional filtering.

        Args:
            company (str): Filter by company slug
            page (int): Page number for pagination
            limit (int): Number of results per page
            **kwargs: Additional filter parameters
        """
        params = {"company": company, "page": page, "limit": limit, **kwargs}
        params = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("GET", "jobs", params=params)
        data = response.json()
        return data.get("results", {}).get("jobs", [])

    def create(
        self,
        company_id: int,
        jobtype_id: int,
        title: str,
        description_html: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new job posting."""
        payload = {
            "company_id": company_id,
            "jobtype_id": jobtype_id,
            "title": title,
            "description_html": description_html,
            **kwargs,
        }
        response = self._make_request("POST", "jobs", data=payload)
        return response.json()

    def get(self, job_id: int) -> Dict[str, Any]:
        """Get a specific job by ID."""
        response = self._make_request("GET", f"jobs/{job_id}")
        return response.json()

    def update(self, job_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing job."""
        response = self._make_request("PATCH", f"jobs/{job_id}", data=kwargs)
        return response.json()

    def delete(self, job_id: int) -> Dict[str, Any]:
        """Update an existing job."""
        response = self._make_request("DELETE", f"jobs/{job_id}")
        return response.json()
