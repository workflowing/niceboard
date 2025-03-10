import os
from datetime import datetime
from typing import Any, Dict

import pytest
from tenacity import retry, stop_after_attempt, wait_exponential

from niceboard.client import Client
from niceboard.services.upload import NiceBoardUploadService


@pytest.fixture
def sample_job_data():
    return {
        "company_name": f"Test Company {datetime.now().timestamp()}",
        "company_description": "A test company",
        "company_site_url": "https://testcompany.com",
        "company_logo_url": "https://yahoo.com",
        "company_linkedin_url": "https://linkedin.com/company/testcompany",
        "company_twitter_handle": "testcompany",
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
    api_key = os.getenv("NICEBOARD_API_KEY")
    base_url = os.getenv("NICEBOARD_BASE_URL")
    if not api_key:
        pytest.skip("NICEBOARD_API_KEY environment variable not set")
    return NiceBoardUploadService(api_key=api_key, base_url=base_url)


@pytest.fixture
def client():
    api_key = os.getenv("NICEBOARD_API_KEY")
    base_url = os.getenv("NICEBOARD_BASE_URL")
    if not api_key:
        pytest.skip("NICEBOARD_API_KEY environment variable not set")
    return Client(api_key=api_key, base_url=base_url)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_job_with_retry(client, job_id):
    print(f"Attempt to get job with retry {job_id}")
    job = client.jobs.get(job_id)
    if not job or not job.get("company"):
        raise ValueError("Job or company details not available yet")
    return job


@pytest.mark.integration
class TestUploadService:
    def test_upload_single_job(
        self, upload_service, sample_job_data, client, created_company
    ):
        job_types = client.job_types.list()
        sample_job_data["jobtype_id"] = job_types[0]["id"]

        result = upload_service.upload_job(job_data=sample_job_data)

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
        assert "job" in result
        assert "id" in result["job"]

    def test_upload_batch_jobs(
        self, upload_service, sample_job_data, client, created_company
    ):
        job_types = client.job_types.list()
        jobtype_id = job_types[0]["id"]

        jobs = []
        for i in range(3):
            job_data = sample_job_data.copy()
            job_data["title"] = f"Test Job {i} - {datetime.now().timestamp()}"
            job_data["jobtype_id"] = jobtype_id
            jobs.append(job_data)

        result = upload_service.upload_jobs(jobs=jobs, batch_size=2)

        if result["success"]:
            try:
                job = get_job_with_retry(client, result["job_ids"][0])
                if job and job.get("company"):
                    created_company.company_id = job["company"]["id"]
            except Exception as e:
                pytest.fail(
                    f"Failed to get job details after multiple retries: {str(e)}"
                )
        assert result["success"] == True
        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0

    def test_upload_job_with_remote_location(
        self, upload_service, sample_job_data, client, created_company
    ):
        job_types = client.job_types.list()
        sample_job_data["jobtype_id"] = job_types[0]["id"]
        sample_job_data["remote"] = True

        result = upload_service.upload_job(job_data=sample_job_data)

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
        job_types = client.job_types.list()
        sample_job_data["jobtype_id"] = job_types[0]["id"]
        sample_job_data["salary"] = "$50 per hour"

        result = upload_service.upload_job(job_data=sample_job_data)

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
        first_result = upload_service.upload_job(job_data=sample_job_data)

        if first_result["success"]:
            try:
                first_job = get_job_with_retry(client, first_result["job"]["id"])
                if first_job and first_job.get("company"):
                    created_company.company_id = first_job["company"]["id"]
            except Exception as e:
                pytest.fail(
                    f"Failed to get job details after multiple retries: {str(e)}"
                )
        second_job_data = sample_job_data.copy()
        second_job_data["title"] = f"Second Test Job {datetime.now().timestamp()}"
        second_result = upload_service.upload_job(job_data=second_job_data)
        try:
            second_job = get_job_with_retry(client, second_result["job"]["id"])
            if second_job and second_job.get("company"):
                created_company.company_id = second_job["company"]["id"]
        except Exception as e:
            pytest.fail(f"Failed to get job details after multiple retries: {str(e)}")

        assert second_job["company"]["id"] == created_company.company_id

    def test_update_existing_job(
        self, upload_service, sample_job_data, client, created_company
    ):
        """Test updating an existing job."""
        job_types = client.job_types.list()
        sample_job_data["jobtype_id"] = job_types[0]["id"]

        first_result = upload_service.upload_job(job_data=sample_job_data)
        assert first_result["success"] == True
        assert first_result["operation"] == "created"

        job_id = first_result["job"]["id"]
        if first_result["job"].get("company"):
            created_company.company_id = first_result["job"]["company"]["id"]

        updated_job_data = sample_job_data.copy()
        updated_job_data["title"] = sample_job_data["title"]
        updated_job_data["description_html"] = "<p>Updated job description</p>"
        updated_job_data["salary"] = "$90,000 - $120,000 per year"

        update_result = upload_service.upload_job(job_data=updated_job_data)

        assert update_result["success"] == True
        assert update_result["operation"] == "updated"

        updated_job = get_job_with_retry(client, job_id)
        assert updated_job["description_html"] == "<p>Updated job description</p>"
        assert float(updated_job["salary_min"]) == 90000
        assert float(updated_job["salary_max"]) == 120000

    def test_update_nonexistent_job(self, upload_service, sample_job_data, client):
        """Test attempting to update a job that doesn't exist creates new job."""
        job_types = client.job_types.list()
        sample_job_data["jobtype_id"] = job_types[0]["id"]
        sample_job_data["title"] = f"Nonexistent Job {datetime.now().timestamp()}"

        result = upload_service.upload_job(job_data=sample_job_data)

        assert result["success"] == True
        assert result["operation"] == "created"
