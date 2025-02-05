import os
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from collections import Counter

from ..client import Client
from ..exceptions import SearchError


class NiceBoardSearchService:
    VALID_QUERY_TYPES = {"jobs", "companies", "locations", "categories", "jobtypes"}

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
        display: str = "summary",
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

        if display == "limit" or display == "all":
            response["entries"] = results

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

    def search(
        self,
        query_type: str,
        filters: Optional[Dict[str, Any]] = None,
        display: str = "summary",
    ) -> Dict[str, Any]:
        try:
            self._validate_query_type(query_type)
            processed_filters = self._process_filters(filters or {})

            page = int(processed_filters.get("page", 1))
            limit = min(int(processed_filters.get("limit", 30)), 100)

            if query_type == "jobs":
                results = self.client.jobs.list(**processed_filters)
            else:
                if query_type == "companies":
                    all_results = self.client.companies.list()
                    all_results = self._filter_companies(all_results, processed_filters)
                elif query_type == "locations":
                    all_results = self.client.locations.list()
                elif query_type == "categories":
                    all_results = self.client.categories.list()
                elif query_type == "jobtypes":
                    all_results = self.client.job_types.list()
                else:
                    raise SearchError(f"Unsupported query type: {query_type}")

                start_idx = (page - 1) * limit
                end_idx = start_idx + limit
                results = all_results[start_idx:end_idx]

            response = self._format_results(results, display=display)

            response["pagination"] = {
                "page": page,
                "limit": limit,
                "total": len(all_results) if query_type != "jobs" else len(results),
            }

            return response

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
            "id": "id",
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
                elif key == "id" and value is not None:
                    value = int(value) if str(value).isdigit() else value
                processed[mapped_key] = value
        return processed

    def _filter_companies(
        self, companies: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter companies based on provided filters."""
        filtered_companies = companies

        if not filters:
            return filtered_companies

        if "keyword" in filters:
            keyword = filters["keyword"].lower()
            filtered_companies = [
                company
                for company in filtered_companies
                if keyword in company.get("name", "").lower()
            ]

        if "id" in filters:
            company_id = filters["id"]
            filtered_companies = [
                company
                for company in filtered_companies
                if company.get("id") == company_id
            ]

        return filtered_companies

    def search_niceboard(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute niceboard search with standardized args format.

        Args:
            args: Dictionary containing:
                query_type: str - Type of search (jobs, companies, locations, categories, jobtypes)
                filters: Dict - Optional filters (remote_ok, company, category, etc.)
                display: str - How to display results (summary or limit)
                page: int - Page number for pagination
                limit: int - Results per page (max 100)
        """
        filters = args.get("filters", {})
        if "page" in args:
            filters["page"] = args["page"]
        if "limit" in args:
            filters["limit"] = args["limit"]

        return self.search(
            query_type=args.get("query_type"),
            filters=filters,
            display=args.get("display", "summary"),
        )
