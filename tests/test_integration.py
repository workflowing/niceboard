# tests/test_integration.py
import pytest
from pprint import pprint
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_job_with_retry(client, job_id):
    """
    Retry getting job details with exponential backoff.
    Will attempt 3 times with delays of 2, 4, and 8 seconds between attempts.
    """
    print(f"Attempt to get job with retry {job_id}")
    job = client.jobs.get(job_id=job_id)
    if not job or not job.get("company"):
        raise ValueError("Job or company details not available yet")
    return job


@pytest.mark.integration
class TestIntegration:
    def test_list_companies(self, client):
        """Fetch and inspect companies response structure"""
        try:
            companies = client.companies.list()
            print("\nCompanies Response Structure:")
            pprint(companies[:2] if companies else "Empty response")
            assert isinstance(companies, list)

            if companies:
                print("\nFirst Company Fields:")
                pprint(list(companies[0].keys()))
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

    def test_get_company(self, client):
        """Fetch and inspect a single company's response structure"""
        try:
            companies = client.companies.list()
            if not companies:
                pytest.skip("No companies available to test with")

            company_id = companies[0]["id"]
            company = client.companies.get(company_id)

            print("\nSingle Company Response Structure:")
            pprint(company)
            assert isinstance(company, dict)
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

    @pytest.mark.integration
    def test_get_job(self, client):
        """Fetch and inspect a single job's response structure"""
        try:
            jobs = client.jobs.list()
            if not jobs:
                pytest.skip("No jobs available to test with")

            job_id = jobs[0]["id"]
            # Replace direct call with retry function
            job = get_job_with_retry(client, job_id)

            print("\nSingle Job Response Structure:")
            pprint(job)
            assert isinstance(job, dict)
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

    @pytest.mark.integration
    @pytest.mark.destructive
    def test_create_company(self, client):
        """Create and verify a new company, then clean up"""
        created_company_id = None
        try:
            company_data = {
                "name": "Test Company Integration",
                "site_url": "https://example.com",
                "description": "<p>Test company created by integration tests</p>",
                "tagline": "Testing company creation",
                "custom_fields": '[{"id": "test-field", "value": "test-value"}]',
            }

            print("\nAttempting to create company with data:")
            pprint(company_data)

            response = client.companies.create(**company_data)
            print("\nCreate Company Response Structure:")
            pprint(response)

            assert response["success"] is True
            created_company = response["results"]["company"]
            created_company_id = created_company["id"]

            # Verify all fields were set correctly
            assert created_company["name"] == company_data["name"]
            assert created_company["site_url"] == company_data["site_url"]
            assert created_company["tagline"] == company_data["tagline"]
            assert created_company["description_html"] == company_data["description"]

        except Exception as e:
            print(f"\nError occurred during company creation: {str(e)}")
            raise
        finally:
            # Clean up: Delete the test company
            if created_company_id:
                try:
                    print(f"\nCleaning up - deleting company {created_company_id}")
                    delete_response = client.companies.delete(created_company_id)
                    assert delete_response.get("success") is True
                    print("Test company deleted successfully")
                except Exception as e:
                    print(f"Warning: Cleanup failed: {str(e)}")

    # tests/test_integration.py
    @pytest.mark.integration
    @pytest.mark.destructive
    def test_delete_company(self, client):
        """Test deletion of company created in test_create_company"""
        try:
            # List companies to find the test company
            companies = client.companies.list()
            test_company = next(
                (
                    company
                    for company in companies
                    if company["name"] == "Test Company Integration"
                ),
                None,
            )

            if test_company is None:
                print("\nTest company not found - it may have already been deleted")
                return

            company_id = test_company["id"]
            print(f"\nFound test company with ID: {company_id}")

            # Delete the company
            print(f"\nAttempting to delete company {company_id}")
            delete_response = client.companies.delete(company_id)
            assert delete_response.get("success") is True
            print("Delete operation completed successfully")

            # Verify deletion
            deleted_company = client.companies.get(company_id)
            assert deleted_company is None, "Company should not exist after deletion"
            print("Verified company was deleted successfully")

        except Exception as e:
            print(f"\nError occurred during deletion test: {str(e)}")
            raise

    @pytest.mark.integration
    @pytest.mark.destructive
    def test_create_job(self, client):
        """Create and verify a new job, then clean up"""
        created_job_id = None
        try:
            # Step 1: Get valid category, job type, and location IDs
            print("\nFetching valid categories...")
            categories = client.categories.list()
            if not categories:
                pytest.skip("No categories available - cannot test job creation")
            category_id = categories[0]["id"]

            print("\nFetching valid job types...")
            job_types = client.job_types.list()
            if not job_types:
                pytest.skip("No job types available - cannot test job creation")
            jobtype_id = job_types[0]["id"]

            print("\nFetching valid locations...")
            locations = client.locations.list()
            location_id = locations[0]["id"] if locations else None

            company_data = {
                "name": "Test Company for Job",
                "site_url": "https://example.com",
                "description": "<p>Test company for job integration tests</p>",
                "tagline": "Testing job creation",
            }
            company_response = client.companies.create(**company_data)
            company_id = company_response["results"]["company"]["id"]

            custom_fields = '[ { id: "experience-level", value: "senior" }, { id: "department", value: "engineering" } ]'

            job_data = {
                "company_id": company_id,
                "jobtype_id": jobtype_id,
                "category_id": category_id,
                "location_id": location_id,
                "tags": "python, django, api",
                "title": "Senior Software Engineer",
                "apply_by_form": True,
                "apply_url": "https://example.com/apply",
                "apply_email": "jobs@example.com",
                "description_html": "<p>Test job created by integration tests</p>",
                "salary_min": 80000,
                "salary_max": 120000,
                "salary_timeframe": "annually",
                "salary_currency": "USD",
                "is_remote": True,
                "remote_only": False,
                "remote_required_location": "US/Pacific",
                "is_featured": False,
                "is_published": True,
                "published_at": "2024-01-01T00:00:00Z",
                "expires_on": "2024-02-01",
                "custom_fields": custom_fields,
            }

            print("\nAttempting to create job with data:")
            pprint(job_data)

            response = client.jobs.create(**job_data)
            print("\nCreate Job Response Structure:")
            pprint(response)

            assert response["success"] is True
            created_job = response["job"]
            created_job_id = created_job["id"]

            assert created_job["title"] == job_data["title"]
            assert created_job["company_id"] == job_data["company_id"]
            assert created_job["jobtype_id"] == job_data["jobtype_id"]
            assert created_job["description_html"] == job_data["description_html"]
            assert created_job["apply_by_form"] == job_data["apply_by_form"]

            if "salary_min" in created_job:
                assert float(created_job["salary_min"]) == float(job_data["salary_min"])
            if "salary_max" in created_job:
                assert float(created_job["salary_max"]) == float(job_data["salary_max"])
            if "is_remote" in created_job:
                assert created_job["is_remote"] == job_data["is_remote"]
            if "remote_only" in created_job:
                assert created_job["remote_only"] == job_data["remote_only"]

        except Exception as e:
            print(f"\nError occurred during job creation: {str(e)}")
            raise
        finally:
            if created_job_id:
                try:
                    print(f"\nCleaning up - deleting job {created_job_id}")
                    delete_response = client.jobs.delete(job_id=created_job_id)
                    assert delete_response.get("success") is True
                    print("Test job deleted successfully")
                except Exception as e:
                    print(f"Warning: Job cleanup failed: {str(e)}")

                try:
                    print(f"\nCleaning up - deleting company {company_id}")
                    client.companies.delete(company_id)
                    print("Test company deleted successfully")
                except Exception as e:
                    print(f"Warning: Company cleanup failed: {str(e)}")

    @pytest.mark.integration
    def test_list_jobs(self, client):
        """Fetch and inspect jobs response structure"""
        try:
            jobs = client.jobs.list()
            print("\nJobs Response Structure:")
            pprint(jobs[:2] if jobs else "Empty response")
            assert isinstance(jobs, list)

            if jobs:
                print("\nFirst Job Fields:")
                pprint(list(jobs[0].keys()))
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

    @pytest.mark.integration
    def test_get_job(self, client):
        """Fetch and inspect a single job's response structure"""
        try:
            jobs = client.jobs.list()
            if not jobs:
                pytest.skip("No jobs available to test with")

            job_id = jobs[0]["id"]
            job = client.jobs.get(job_id=job_id)

            print("\nSingle Job Response Structure:")
            pprint(job)
            assert isinstance(job, dict)
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

    @pytest.mark.integration
    @pytest.mark.destructive
    def test_update_job(self, client):
        """Create a job, update it, verify changes, then clean up"""
        created_job_id = None
        try:
            print("\nFetching valid job types...")
            job_types = client.job_types.list()
            if not job_types:
                pytest.skip("No job types available - cannot test job creation")
            jobtype_id = job_types[0]["id"]

            # First create a test company
            company_data = {
                "name": "Test Company for Job Update",
                "site_url": "https://example.com",
                "description": "<p>Test company for job update test</p>",
                "tagline": "Testing job updates",
            }
            company_response = client.companies.create(**company_data)
            company_id = company_response["results"]["company"]["id"]

            # Create initial job
            initial_job_data = {
                "title": "Initial Software Engineer",
                "company_id": company_id,
                "jobtype_id": jobtype_id,
                "description_html": "<p>Initial job description</p>",
                "apply_by_form": True,
            }

            response = client.jobs.create(**initial_job_data)

            print("\nCreate Job Response Structure:")
            pprint(response)

            created_job = response["job"]
            created_job_id = created_job["id"]

            print(f"\ncreated_job: {created_job} created_job_id {created_job_id}")

            job = client.jobs.get(job_id=created_job_id)
            job = get_job_with_retry(client, created_job_id)

            print("\nSingle Job Response Structure:")
            pprint(job)

            # Update job data
            update_data = {
                "title": "Updated Software Engineer",
                "description_html": "<p>Updated job description</p>",
                "salary_currency": "100k to 200k",
            }

            update_response = client.jobs.update(job_id=created_job_id, **update_data)

            print("\nUpdated job with data:")
            pprint(update_response)

            updated_job = update_response["job"]

            # Verify updates
            assert updated_job["title"] == update_data["title"]
            assert updated_job["description_html"] == update_data["description_html"]
            assert (
                updated_job["salary_currency"].lower()
                == update_data["salary_currency"].lower()
            )

        except Exception as e:
            print(f"\nError occurred during job update: {str(e)}")
            raise
        finally:
            # Clean up: Delete the test job and company
            if created_job_id:
                try:
                    print(f"\nCleaning up - deleting job {created_job_id}")
                    client.jobs.delete(job_id=created_job_id)
                    print("Test job deleted successfully")

                    print(f"\nCleaning up - deleting company {company_id}")
                    client.companies.delete(company_id)
                    print("Test company deleted successfully")
                except Exception as e:
                    print(f"Warning: Cleanup failed: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.destructive
    def test_delete_job(self, client):
        """Test deletion of a job"""
        try:
            print("\nFetching valid job types...")
            job_types = client.job_types.list()
            if not job_types:
                pytest.skip("No job types available - cannot test job creation")
            jobtype_id = job_types[0]["id"]

            # Create a test company and job for deletion
            company_response = client.companies.create(
                name="Test Company for Job Deletion",
                site_url="https://example.com",
                description="<p>Test company for job deletion</p>",
                tagline="Testing job deletion",
            )
            company_id = company_response["results"]["company"]["id"]

            job_response = client.jobs.create(
                title="Job to Delete",
                company_id=company_id,
                jobtype_id=jobtype_id,
                apply_by_form=True,
                description_html="<p>Job that will be deleted</p>",
            )

            print("\nCreate Job Response Structure:")
            pprint(job_response)

            job_id = job_response["job"]["id"]

            # Delete the job
            print(f"\nAttempting to delete job {job_id}")
            delete_response = client.jobs.delete(job_id=job_id)

            print("\nDelete Job Response Structure:")
            pprint(delete_response)

            assert delete_response["results"]["deleted"] is True
            print("Delete operation completed successfully")

            # Clean up the test company
            client.companies.delete(company_id)

        except Exception as e:
            print(f"\nError occurred during deletion test: {str(e)}")
            raise
