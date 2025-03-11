import os
import re
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

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

        # In-memory caches
        self._companies_cache: Dict[str, int] = {}
        self._company_slug_cache: Dict[int, str] = {}
        self._location_cache: Dict[str, int] = {}
        self._location_slug_cache: Dict[int, str] = {}
        self._job_types_cache: Optional[List[Dict[str, Any]]] = None
        self._job_type_id_cache: Dict[str, int] = {}

    def _prefetch_job_types(self):
        """Fetch and cache all job types."""
        if self._job_types_cache is None:
            self._job_types_cache = self.client.job_types.list()
            # Also build the id lookup cache
            for jtype in self._job_types_cache:
                normalized_name = jtype["name"].lower().strip()
                self._job_type_id_cache[normalized_name] = jtype["id"]
                self._job_type_id_cache[jtype["slug"]] = jtype["id"]
                # Also cache simplified versions
                simple_name = re.sub(r"[^a-z0-9]", "", normalized_name)
                self._job_type_id_cache[simple_name] = jtype["id"]

    def _prefetch_companies(self, job_batch: List[Dict[str, Any]]):
        """
        Prefetch companies for the entire batch.

        Args:
            job_batch: List of job data dictionaries
        """
        # Only prefetch if we don't already have a full cache
        if not self._companies_cache:
            companies = self.client.companies.list()
            for company in companies:
                self._companies_cache[company["name"].lower()] = company["id"]
                self._company_slug_cache[company["id"]] = company["slug"]

        # Extract unique company names from the batch that aren't in cache yet
        company_names_to_create = set()
        for job in job_batch:
            if "company_id" not in job and "company_name" in job:
                company_name = job["company_name"].lower()
                if company_name not in self._companies_cache:
                    company_names_to_create.add(company_name)

        # We could do a bulk create companies API call here if the API supports it
        # For now, we'll create them individually but only for those not in cache

    def _batch_process_locations(self, job_batch: List[Dict[str, Any]]):
        """
        Process all locations in the batch to avoid repeated geocoding.

        Args:
            job_batch: List of job data dictionaries
        """
        # Extract unique locations from the batch
        unique_locations = set()
        for job in job_batch:
            if "location_id" not in job and "location" in job and job["location"]:
                unique_locations.add(job["location"])

        # Process each unique location once
        for location in unique_locations:
            if location not in self._location_cache:
                try:
                    standardized_location = self.geocode_service.standardize_location(
                        location
                    )
                    if standardized_location:
                        location_id = self.client.locations.get_or_create(
                            standardized_location
                        )
                        if location_id:
                            self._location_cache[location] = location_id
                            # Also fetch and cache the slug
                            location_data = self.client.locations.get(location_id)
                            if location_data and "slug" in location_data:
                                self._location_slug_cache[location_id] = location_data[
                                    "slug"
                                ]
                except Exception as e:
                    print(f"Failed to process location batch {location}: {str(e)}")

    def _process_company(self, company_data: Dict[str, Any]) -> int:
        """Process a company, using cache when possible."""
        try:
            if "company_name" not in company_data:
                raise ValueError("Missing required field: company_name")
            if company_data["company_name"] is None:
                raise ValueError("company_name cannot be None")

            company_name = company_data["company_name"].lower()

            # Check cache first
            if company_name in self._companies_cache:
                return self._companies_cache[company_name]

            # Slow path - check API and update cache
            companies = self.client.companies.list()
            for c in companies:
                self._companies_cache[c["name"].lower()] = c["id"]
                self._company_slug_cache[c["id"]] = c["slug"]

            if company_name in self._companies_cache:
                return self._companies_cache[company_name]

            # Create new company
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

            company_id = company["results"]["company"]["id"]
            # Update cache
            self._companies_cache[company_name] = company_id
            return company_id

        except Exception as e:
            raise ValueError(f"Failed to process company: {str(e)}") from e

    def _process_location(self, location: str) -> int:
        """Process a location, using cache when possible."""
        try:
            if not location:
                raise ValueError("No location provided")

            # Check cache first
            if location in self._location_cache:
                return self._location_cache[location]

            standardized_location = self.geocode_service.standardize_location(location)

            if standardized_location is None:
                raise ValueError(f"Could not standardize location: {location}")

            location_id = self.client.locations.get_or_create(standardized_location)

            if location_id is None:
                raise ValueError(
                    f"Failed to get or create location for: {standardized_location}"
                )

            # Update cache
            self._location_cache[location] = location_id
            return location_id

        except Exception as e:
            raise ValueError(f"Failed to process location: {str(e)}") from e

    def _process_salary(self, salary_text: str) -> Dict[str, Optional[float]]:
        """Process salary information. This is fast enough and doesn't need caching."""
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
        """Get job type ID with caching."""
        if job_type is None:
            raise ValueError("Job type cannot be None")
        if not job_type:
            raise ValueError("Job type cannot be empty")

        try:
            # Ensure job types are loaded
            self._prefetch_job_types()

            normalized_input = job_type.lower().strip()

            # Check direct matches in cache
            if normalized_input in self._job_type_id_cache:
                return self._job_type_id_cache[normalized_input]

            # Try simplified version
            simple_input = re.sub(r"[^a-z0-9]", "", normalized_input)
            if simple_input in self._job_type_id_cache:
                return self._job_type_id_cache[simple_input]

            # Try partial matches - only if _job_types_cache is not None
            if self._job_types_cache is not None:
                for jtype in self._job_types_cache:
                    simple_name = re.sub(r"[^a-z0-9]", "", jtype["name"].lower())
                    if simple_input in simple_name or simple_name in simple_input:
                        self._job_type_id_cache[normalized_input] = jtype[
                            "id"
                        ]  # Cache the result
                        return jtype["id"]

            # Prepare error message with valid types
            valid_types = {}
            if self._job_types_cache is not None:
                valid_types = {
                    jtype["name"]: {
                        "id": jtype["id"],
                        "slug": jtype["slug"],
                        "name": jtype["name"],
                    }
                    for jtype in self._job_types_cache
                }
            else:
                valid_types = {"error": {"message": "Job types could not be loaded"}}

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
        """Get company slug with caching."""
        try:
            # Check cache first
            if company_id in self._company_slug_cache:
                return self._company_slug_cache[company_id]

            # Slow path - API call
            company = self.client.companies.get(company_id)
            if company is None:
                return None

            slug = company.get("slug")
            # Update cache
            if slug:
                self._company_slug_cache[company_id] = slug

            return slug
        except Exception as e:
            raise ValueError(f"Failed to get company slug: {str(e)}") from e

    def _get_location_slug(self, location_id: int) -> Optional[str]:
        """Get location slug with caching."""
        try:
            # Check cache first
            if location_id in self._location_slug_cache:
                return self._location_slug_cache[location_id]

            # Slow path - API call
            location = self.client.locations.get(location_id)
            if location is None:
                return None

            slug = location.get("slug")
            # Update cache
            if slug:
                self._location_slug_cache[location_id] = slug

            return slug
        except Exception as e:
            raise ValueError(f"Failed to get location slug: {str(e)}") from e

    def _batch_find_existing_jobs(
        self, job_batch: List[Dict[str, Any]]
    ) -> Dict[Tuple[int, int, str], int]:
        """
        Find existing jobs in batch to minimize API calls.

        Args:
            job_batch: List of job data dictionaries

        Returns:
            Dictionary mapping (company_id, location_id, title) tuples to job_id
        """
        existing_jobs = {}

        # Group jobs by company and location to minimize API calls
        company_location_groups: Dict[
            Tuple[int, int], List[Tuple[int, Dict[str, Any]]]
        ] = {}

        for i, job in enumerate(job_batch):
            if all(k in job for k in ["company_id", "location_id", "title"]):
                key = (job["company_id"], job["location_id"])
                if key not in company_location_groups:
                    company_location_groups[key] = []
                company_location_groups[key].append((i, job))

        # For each company/location pair, make a single API call
        for (company_id, location_id), jobs in company_location_groups.items():
            try:
                # Get slugs (using cached values if available)
                company_slug = self._get_company_slug(company_id)
                location_slug = self._get_location_slug(location_id)

                if not company_slug or not location_slug:
                    continue

                # Get all jobs for this company/location pair
                api_jobs = self.client.jobs.list(
                    company=company_slug,
                    location=location_slug,
                    limit=100,
                )

                # Create lookup dictionary
                job_dict = {job["title"].lower().strip(): job["id"] for job in api_jobs}

                # Check each job in this group
                for _, job in jobs:
                    normalized_title = job["title"].lower().strip()
                    if normalized_title in job_dict:
                        existing_jobs[(company_id, location_id, normalized_title)] = (
                            job_dict[normalized_title]
                        )
            except Exception as e:
                print(
                    f"Error finding existing jobs for company {company_id}, location {location_id}: {str(e)}"
                )

        return existing_jobs

    def _find_existing_job(self, job_data: Dict[str, Any]) -> Optional[int]:
        """Find existing job, using the batch results if available."""
        try:
            key = (
                job_data["company_id"],
                job_data["location_id"],
                job_data["title"].lower().strip(),
            )

            # Check if we have a batch result
            if (
                hasattr(self, "_batch_existing_jobs")
                and key in self._batch_existing_jobs
            ):
                return self._batch_existing_jobs[key]

            # Fall back to individual lookup
            company_slug = self._get_company_slug(job_data["company_id"])
            location_slug = self._get_location_slug(job_data["location_id"])

            if not company_slug:
                raise ValueError(
                    f"Could not get company slug for ID: {job_data['company_id']}"
                )
            if not location_slug:
                raise ValueError(
                    f"Could not get location slug for ID: {job_data['location_id']}"
                )

            jobs = self.client.jobs.list(
                company=company_slug,
                location=location_slug,
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

    def upload_job(self, **kwargs) -> Dict[str, Any]:
        """
        Upload a single job to NiceBoard with proper processing and validation.
        Will update the job if it already exists.
        """
        try:
            job_data = kwargs.get("job_data", {})
            batch_mode = kwargs.get("batch_mode", False)

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
                # In batch mode, use the pre-computed results
                existing_job_id = None
                if batch_mode and hasattr(self, "_batch_existing_jobs"):
                    key = (
                        job_data["company_id"],
                        job_data["location_id"],
                        job_data["title"].lower().strip(),
                    )
                    existing_job_id = self._batch_existing_jobs.get(key)
                else:
                    existing_job_id = self._find_existing_job(job_data)

                if existing_job_id:
                    response = self.client.jobs.update(existing_job_id, **job_params)
                    return {
                        "success": True,
                        "operation": "updated",
                        "job": response.get("job", {}),
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
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
        Upload multiple jobs with batching and optimized processing.

        Args:
            **kwargs: Dictionary containing:
                - jobs: List of job data dictionaries
                - batch_size: Number of jobs to process in each batch

        Returns:
            Dictionary containing upload statistics and detailed error results
        """
        jobs = kwargs.get("jobs", [])
        batch_size = kwargs.get("batch_size", 10)

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

            valid_batch = []
            for j, job in enumerate(batch):
                missing_fields = []

                if "company_id" not in job and (
                    "company_name" not in job or job["company_name"] is None
                ):
                    missing_fields.append("company_id or company_name")

                if "location_id" not in job and (
                    "location" not in job or job["location"] is None
                ):
                    missing_fields.append("location_id or location")

                if "jobtype_id" not in job and (
                    "job_type" not in job or job["job_type"] is None
                ):
                    missing_fields.append("jobtype_id or job_type")

                for field in ["title", "description_html"]:
                    if field not in job or job[field] is None:
                        missing_fields.append(field)

                if "apply_by_form" in job and job["apply_by_form"] is False:
                    if "apply_url" not in job and "apply_email" not in job:
                        missing_fields.append("apply_url or apply_email")

                if missing_fields:
                    results["failed"] += 1
                    error_info = {
                        "success": False,
                        "message": f"Missing required fields: {', '.join(missing_fields)}",
                        "timestamp": datetime.now().isoformat(),
                        "job_index": i + j,
                        "job_title": job.get("title", "Unknown"),
                        "field_error": missing_fields[0] if missing_fields else None,
                    }
                    results["errors"].append(error_info)
                else:
                    valid_batch.append(job)

            if valid_batch:
                try:
                    self._prefetch_job_types()
                    self._prefetch_companies(valid_batch)
                    self._batch_process_locations(valid_batch)

                    for job in valid_batch:
                        if "company_id" not in job and "company_name" in job:
                            job["company_id"] = self._process_company(job)
                        if "location_id" not in job and "location" in job:
                            job["location_id"] = self._process_location(job["location"])

                    self._batch_existing_jobs = self._batch_find_existing_jobs(
                        valid_batch
                    )

                    for job in valid_batch:
                        job_index = i + batch.index(job)

                        try:
                            upload_result = self.upload_job(
                                job_data=job, batch_mode=True
                            )

                            if upload_result.get("success") is True:
                                results["successful"] += 1

                                job_id = upload_result.get("job", {}).get("id")
                                if job_id is not None:
                                    results["job_ids"].append(job_id)
                            else:
                                results["failed"] += 1
                                error_info = upload_result.copy()
                                error_info["job_index"] = job_index
                                error_info["job_title"] = job.get("title", "Unknown")
                                results["errors"].append(error_info)
                        except Exception as e:
                            results["failed"] += 1
                            results["errors"].append(
                                {
                                    "success": False,
                                    "message": f"Error processing job: {str(e)}",
                                    "timestamp": datetime.now().isoformat(),
                                    "job_index": job_index,
                                    "job_title": job.get("title", "Unknown"),
                                }
                            )
                except Exception as e:
                    pass
                finally:
                    if hasattr(self, "_batch_existing_jobs"):
                        delattr(self, "_batch_existing_jobs")

        if results["failed"] == 0:
            results["success"] = True
        elif results["successful"] > 0:
            results["success"] = "partial_success"
        else:
            results["success"] = False

        return results
