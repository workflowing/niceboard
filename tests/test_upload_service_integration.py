import os
import pytest
from datetime import datetime
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from niceboard.services.upload import NiceBoardUploadService
from niceboard.client import Client


@pytest.fixture
def sample_job_data():
    """Fixture providing sample job data for testing."""
    return {
        "company": {
            "name": f"Test Company {datetime.now().timestamp()}",
            "description": "A test company",
            "site_url": "https://testcompany.com",
            "logo_url": "https://yahoo.com",
            "linkedin_url": "https://linkedin.com/company/testcompany",
            "twitter_handle": "testcompany",
        },
        "apply_by_form": False,
        "title": f"Test Job {datetime.now().timestamp()}",
        "description_html": "<p>This is a test job posting</p>",
        "job_type": "Full Time",
        "location": "New York, NY",
        "remote": False,
        "salary": "$80,000 - $100,000 per year",
        "apply_url": "https://testcompany.com/careers/test-job",
    }


@pytest.fixture
def created_company(client):
    """
    Fixture that yields None initially and handles company cleanup after test.
    The test should set the company_id on the fixture for cleanup.
    """
    company_id = None

    class CompanyContext:
        def __init__(self):
            self.company_id = None

    context = CompanyContext()
    yield context

    if context.company_id:
        client.companies.delete(context.company_id)


@pytest.fixture
def upload_service():
    """Fixture for upload service with API key from environment."""
    api_key = os.getenv("NICEBOARD_API_KEY")
    base_url = os.getenv("NICEBOARD_BASE_URL")
    if not api_key:
        pytest.skip("NICEBOARD_API_KEY environment variable not set")
    return NiceBoardUploadService(api_key=api_key, base_url=base_url)


@pytest.fixture
def client():
    """Fixture for NiceBoard client for cleanup operations."""
    api_key = os.getenv("NICEBOARD_API_KEY")
    base_url = os.getenv("NICEBOARD_BASE_URL")
    if not api_key:
        pytest.skip("NICEBOARD_API_KEY environment variable not set")
    return Client(api_key=api_key, base_url=base_url)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_job_with_retry(client, job_id):
    """
    Retry getting job details with exponential backoff.
    Will attempt 3 times with delays of 2, 4, and 8 seconds between attempts.
    """
    print(f"Attempt to get job with retry {job_id}")
    job = client.jobs.get(job_id)
    if not job or not job.get("company"):
        raise ValueError("Job or company details not available yet")
    return job


@pytest.mark.integration
class TestUploadService:
    """Integration tests for NiceBoardUploadService."""

    def test_upload_single_job(
        self, upload_service, sample_job_data, client, created_company
    ):
        """Test uploading a single job."""
        # First get a valid job type ID
        job_types = client.job_types.list()
        sample_job_data["job_type_id"] = job_types[0]["id"]

        # Upload job
        result = upload_service.upload_job(sample_job_data)

        if result["success"]:
            try:
                job = get_job_with_retry(client, result["job"]["id"])
                if job and job.get("company"):
                    created_company.company_id = job["company"]["id"]
            except Exception as e:
                pytest.fail(
                    f"Failed to get job details after multiple retries: {str(e)}"
                )

        # Verify upload success
        assert result["success"] == True
        assert "job" in result
        assert "id" in result["job"]

    def test_upload_batch_jobs(
        self, upload_service, sample_job_data, client, created_company
    ):
        """Test uploading multiple jobs in batch."""
        job_types = client.job_types.list()
        job_type_id = job_types[0]["id"]

        # Create multiple job data entries
        jobs = []
        for i in range(3):
            job_data = sample_job_data.copy()
            job_data["title"] = f"Test Job {i} - {datetime.now().timestamp()}"
            job_data["job_type_id"] = job_type_id
            jobs.append(job_data)

        # Upload batch
        result = upload_service.upload_jobs(jobs, batch_size=2)

        if result["success"]:
            try:
                job = get_job_with_retry(client, result["job_ids"][0])
                if job and job.get("company"):
                    created_company.company_id = job["company"]["id"]
            except Exception as e:
                pytest.fail(
                    f"Failed to get job details after multiple retries: {str(e)}"
                )

        # Verify batch upload results
        assert result["success"] == True
        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0

    def test_upload_job_with_remote_location(
        self, upload_service, sample_job_data, client, created_company
    ):
        """Test uploading a remote job."""
        job_types = client.job_types.list()
        sample_job_data["job_type_id"] = job_types[0]["id"]
        sample_job_data["remote"] = True

        result = upload_service.upload_job(sample_job_data)

        if result["success"]:
            job = get_job_with_retry(client, result["job"]["id"])
            if job and job.get("company"):
                created_company.company_id = job["company"]["id"]

        assert result["success"] == True
        if job and job.get("company"):
            assert job["remote_only"] is True

    def test_upload_job_with_salary_conversion(
        self, upload_service, sample_job_data, client, created_company
    ):
        """Test uploading a job with hourly salary conversion."""
        job_types = client.job_types.list()
        sample_job_data["job_type_id"] = job_types[0]["id"]
        sample_job_data["salary"] = "$50 per hour"

        result = upload_service.upload_job(sample_job_data)

        if result["success"]:
            try:
                job = get_job_with_retry(client, result["job"]["id"])
                if job and job.get("company"):
                    created_company.company_id = job["company"]["id"]
            except Exception as e:
                pytest.fail(
                    f"Failed to get job details after multiple retries: {str(e)}"
                )

        assert result["success"] == True
        expected_annual_salary = 50 * 2080
        assert float(job["salary_min"]) == float(expected_annual_salary)

    def test_company_reuse(
        self, upload_service, sample_job_data, client, created_company
    ):
        """Test that uploading multiple jobs for same company reuses company profile."""
        # Upload first job
        first_result = upload_service.upload_job(sample_job_data)

        if first_result["success"]:
            try:
                first_job = get_job_with_retry(client, first_result["job"]["id"])
                if first_job and first_job.get("company"):
                    created_company.company_id = first_job["company"]["id"]
            except Exception as e:
                pytest.fail(
                    f"Failed to get job details after multiple retries: {str(e)}"
                )

        # Upload second job with same company
        second_job_data = sample_job_data.copy()
        second_job_data["title"] = f"Second Test Job {datetime.now().timestamp()}"
        second_result = upload_service.upload_job(second_job_data)
        try:
            second_job = get_job_with_retry(client, second_result["job"]["id"])
            if second_job and second_job.get("company"):
                created_company.company_id = second_job["company"]["id"]
        except Exception as e:
            pytest.fail(f"Failed to get job details after multiple retries: {str(e)}")

        # Verify same company was reused
        assert second_job["company"]["id"] == created_company.company_id
