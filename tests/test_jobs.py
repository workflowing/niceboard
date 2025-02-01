import pytest
from unittest.mock import Mock


class TestJobs:
    def test_list_jobs(self, mock_client, mock_session):
        response_data = {
            "error": False,
            "results": {
                "jobs": [
                    {
                        "id": 1651824,
                        "title": "VP of Finance - Controls & FinOps",
                        "apply_by_form": False,
                        "apply_email": None,
                        "apply_url": "https://jobs.lever.co/hopper/0cc8a635-e6ba-4bc9-85aa-7bfbb6a6210b/apply",
                        "category": {
                            "id": 39010,
                            "name": "Finance Leadership",
                            "secondary_lang_name": None,
                            "slug": "finance-leadership",
                        },
                        "company": {
                            "id": 303842,
                            "name": "Hopper",
                            "logo_url": "https://s3.amazonaws.com/static.niceboard.co/boards/auditfriendly1/companies/hopper-OT0_xWbwH7Aj.png",
                            "logo_small_url": "https://s3.amazonaws.com/static.niceboard.co/boards/auditfriendly1/companies/hopper-OT0_xWbwH7Aj-s.png",
                            "is_approved": True,
                            "is_published": True,
                        },
                        "created_at": "2025-01-16T02:27:01.739Z",
                        "custom_fields": {},
                        "expires_on": "2025-02-15T02:27:01.734Z",
                        "is_featured": False,
                        "is_filled": False,
                        "is_published": True,
                        "is_remote": False,
                        "location_name": "Greater Toronto Area, Canada",
                        "uid": "q7iNiue4IV",
                        "updated_at": "2025-01-16T02:27:01.739Z",
                    }
                ]
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        jobs = mock_client.jobs.list()

        assert len(jobs) == 1
        assert jobs[0]["id"] == 1651824
        assert jobs[0]["title"] == "VP of Finance - Controls & FinOps"
        assert jobs[0]["company"]["name"] == "Hopper"
        assert "location_name" in jobs[0]
        assert "uid" in jobs[0]
        assert isinstance(jobs[0]["custom_fields"], dict)
        assert "category" in jobs[0]
        assert jobs[0]["category"]["name"] == "Finance Leadership"

    def test_create_job(self, mock_client, mock_session):
        job_data = {
            "title": "Job to Delete",
            "description_html": "<p>Job that will be deleted</p>",
            "company_id": 355565,
            "jobtype_id": 16388,
            "apply_by_form": True,
            "show_salary": True,
            "salary_timeframe": "annually",
        }

        response_data = {
            "success": True,
            "job": {
                "id": 1664341,
                "title": "Job to Delete",
                "description_html": "<p>Job that will be deleted</p>",
                "company_id": 355565,
                "jobtype_id": 16388,
                "apply_by_form": True,
                "apply_email": None,
                "apply_url": None,
                "is_draft": False,
                "is_featured": False,
                "is_filled": False,
                "is_published": True,
                "is_remote": False,
                "jobboard_id": 3297,
                "created_at": "2025-01-31T19:24:04.611Z",
                "updated_at": "2025-01-31T19:24:04.611Z",
                "expires_on": "2025-03-02T19:24:04.611Z",
                "published_at": "2025-01-31T19:24:04.611Z",
                "uid": "SbHHo8LQGo",
                "slug": "job-to-delete",
                "salary_timeframe": "annually",
                "show_salary": True,
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        created = mock_client.jobs.create(**job_data)

        assert created["success"] is True
        assert created["job"]["id"] == 1664341
        assert created["job"]["title"] == job_data["title"]
        assert created["job"]["description_html"] == job_data["description_html"]
        assert created["job"]["company_id"] == job_data["company_id"]
        assert created["job"]["jobtype_id"] == job_data["jobtype_id"]
        assert "uid" in created["job"]
        assert "slug" in created["job"]
        assert created["job"]["is_published"] is True

    def test_get_job(self, mock_client, mock_session):
        response_data = {
            "error": False,
            "results": {
                "job": {
                    "id": 1651824,
                    "title": "VP of Finance - Controls & FinOps",
                    "apply_by_form": False,
                    "apply_email": None,
                    "apply_url": "https://jobs.lever.co/hopper/0cc8a635-e6ba-4bc9-85aa-7bfbb6a6210b/apply",
                    "category": {
                        "id": 39010,
                        "name": "Finance Leadership",
                        "secondary_lang_name": None,
                        "slug": "finance-leadership",
                    },
                    "company": {
                        "id": 303842,
                        "name": "Hopper",
                        "logo_url": "https://s3.amazonaws.com/static.niceboard.co/boards/auditfriendly1/companies/hopper-OT0_xWbwH7Aj.png",
                        "logo_small_url": "https://s3.amazonaws.com/static.niceboard.co/boards/auditfriendly1/companies/hopper-OT0_xWbwH7Aj-s.png",
                        "is_approved": True,
                        "is_published": True,
                        "is_verified": False,
                        "site_url": "http://hopper.com/",
                        "slug": "hopper",
                    },
                    "created_at": "2025-01-16T02:27:01.739Z",
                    "custom_fields": {},
                    "description_html": "<div><div><b>About the job</b></div>...",
                    "expires_on": "2025-02-15T02:27:01.734Z",
                    "location": {
                        "id": 109079,
                        "name": "Greater Toronto Area, Canada",
                        "city_long": "Toronto",
                        "country_long": "Canada",
                        "state_long": "Ontario",
                    },
                    "location_name": "Greater Toronto Area, Canada",
                    "jobtype": {"id": 16388, "name": "Full time", "slug": "full-time"},
                    "is_featured": False,
                    "is_filled": False,
                    "is_published": True,
                    "is_remote": False,
                    "published_at": "2025-01-31T00:04:16.085Z",
                    "salary_timeframe": "annually",
                    "slug": "vp-of-finance-controls-and-finops",
                    "uid": "q7iNiue4IV",
                    "updated_at": "2025-01-16T02:27:01.739Z",
                },
                "total_count": 1,
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        # Execute test
        job = mock_client.jobs.get(job_id=1651824)

        # Assertions
        assert job["error"] is False
        assert job["results"]["job"]["id"] == 1651824
        assert job["results"]["job"]["title"] == "VP of Finance - Controls & FinOps"
        assert job["results"]["job"]["company"]["name"] == "Hopper"
        assert job["results"]["job"]["location_name"] == "Greater Toronto Area, Canada"
        assert job["results"]["job"]["jobtype"]["name"] == "Full time"
        assert job["results"]["job"]["uid"] == "q7iNiue4IV"
        assert isinstance(job["results"]["job"]["custom_fields"], dict)
        assert job["results"]["total_count"] == 1

    def test_delete_job(self, mock_client, mock_session):
        response_data = {"error": False, "results": {"deleted": True}}

        mock_session.return_value.request.return_value.json.return_value = response_data

        # Execute test
        response = mock_client.jobs.delete(job_id=1651824)

        assert response["error"] is False
        assert response["results"]["deleted"] is True

    def test_update_job(self, mock_client, mock_session):
        job_data = {
            "title": "Updated Software Engineer",
            "description_html": "<p>Updated job description</p>",
            "jobtype_id": 16388,
            "apply_by_form": True,
            "show_salary": True,
            "salary_timeframe": "annually",
            "salary_currency": "100K TO 200K",
        }

        response_data = {
            "success": True,
            "job": {
                "id": 1664466,
                "title": "Updated Software Engineer",
                "description_html": "<p>Updated job description</p>",
                "company_id": 355591,
                "jobtype_id": 16388,
                "apply_by_form": True,
                "apply_email": None,
                "apply_url": None,
                "is_draft": False,
                "is_featured": False,
                "is_filled": False,
                "is_published": True,
                "is_remote": False,
                "jobboard_id": 3297,
                "created_at": "2025-02-01T00:01:16.152Z",
                "updated_at": "2025-02-01T00:01:16.152Z",
                "expires_on": "2025-03-03T00:01:16.151Z",
                "published_at": "2025-02-01T00:01:17.151Z",
                "uid": "i8cY4NDc9g",
                "slug": "updated-software-engineer",
                "salary_timeframe": "annually",
                "show_salary": True,
                "salary_currency": "100K TO 200K",
                "custom_fields": {},
                "location_name": None,
                "location_id": None,
                "category_id": None,
                "experience": None,
                "filled_at": None,
                "how_to_apply": None,
                "is_paid": False,
                "is_sample": False,
                "last_google_deindexed_at": None,
                "last_google_indexed_at": None,
                "last_indexed_at": "2025-02-01T00:01:16.392Z",
                "remote_only": False,
                "remote_required_location": None,
                "salary_description": None,
                "salary_max": None,
                "salary_min": None,
                "scheduled_at": None,
                "secondary_category_id": None,
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        updated = mock_client.jobs.update(job_id=1664466, **job_data)

        assert updated["success"] is True
        assert updated["job"]["id"] == 1664466
        assert updated["job"]["title"] == job_data["title"]
        assert updated["job"]["description_html"] == job_data["description_html"]
        assert updated["job"]["jobtype_id"] == job_data["jobtype_id"]
        assert updated["job"]["apply_by_form"] == job_data["apply_by_form"]
        assert updated["job"]["show_salary"] == job_data["show_salary"]
        assert updated["job"]["salary_timeframe"] == job_data["salary_timeframe"]
        assert updated["job"]["salary_currency"] == job_data["salary_currency"]
        assert "uid" in updated["job"]
        assert "slug" in updated["job"]
        assert updated["job"]["is_published"] is True
