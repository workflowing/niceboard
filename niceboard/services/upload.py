import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..client import Client
from ..exceptions import SearchError
from ..resources.logo import LogoService
from ..resources.geocoding import GeocodeService


class NiceBoardUploadService:
    """Service for uploading jobs to NiceBoard with proper processing and validation."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("NICEBOARD_API_KEY")
        self.base_url = base_url or os.getenv("NICEBOARD_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "No API key provided and NICEBOARD_API_KEY environment variable not set"
            )

        self.client = Client(api_key=self.api_key, base_url=self.base_url)
        self.logo_service = LogoService()
        self.geocode_service = GeocodeService()

    def _process_company(self, company_data: Dict[str, Any]) -> int:
        """Process company data and return company ID."""
        try:
            # Check if company exists
            companies = self.client.companies.list()
            company_name = company_data["name"].lower()

            existing_company = next(
                (c for c in companies if c["name"].lower() == company_name), None
            )

            if existing_company:
                return existing_company["id"]

            # Process logo if provided
            logo = None
            if company_data.get("logo_url"):
                try:
                    logo = self.logo_service.process_logo(
                        company_data["logo_url"], company_data.get("website")
                    )
                except Exception as e:
                    print(f"Logo processing failed: {str(e)}")

            # Create new company
            company = self.client.companies.create(
                name=company_data["name"],
                description=company_data.get("description"),
                site_url=company_data.get("site_url"),
                logo=logo,
                linkedin_url=company_data.get("linkedin_url"),
                twitter_handle=company_data.get("twitter_handle"),
            )

            return company["results"]["company"]["id"]

        except Exception as e:
            raise ValueError(f"Failed to process company: {str(e)}") from e

    def _process_location(self, location: str) -> int:
        """
        Process location string and return location ID.

        Args:
            location: String representing the location (city, state or full address)

        Returns:
            Location ID from the API
        """
        try:
            if not location:
                raise ValueError("No location provided")

            # Standardize location string
            standardized_location = self.geocode_service.standardize_location(location)

            # Get or create location
            location_result = self.client.locations.get_or_create(standardized_location)

            return location_result

        except Exception as e:
            raise ValueError(f"Failed to process location: {str(e)}") from e

    def _process_salary(self, salary_text: str) -> Dict[str, Any]:
        """Process salary information with standardized parsing.

        Args:
            salary_text: Raw salary text from job listing (e.g. "$80,000 - $100,000 per year", "$40/hour")

        Returns:
            Dict containing standardized salary_min and salary_max values converted to annual amounts
        """
        salary_data = {"salary_min": None, "salary_max": None}

        if not salary_text:
            return salary_data

        try:
            text = salary_text.lower().strip()

            def parse_amount(value: str) -> float:
                """Extract numeric value from string."""
                return float(re.sub(r"[^\d.]", "", value))

            def get_multiplier(text: str) -> float:
                """Get multiplier to convert to annual salary."""
                if "hour" in text:
                    return 2080  # 40 hours * 52 weeks
                elif "month" in text:
                    return 12
                return 1  # already yearly

            multiplier = get_multiplier(text)

            # Extract all numbers from text
            numbers = re.findall(r"[\d,.]+", text)

            if len(numbers) >= 2:
                # Handle range (e.g. "$50,000 - $70,000")
                salary_data["salary_min"] = parse_amount(numbers[0]) * multiplier
                salary_data["salary_max"] = parse_amount(numbers[1]) * multiplier
            elif len(numbers) == 1:
                # Handle single value
                amount = parse_amount(numbers[0]) * multiplier
                salary_data["salary_min"] = amount
                salary_data["salary_max"] = amount

        except Exception as e:
            print(f"Could not parse salary text: {salary_text} - Error: {str(e)}")

        return salary_data

    def _get_job_type_id(self, job_type: str) -> int:
        """
        Get job type ID from string representation.

        Args:
            job_type: String representation of job type (e.g. "full time", "part time")

        Returns:
            Job type ID from the API

        Raises:
            ValueError: If job type cannot be found or is invalid
        """
        try:
            # Get all job types from API
            job_types = self.client.job_types.list()

            # Normalize the input job type
            normalized_type = job_type.lower().strip()

            print(f"\n job_type {job_type}")

            # Try to find exact match first
            for jtype in job_types:
                if jtype["name"].lower() == normalized_type:
                    return jtype["id"]

            # Try to find partial match if exact match fails
            for jtype in job_types:
                if normalized_type in jtype["name"].lower():
                    return jtype["id"]

            raise ValueError(f"Job type '{job_type}' not found in available types")

        except Exception as e:
            raise ValueError(f"Failed to process job type: {str(e)}") from e

    def upload_job(self, **kwargs) -> Dict[str, Any]:
        """
        Upload a single job to NiceBoard with proper processing and validation.

        Args:
            **kwargs: Dictionary containing job information including:
                - company information
                - job details
                - location information
                - salary data

        Returns:
            Dictionary containing upload result and job ID, or error details
        """
        try:
            job_data = kwargs.get("job_data", {})

            # Process company if company_id not provided
            if "company_id" in job_data:
                company_id = job_data["company_id"]
            else:
                try:
                    company_id = self._process_company(job_data["company"])
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Company processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "company",
                    }

            # Process location if location_id not provided
            if "location_id" in job_data:
                location_id = job_data["location_id"]
            else:
                try:
                    location_id = self._process_location(job_data["location"])
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Location processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "location",
                    }

            # Process salary
            try:
                salary_info = self._process_salary(job_data.get("salary"))
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Salary processing failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "field_error": "salary",
                }

            # Process job type if job_type_id not provided
            if "job_type_id" in job_data:
                job_type_id = job_data["job_type_id"]
            else:
                try:
                    job_type_id = self._get_job_type_id(job_data["job_type"])
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Job type processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "job_type",
                    }

            # Create job
            try:
                response = self.client.jobs.create(
                    company_id=company_id,
                    jobtype_id=job_type_id,
                    title=job_data["title"],
                    description_html=job_data["description_html"],
                    apply_by_form=job_data["apply_by_form"],
                    location_id=location_id,
                    is_remote=job_data.get("remote", False),
                    remote_only=job_data.get("remote", False),
                    apply_url=job_data.get("apply_url"),
                    **salary_info,
                )
                return response
            except Exception as e:
                error_msg = str(e)

                error_response = {
                    "success": False,
                    "error": f"API call failed: {error_msg}",
                    "timestamp": datetime.now().isoformat(),
                }

                return error_response

        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def upload_jobs(self, **kwargs) -> Dict[str, Any]:
        """
        Upload multiple jobs with batching and detailed error handling.

        Args:
            **kwargs: Dictionary containing:
                - jobs: List of job data dictionaries
                - batch_size: Number of jobs to process in each batch

        Returns:
            Dictionary containing upload statistics and detailed error results
        """
        jobs = kwargs.get("jobs", [])
        batch_size = kwargs.get("batch_size", 10)

        results = {
            "total": len(jobs),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "job_ids": [],
            "timestamp": datetime.now().isoformat(),
        }

        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]

            for j, job in enumerate(batch):
                upload_result = self.upload_job(job_data=job)

                # Check if the result indicates success
                if upload_result.get("success") == True:
                    results["successful"] += 1
                    results["job_ids"].append(upload_result["job"]["id"])
                else:
                    results["failed"] += 1
                    job_index = i + j  # Calculate overall job index

                    upload_result["job_index"] = job_index
                    upload_result["job_title"] = job.get("title", "Unknown")

                    results["errors"].append(upload_result)

        # Determine overall success status
        if results["failed"] == 0:
            results["success"] = True
        elif results["successful"] > 0:
            results["success"] = "partial_success"
        else:
            results["success"] = False

        return results
