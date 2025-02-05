import os
import pytest
from pprint import pprint
from typing import Dict, Any

from niceboard.services.search import NiceBoardSearchService
from niceboard.exceptions import SearchError


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
        results = search_service.search_jobs(
            fields=["title", "company", "location"], display="all"
        )

        assert results["status"] == "success"
        assert "count" in results
        assert results["count"] > 0
        assert "statistics" in results
        assert "entries" in results

    @pytest.mark.integration
    def test_search_jobs_with_company_filter(self, search_service):
        """Test job search with company filter."""

        initial_results = search_service.search_jobs(
            fields=["company.name", "company.slug", "title", "id"],
            display="show_n",
            sample_size=5,
        )

        assert initial_results["status"] == "success"
        assert len(initial_results["sample_entries"]) > 0

        company_name = initial_results["sample_entries"][0]["company.name"]
        company_slug = initial_results["sample_entries"][0]["company.slug"]

        results = search_service.search_jobs(
            filters={"company": company_slug}, display="all"
        )

        assert results["status"] == "success"
        assert results["count"] > 0
        assert all(job["company"]["name"] == company_name for job in results["entries"])

    @pytest.mark.integration
    def test_search_jobs_display_modes(self, search_service):
        """Test different display modes."""

        summary_results = search_service.search_jobs(display="summary")
        assert "statistics" in summary_results
        assert "entries" not in summary_results
        assert summary_results["statistics"]["companies"]

        sample_results = search_service.search_jobs(display="show_n", sample_size=3)
        assert "sample_entries" in sample_results
        assert len(sample_results["sample_entries"]) <= 3

    @pytest.mark.integration
    def test_search_jobs_with_location_filter(self, search_service):
        """Test job search with location filter."""
        initial_results = search_service.search_jobs(
            fields=[
                "company.name",
                "company.slug",
                "title",
                "id",
                "location.name",
                "location.slug",
            ],
            display="show_n",
            sample_size=5,
        )

        location_entry = next(
            (
                entry
                for entry in initial_results["sample_entries"]
                if "location.name" in entry and "location.slug" in entry
            ),
            None,
        )

        if location_entry:
            location_name = location_entry["location.name"]
            location_slug = location_entry["location.slug"]
        else:
            location_name = None
            location_slug = None

        results = search_service.search_jobs(
            filters={"location": location_slug}, display="all"
        )

        assert results["status"] == "success"
        assert results["count"] > 0
        assert all(
            job["location"]["name"] == location_name for job in results["entries"]
        )

    @pytest.mark.integration
    def test_search_jobs_with_remote_filter(self, search_service):
        """Test job search filtering for remote jobs."""
        results = search_service.search_jobs(filters={"remote_ok": True}, display="all")

        assert results["status"] == "success"
        all_remote_only = all(job["remote_only"] for job in results["entries"])

        if not all_remote_only:
            assert all(
                job.get("remote_required_location", "").lower().startswith("remote")
                for job in results["entries"]
            ), "When not all jobs are remote_only, all jobs must have remote_required_location starting with 'Remote'"

    @pytest.mark.integration
    def test_search_jobs_with_multiple_fields(self, search_service):
        """Test job search with multiple field selection."""
        fields = [
            "title",
            "company",
            "location",
            "salary_min",
            "salary_max",
            "remote_only",
            "category",
            "jobtype",
        ]

        results = search_service.search_jobs(
            fields=fields, display="show_n", sample_size=5
        )

        assert results["status"] == "success"
        assert "sample_entries" in results
        for entry in results["sample_entries"]:
            for field in fields:
                assert field in entry

    @pytest.mark.integration
    def test_invalid_query_type(self, search_service):
        """Test handling of invalid query type."""
        with pytest.raises(SearchError, match="Invalid query type"):
            search_service.search(query_type="invalid", fields=["name"])

    @pytest.mark.integration
    def test_invalid_fields(self, search_service):
        """Test handling of invalid fields."""
        with pytest.raises(SearchError, match="Invalid fields"):
            search_service.search_jobs(fields=["invalid_field"])

    @pytest.mark.integration
    def test_search_jobs_pagination(self, search_service):
        """Test job search pagination."""

        page1 = search_service.search_jobs(filters={"limit": 5}, display="all")

        page2 = search_service.search_jobs(
            filters={"limit": 5, "page": 2}, display="all"
        )

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
        results = search_service.search_companies(
            fields=["id", "name", "site_url"], display="all"
        )

        assert results["status"] == "success"
        assert "entries" in results
        assert len(results["entries"]) > 0

        sample_company = results["entries"][0]
        search_term = sample_company["name"][:4]

        search_results = search_service.search_companies(
            fields=["id", "name"], filters={"keyword": search_term}, display="all"
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
        initial_results = search_service.search_companies(
            fields=["id", "name"], display="all"
        )

        assert initial_results["status"] == "success"
        assert len(initial_results["entries"]) > 0

        company_id = initial_results["entries"][0]["id"]

        results = search_service.search_companies(
            filters={"id": company_id}, display="all"
        )

        assert results["status"] == "success"
        assert len(results["entries"]) == 1
        assert results["entries"][0]["id"] == company_id

    @pytest.mark.integration
    def test_search_companies_with_multiple_fields(self, search_service):
        """Test company search with multiple field selection."""
        fields = [
            "id",
            "name",
            "site_url",
            "description_html",
            "logo_url",
            "linkedin_url",
            "twitter_handle",
            "slug",
        ]

        results = search_service.search_companies(fields=fields, display="all")

        assert results["status"] == "success"
        assert "entries" in results
        assert len(results["entries"]) > 0

        for field in fields:
            assert field in results["entries"][0]

    @pytest.mark.integration
    def test_search_companies_display_modes(self, search_service):
        """Test different display modes for company search."""
        summary_results = search_service.search_companies(display="summary")
        assert "statistics" in summary_results
        assert "entries" not in summary_results

        sample_results = search_service.search_companies(
            display="show_n", sample_size=3
        )
        assert "sample_entries" in sample_results
        assert len(sample_results["sample_entries"]) <= 3

        all_results = search_service.search_companies(display="all")
        assert "entries" in all_results

    @pytest.mark.integration
    def test_search_companies_pagination(self, search_service):
        """Test client-side pagination for companies search."""

        all_companies = search_service.search_companies(
            fields=["id", "name"], display="all"
        )

        assert all_companies["status"] == "success"
        total_companies = all_companies["pagination"]["total"]

        page1 = search_service.search_companies(
            fields=["id", "name"], filters={"limit": 5, "page": 1}, display="all"
        )

        page2 = search_service.search_companies(
            fields=["id", "name"], filters={"limit": 5, "page": 2}, display="all"
        )

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
