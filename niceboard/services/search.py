import os
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from collections import Counter

from ..client import Client
from ..exceptions import SearchError


class NiceBoardSearchService:
    VALID_QUERY_TYPES = {"jobs", "companies", "locations", "categories", "jobtypes"}

    VALID_FIELDS = {
        "jobs": {
            "id",
            "title",
            "company",
            "location",
            "salary_min",
            "salary_max",
            "remote_only",
            "remote_ok",
            "remote_required_location",
            "apply_url",
            "published_at",
            "description_html",
            "category",
            "jobtype",
            "company.name",
            "company.slug",
            "location.name",
            "location.slug",
            "job_type.name",
            "job_type.slug",
            "category.name",
            "category.slug",
            "is_featured",
            "tags",
            "published_url",
            "slug",
        },
        "companies": {
            "id",
            "name",
            "site_url",
            "description",
            "logo",
            "linkedin_url",
            "twitter_handle",
            "active_jobs",
        },
        "locations": {"id", "name", "slug", "job_count"},
        "categories": {"id", "name", "slug", "job_count"},
        "jobtypes": {"id", "name", "slug", "job_count"},
    }

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("NICEBOARD_API_KEY")
        self.base_url = base_url or os.getenv("NICEBOARD_BASE_URL")
        if not self.api_key:
            raise SearchError(
                "No API key provided and NICEBOARD_API_KEY environment variable not set"
            )

        self.client = Client(api_key=self.api_key, base_url=self.base_url)
        self.base_job_url = self.base_url

    def _validate_query_type(self, query_type: str) -> None:
        if query_type not in self.VALID_QUERY_TYPES:
            raise SearchError(
                f"Invalid query type: {query_type}. Must be one of {self.VALID_QUERY_TYPES}"
            )

    def _format_results(
        self,
        results: List[Dict[str, Any]],
        filtered_results: List[Dict[str, Any]],
        display: str = "summary",
        sample_size: int = 5,
    ) -> Dict[str, Any]:
        if not results:
            return {
                "status": "error",
                "message": "No results found",
                "timestamp": datetime.now().isoformat(),
                "count": 0,
            }

        companies = Counter(
            str((result.get("company") or {}).get("name", "Unknown"))
            for result in results
        )
        locations = Counter(
            str((result.get("location") or {}).get("name", "Unknown"))
            for result in results
        )
        categories = Counter(
            str((result.get("category") or {}).get("name", "Unknown"))
            for result in results
        )
        job_types = Counter(
            str((result.get("jobtype") or {}).get("name", "Unknown"))
            for result in results
        )

        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "count": len(results),
            "statistics": {
                "companies": [
                    {"name": k, "count": v} for k, v in companies.most_common(5)
                ],
                "categories": [
                    {"name": k, "count": v} for k, v in categories.most_common(5)
                ],
                "locations": [
                    {"name": k, "count": v} for k, v in locations.most_common(5)
                ],
                "job_types": [
                    {"name": k, "count": v} for k, v in job_types.most_common(5)
                ],
            },
        }

        if display == "show_n":
            response["sample_entries"] = self._process_entries(
                filtered_results[:sample_size]
            )
        elif display == "all":
            response["entries"] = self._process_entries(filtered_results)

        return response

    def _process_entries(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []
        for result in results:
            entry = {}
            for field, value in result.items():
                if isinstance(value, dict):
                    for attr, attr_value in value.items():
                        entry[f"{field}.{attr}"] = attr_value
                entry[field] = value
            processed.append(entry)
        return processed

    def _validate_fields(self, query_type: str, fields: List[str]) -> None:
        valid_fields = self.VALID_FIELDS[query_type]
        invalid_fields = set(fields) - valid_fields
        if invalid_fields:
            raise SearchError(
                f"Invalid fields for {query_type}: {invalid_fields}. "
                f"For nested fields use dot notation (e.g. 'company.slug')"
            )

    def search(
        self,
        query_type: str,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        display: str = "summary",
        sample_size: int = 5,
    ) -> Dict[str, Any]:
        try:
            self._validate_query_type(query_type)
            if fields:
                self._validate_fields(query_type, fields)
            else:
                fields = list(self.VALID_FIELDS[query_type])

            processed_filters = self._process_filters(filters or {})

            if query_type == "jobs":
                results = self.client.jobs.list(**processed_filters)
            elif query_type == "companies":
                results = self.client.companies.list()
            elif query_type == "locations":
                results = self.client.locations.list()
            elif query_type == "categories":
                results = self.client.categories.list()
            elif query_type == "jobtypes":
                results = self.client.job_types.list()
            else:
                raise SearchError(f"Unsupported query type: {query_type}")

            full_results = results

            if fields:
                filtered_results = []
                for result in results:
                    filtered_result = {}
                    for field in fields:
                        if "." in field:
                            resource, attribute = field.split(".")
                            if resource in result and isinstance(
                                result[resource], dict
                            ):
                                filtered_result[field] = result[resource].get(attribute)
                        else:
                            if field in result:
                                filtered_result[field] = result[field]
                    filtered_results.append(filtered_result)
            else:
                filtered_results = results

            return self._format_results(
                full_results, filtered_results, display=display, sample_size=sample_size
            )
        except Exception as e:
            raise SearchError(f"Search failed: {str(e)}") from e

    def search_jobs(self, **kwargs) -> Dict[str, Any]:
        return self.search(query_type="jobs", **kwargs)

    def search_companies(self, **kwargs) -> Dict[str, Any]:
        return self.search(query_type="companies", **kwargs)

    def search_locations(self, **kwargs) -> Dict[str, Any]:
        return self.search(query_type="locations", **kwargs)

    def search_categories(self, **kwargs) -> Dict[str, Any]:
        return self.search(query_type="categories", **kwargs)

    def search_jobtypes(self, **kwargs) -> Dict[str, Any]:
        return self.search(query_type="jobtypes", **kwargs)

    def _process_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        processed = {}

        filter_mapping = {
            "remote_ok": "remote_ok",
            "company": "company",
            "company.slug": "company",
            "category": "category",
            "category.slug": "category",
            "jobtype": "jobtype",
            "jobtype.slug": "jobtype",
            "tags": "tags",
            "is_featured": "is_featured",
            "keyword": "keyword",
            "location": "location",
            "location.slug": "location",
            "limit": "limit",
            "page": "page",
        }

        for key, value in filters.items():
            if key in filter_mapping:
                mapped_key = filter_mapping[key]
                if key == "company" and value is not None:
                    value = value.lower()
                elif key == "remote_ok" and value is not None:
                    value = bool(value)
                elif key == "location" and value is not None:
                    value = str(value).strip()
                processed[mapped_key] = value
        return processed
