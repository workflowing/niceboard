# src/niceboard/utils/geocoding.py
import logging
from functools import lru_cache
from typing import Optional

from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim


class GeocodeService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="niceboard_service")
        self._cache = {}

    def standardize_location(
        self, location_str: str, max_attempts: int = 3
    ) -> Optional[str]:
        """Standardize location string using geocoding."""
        if location_str.lower() == "remote":
            return "Remote"

        if location_str in self._cache:
            return self._cache[location_str]

        for attempt in range(max_attempts):
            try:
                locations = self.geolocator.geocode(
                    location_str,
                    addressdetails=True,
                    timeout=10,
                    exactly_one=False,
                    language="en",
                )

                if locations:
                    location = str(locations[0])

                    parts = [part.strip() for part in location.split(",")]
                    standardized = ", ".join(parts)

                    self._cache[location_str] = standardized
                    return standardized

            except GeocoderTimedOut:
                if attempt == max_attempts - 1:
                    logging.error("Maximum geocoding retry attempts reached")
                    break
                continue

        self._cache[location_str] = None
        return None
