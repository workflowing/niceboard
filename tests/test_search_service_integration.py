import os
from pprint import pprint
from typing import Any, Dict

import pytest

from niceboard.exceptions import SearchError
from niceboard.services.search import NiceBoardSearchService


@pytest.fixture
def search_service():
    """Fixture for search service with API key from environment."""
    api_key = os.getenv("NICEBOARD_API_KEY")
    base_url = os.getenv("NICEBOARD_BASE_URL")
    if not api_key:
        pytest.skip("NICEBOARD_API_KEY environment variable not set")
    return NiceBoardSearchService(api_key=api_key, base_url=base_url)


@pytest.mark.integration
class TestSearchService:
    """Integration tests for NiceBoardSearchService."""

    @pytest.mark.integration
    def test_search_jobs_basic(self, search_service):
        """Test basic job search functionality."""
        results = search_service.search_jobs()

        assert results["status"] == "success"
        assert "count" in results
        assert results["count"] > 0
        assert "statistics" in results
        assert "entries" in results

    @pytest.mark.integration
    def test_search_jobs_with_company_filter(self, search_service):
        """Test job search with company filter."""
        initial_results = search_service.search_jobs(
            filters={"limit": 5},
        )

        assert initial_results["status"] == "success"
        assert len(initial_results["entries"]) > 0

        company_name = initial_results["entries"][0]["company"]["name"]
        company_slug = initial_results["entries"][0]["company"]["slug"]

        results = search_service.search_jobs(filters={"company": company_slug})

        assert results["status"] == "success"
        assert results["count"] > 0
        assert all(job["company"]["name"] == company_name for job in results["entries"])

    @pytest.mark.integration
    def test_search_jobs_limit(self, search_service):
        """Test jobs with limit."""
        sample_results = search_service.search_jobs(filters={"limit": 3})
        assert "entries" in sample_results
        assert len(sample_results["entries"]) <= 3

    @pytest.mark.integration
    def test_search_jobs_with_location_filter(self, search_service):
        """Test job search with location filter."""
        initial_results = search_service.search_jobs(
            filters={"limit": 5},
        )

        location_entry = next(
            (entry for entry in initial_results["entries"] if entry.get("location")),
            None,
        )

        if location_entry:
            location_name = location_entry["location"]["name"]
            location_slug = location_entry["location"]["slug"]
        else:
            location_name = None
            location_slug = None

        results = search_service.search_jobs(filters={"location": location_slug})

        assert results["status"] == "success"
        assert results["count"] > 0
        assert all(
            job["location"]["name"] == location_name for job in results["entries"]
        )

    @pytest.mark.integration
    def test_search_jobs_with_remote_filter(self, search_service):
        """Test job search filtering for remote jobs."""
        results = search_service.search_jobs(filters={"remote_ok": True})

        assert results["status"] == "success"
        all_remote_only = all(job["remote_only"] for job in results["entries"])

        if not all_remote_only:
            assert all(
                job.get("remote_required_location", "").lower().startswith("remote")
                for job in results["entries"]
            ), "When not all jobs are remote_only, all jobs must have remote_required_location starting with 'Remote'"

    @pytest.mark.integration
    def test_invalid_query_type(self, search_service):
        """Test handling of invalid query type."""
        with pytest.raises(SearchError, match="Invalid query type"):
            search_service.search(query_type="invalid")

    @pytest.mark.integration
    def test_search_jobs_pagination(self, search_service):
        """Test job search pagination."""
        page1 = search_service.search_jobs(filters={"limit": 5})

        page2 = search_service.search_jobs(filters={"limit": 5, "page": 2})

        assert page1["status"] == "success"
        assert page2["status"] == "success"
        assert len(page1["entries"]) == 5
        assert len(page2["entries"]) == 5

        page1_ids = {job["id"] for job in page1["entries"]}
        page2_ids = {job["id"] for job in page2["entries"]}
        assert not page1_ids.intersection(page2_ids)

    @pytest.mark.integration
    def test_search_companies_by_name(self, search_service):
        """Test company search by name."""
        results = search_service.search_companies()

        assert results["status"] == "success"
        assert "entries" in results
        assert len(results["entries"]) > 0

        sample_company = results["entries"][0]
        search_term = sample_company["name"][:4]

        search_results = search_service.search_companies(
            filters={"keyword": search_term}
        )

        assert search_results["status"] == "success"
        assert len(search_results["entries"]) > 0
        assert all(
            search_term.lower() in company["name"].lower()
            for company in search_results["entries"]
        )

    @pytest.mark.integration
    def test_search_companies_by_id(self, search_service):
        """Test company search by ID."""
        initial_results = search_service.search_companies()

        assert initial_results["status"] == "success"
        assert len(initial_results["entries"]) > 0

        company_id = initial_results["entries"][0]["id"]

        results = search_service.search_companies(filters={"id": company_id})

        assert results["status"] == "success"
        assert len(results["entries"]) == 1
        assert results["entries"][0]["id"] == company_id

    @pytest.mark.integration
    def test_search_companies_limit(self, search_service):
        """Test limit for company search."""
        sample_results = search_service.search_companies(filters={"limit": 3})
        assert "entries" in sample_results
        assert len(sample_results["entries"]) <= 3

    @pytest.mark.integration
    def test_search_companies_pagination(self, search_service):
        """Test client-side pagination for companies search."""
        all_companies = search_service.search_companies()

        assert all_companies["status"] == "success"
        total_companies = all_companies["pagination"]["total"]

        page1 = search_service.search_companies(filters={"limit": 5, "page": 1})

        page2 = search_service.search_companies(filters={"limit": 5, "page": 2})

        assert page1["status"] == "success"
        assert page2["status"] == "success"

        assert page1["pagination"]["page"] == 1
        assert page2["pagination"]["page"] == 2
        assert page1["pagination"]["limit"] == 5
        assert page2["pagination"]["limit"] == 5
        assert page1["pagination"]["total"] == total_companies
        assert page2["pagination"]["total"] == total_companies

        assert len(page1["entries"]) == 5
        assert len(page2["entries"]) <= 5

        page1_ids = {company["id"] for company in page1["entries"]}
        page2_ids = {company["id"] for company in page2["entries"]}
        assert not page1_ids.intersection(
            page2_ids
        ), "Pages should contain different companies"

        assert [company["id"] for company in page1["entries"]] == [
            company["id"] for company in all_companies["entries"][:5]
        ]
