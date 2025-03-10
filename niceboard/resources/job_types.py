# src/niceboard/resources/job_types.py
from typing import Any, Dict, List

from ..resource import Resource


class JobTypes(Resource):
    def list(self) -> List[Dict[str, Any]]:
        """List all job types."""
        response = self._make_request("GET", "jobtypes")
        return response.json().get("results", {}).get("jobtypes", [])
