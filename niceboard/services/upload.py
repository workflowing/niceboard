import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..client import Client
from ..exceptions import SearchError
from ..resources.geocoding import GeocodeService
from ..resources.logo import LogoService


class NiceBoardUploadService:
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
        try:
            companies = self.client.companies.list()
            company_name = company_data["company_name"].lower()

            existing_company = next(
                (c for c in companies if c["name"].lower() == company_name), None
            )

            if existing_company:
                return existing_company["id"]

            logo = None
            if company_data.get("company_logo_url"):
                try:
                    logo = self.logo_service.process_logo(
                        company_data["company_logo_url"], company_data.get("website")
                    )
                except Exception as e:
                    print(f"Logo processing failed: {str(e)}")

            company = self.client.companies.create(
                name=company_data["company_name"],
                description=company_data.get("company_description"),
                site_url=company_data.get("company_site_url"),
                logo=logo,
                linkedin_url=company_data.get("company_linkedin_url"),
                twitter_handle=company_data.get("company_twitter_handle"),
            )

            return company["results"]["company"]["id"]

        except Exception as e:
            raise ValueError(f"Failed to process company: {str(e)}") from e

    def _process_location(self, location: str) -> int:
        try:
            if not location:
                raise ValueError("No location provided")

            standardized_location = self.geocode_service.standardize_location(location)

            if standardized_location is None:
                raise ValueError(f"Could not standardize location: {location}")

            location_result = self.client.locations.get_or_create(standardized_location)

            if location_result is None:
                raise ValueError(
                    f"Failed to get or create location for: {standardized_location}"
                )

            return location_result

        except Exception as e:
            raise ValueError(f"Failed to process location: {str(e)}") from e

    def _process_salary(self, salary_text: str) -> Dict[str, Optional[float]]:
        salary_data: Dict[str, Optional[float]] = {
            "salary_min": None,
            "salary_max": None,
        }
        if not salary_text:
            return salary_data

        try:
            text = salary_text.lower().strip()

            def parse_amount(value: str) -> float:
                return float(re.sub(r"[^\d.]", "", value))

            def get_multiplier(text: str) -> float:
                if "hour" in text:
                    return 2080
                elif "month" in text:
                    return 12
                return 1

            multiplier = get_multiplier(text)

            numbers = re.findall(r"[\d,.]+", text)

            if len(numbers) >= 2:
                salary_data["salary_min"] = parse_amount(numbers[0]) * multiplier
                salary_data["salary_max"] = parse_amount(numbers[1]) * multiplier
            elif len(numbers) == 1:
                amount = parse_amount(numbers[0]) * multiplier
                salary_data["salary_min"] = amount
                salary_data["salary_max"] = amount

        except Exception as e:
            print(f"Could not parse salary text: {salary_text} - Error: {str(e)}")

        return salary_data

    def _get_jobType_id(self, job_type: str) -> int:
        if not job_type:
            raise ValueError("Job type cannot be empty")

        try:
            job_types = self.client.job_types.list()
            normalized_input = job_type.lower().strip()

            valid_types = {
                jtype["name"]: {
                    "id": jtype["id"],
                    "slug": jtype["slug"],
                    "name": jtype["name"],
                }
                for jtype in job_types
            }

            for jtype in job_types:
                if (
                    normalized_input == jtype["name"].lower()
                    or normalized_input == jtype["slug"]
                ):
                    return jtype["id"]

            simple_input = re.sub(r"[^a-z0-9]", "", normalized_input)
            for jtype in job_types:
                simple_name = re.sub(r"[^a-z0-9]", "", jtype["name"].lower())
                if simple_input == simple_name:
                    return jtype["id"]

            for jtype in job_types:
                simple_name = re.sub(r"[^a-z0-9]", "", jtype["name"].lower())
                if simple_input in simple_name or simple_name in simple_input:
                    return jtype["id"]

            error_msg = {
                "error": f"Job type '{job_type}' not found in available types",
                "valid_job_types": valid_types,
                "suggestion": "Please select one of the valid job types listed",
            }
            raise ValueError(str(error_msg))

        except Exception as e:
            if "valid_job_types" not in str(e):
                raise ValueError(f"Failed to process job type: {str(e)}") from e
            raise

    def _find_existing_job(self, job_data: Dict[str, Any]) -> Optional[int]:
        """
        Find existing job by title, company and location.
        Args:
            job_data: Dictionary containing job information
        Returns:
            Job ID if found, None otherwise
        """
        try:
            # Get company and location slugs from their IDs
            company_slug = self._get_company_slug(job_data["company_id"])
            location_slug = self._get_location_slug(job_data["location_id"])

            # Verify we have valid slugs before proceeding
            if not company_slug:
                raise ValueError(
                    f"Could not get company slug for ID: {job_data['company_id']}"
                )
            if not location_slug:
                raise ValueError(
                    f"Could not get location slug for ID: {job_data['location_id']}"
                )

            # Use the slugs in the API call as per the API documentation
            jobs = self.client.jobs.list(
                company=company_slug,  # Using slug instead of ID
                location=location_slug,  # Using slug instead of ID
                keyword=job_data["title"],
                limit=100,
            )

            normalized_title = job_data["title"].lower().strip()
            for job in jobs:
                if job["title"].lower().strip() == normalized_title:
                    return job["id"]

            return None

        except Exception as e:
            raise ValueError(f"Failed to search for existing job: {str(e)}") from e

    def _extract_job_id_from_error(
        self, error_response: Dict[str, Any]
    ) -> Optional[int]:
        """Extract job ID from error response when job already exists."""
        if isinstance(error_response, dict):
            if (
                error_response.get("reason") == "job_exists"
                and "job_id" in error_response
            ):
                return error_response["job_id"]
        return None

    def _get_company_slug(self, company_id: int) -> Optional[str]:
        """Helper method to get company slug from ID."""
        try:
            company = self.client.companies.get(company_id)

            # Add null check before calling .get() method
            if company is None:
                return None

            return company.get("slug")
        except Exception as e:
            raise ValueError(f"Failed to get company slug: {str(e)}") from e

    def _get_location_slug(self, location_id: int) -> Optional[str]:
        """Helper method to get location slug from ID."""
        try:
            location = self.client.locations.get(location_id)

            # Add null check before calling .get() method
            if location is None:
                return None

            return location.get("slug")
        except Exception as e:
            raise ValueError(f"Failed to get location slug: {str(e)}") from e

    def upload_job(self, **kwargs) -> Dict[str, Any]:
        """
        Upload a single job to NiceBoard with proper processing and validation.
        Will update the job if it already exists.
        """
        try:
            job_data = kwargs.get("job_data", {})

            # Process company data
            if "company_id" not in job_data:
                try:
                    job_data["company_id"] = self._process_company(job_data)
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Company processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "company",
                    }

            # Process location data
            if "location_id" not in job_data:
                try:
                    job_data["location_id"] = self._process_location(
                        job_data["location"]
                    )
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Location processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "location",
                    }

            # Process salary data
            salary_info = {}
            if "salary" in job_data:
                try:
                    salary_info = self._process_salary(job_data.get("salary"))
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Salary processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "salary",
                    }

            # Process job type
            if "jobtype_id" not in job_data:
                try:
                    job_data["jobtype_id"] = self._get_jobType_id(job_data["job_type"])
                except Exception as e:
                    error_info = str(e)
                    if "valid_job_types" in error_info:
                        return {
                            "success": False,
                            "message": "Invalid job type",
                            "error_details": eval(error_info),
                            "timestamp": datetime.now().isoformat(),
                            "field_error": "job_type",
                            "needs_correction": True,
                        }
                    return {
                        "success": False,
                        "message": f"Job type processing failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "field_error": "job_type",
                    }

            # Prepare common job parameters
            job_params = {
                "company_id": job_data["company_id"],
                "jobtype_id": job_data["jobtype_id"],
                "title": job_data["title"],
                "description_html": job_data["description_html"],
                "apply_by_form": job_data.get("apply_by_form", False),
                "location_id": job_data["location_id"],
                "is_remote": job_data.get("remote", False),
                "remote_only": job_data.get("remote", False),
                "apply_url": job_data.get("apply_url"),
                **salary_info,
            }

            # First check if job exists
            try:
                existing_job_id = self._find_existing_job(job_data)

                # Update existing job
                if existing_job_id:
                    response = self.client.jobs.update(existing_job_id, **job_params)
                    return {
                        "success": True,
                        "operation": "updated",
                        "job": response.get("job", {}),
                        "timestamp": datetime.now().isoformat(),
                    }

                # Create new job
                response = self.client.jobs.create(**job_params)

                return {
                    "success": True,
                    "operation": "created",
                    "job": response.get("job", {}),
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"API call failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
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

        # Initialize results with proper types
        results: Dict[str, Any] = {
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

                if upload_result.get("success") is True:
                    results["successful"] += 1

                    job_id = upload_result.get("job", {}).get("id")
                    if job_id is not None:
                        results["job_ids"].append(job_id)
                else:
                    results["failed"] += 1
                    job_index = i + j
                    error_info = upload_result.copy()
                    error_info["job_index"] = job_index
                    error_info["job_title"] = job.get("title", "Unknown")
                    results["errors"].append(error_info)

        if results["failed"] == 0:
            results["success"] = True
        elif results["successful"] > 0:
            results["success"] = "partial_success"
        else:
            results["success"] = False

        return results
