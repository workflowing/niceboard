# src/niceboard/resources/locations.py
from typing import Any, Dict, List, Optional

from ..resource import Resource
from .geocoding import GeocodeService


class Locations(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geocode_service = GeocodeService()

    def list(self) -> List[Dict[str, Any]]:
        """List all locations."""
        response = self._make_request("GET", "locations")
        return response.json().get("results", {}).get("locations", [])

    def get(self, location_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific location by ID."""
        response = self._make_request("GET", f"locations/{location_id}")
        return response.json().get("results", {}).get("location")

    def create(self, name: str) -> Dict[str, Any]:
        """Create a new location."""
        payload = {"name": name}
        response = self._make_request("POST", "locations", data=payload)
        return response.json()

    def get_or_create(self, location_str: str) -> Optional[int]:
        """Get existing location ID or create new one."""
        if not location_str:
            return None

        if location_str.lower() == "remote":
            return self._handle_remote_location()

        standardized_location = self.geocode_service.standardize_location(location_str)
        if not standardized_location:
            standardized_location = location_str

        # Try to find existing location
        locations = self.list()
        for location in locations:
            if location["name"].lower() == standardized_location.lower():
                return location["id"]

        # Create new location if not found
        new_location = self.create(standardized_location)
        return new_location.get("results", {}).get("location", {}).get("id")

    def _handle_remote_location(self) -> Optional[int]:
        """Handle Remote location special case."""
        locations = self.list()
        for location in locations:
            if "remote" in location["name"].lower():
                return location["id"]

        new_remote = self.create("Remote")
        return new_remote.get("results", {}).get("location", {}).get("id")
