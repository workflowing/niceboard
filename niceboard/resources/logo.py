# src/niceboard/utils/logo.py
import base64
import logging
from io import BytesIO
import requests
from urllib.parse import urlparse
from typing import Optional


class LogoService:
    def __init__(self, clearbit_base_url: str = "https://logo.clearbit.com"):
        self.clearbit_base_url = clearbit_base_url

    def process_logo(
        self, logo_input: str, site_url: Optional[str] = None
    ) -> Optional[str]:
        """Process logo from URL or fetch from Clearbit."""
        if not logo_input and not site_url:
            return None

        if logo_input:
            if logo_input.startswith(("http://", "https://")):
                return self._convert_url_to_base64(logo_input)
            return logo_input

        return self._get_clearbit_logo(site_url) if site_url else None

    def _convert_url_to_base64(self, url: str) -> Optional[str]:
        """Convert image URL to base64 string."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_binary = BytesIO(response.content)
            return base64.b64encode(image_binary.getvalue()).decode("utf-8")
        except Exception as e:
            logging.error(f"Error converting image to base64: {str(e)}")
            return None

    def _get_clearbit_logo(self, site_url: str) -> Optional[str]:
        """Fetch logo from Clearbit."""
        try:
            if not site_url.startswith(("http://", "https://")):
                site_url = f"https://{site_url}"

            domain = urlparse(site_url).netloc
            domain = domain[4:] if domain.startswith("www.") else domain

            if not domain:
                return None

            clearbit_url = f"{self.clearbit_base_url}/{domain}"
            return self._convert_url_to_base64(clearbit_url)
        except Exception as e:
            logging.error(f"Error fetching Clearbit logo: {str(e)}")
            return None
