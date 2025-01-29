# src/niceboard/resources/categories.py
from typing import Dict, Any, List
from ..resource import Resource


class Categories(Resource):
    def list(self) -> List[Dict[str, Any]]:
        """List all job categories."""
        response = self._make_request("GET", "categories")
        return response.json().get("results", {}).get("categories", [])

    def get_mapping(self) -> Dict[str, int]:
        """Get category name to ID mapping."""
        categories = self.list()
        return {category["name"]: category["id"] for category in categories}
