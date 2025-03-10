from unittest.mock import Mock

import pytest

from niceboard.resources import Companies


class TestCompanies:
    def test_list_companies(self, mock_client, mock_session):
        response_data = {
            "error": False,
            "results": {
                "companies": [
                    {
                        "id": 1,
                        "name": "Test Company",
                        "slug": "test-company",
                        "anonymity_enabled": False,
                        "contact_name": None,
                        "created_at": "2024-03-13T08:18:55.574Z",
                        "custom_fields": {},
                        "description_html": None,
                        "email": None,
                        "logo_url": None,
                        "site_url": "https://example.com",
                        "is_verified": False,
                        "facebook_url": None,
                        "google_user_id": None,
                        "id": 298086,
                        "is_approved": True,
                        "is_member": False,
                        "is_published": True,
                        "is_verified": False,
                        "linkedin_url": None,
                        "linkedin_user_id": None,
                        "logo_url": "https://cdn.niceboard.co/boards/auditfriendly1/companies/tesla-BLrRiudKvUP.png",
                        "name": "Tesla",
                        "site_url": "https://www.tesla.com",
                        "slug": "tesla",
                        "sso_profile_id": None,
                        "sso_raw_attributes": None,
                        "tagline": None,
                        "tax_id": None,
                        "twitter_handle": None,
                        "uid": "wDKvAcJCbdc",
                        "updated_at": "2024-03-14T06:59:57.053Z",
                    }
                ]
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        companies = mock_client.companies.list()

        assert len(companies) == 1
        assert companies[0]["name"] == "Tesla"
        assert "anonymity_enabled" in companies[0]
        assert "uid" in companies[0]
        assert isinstance(companies[0]["custom_fields"], dict)

    def test_get_company(self, mock_client, mock_session):
        response_data = {
            "error": False,
            "results": {
                "company": {
                    "id": 1,
                    "name": "Test Company",
                    "slug": "test-company",
                    "anonymity_enabled": False,
                    "contact_name": None,
                    "created_at": "2024-03-13T08:18:55.574Z",
                    "custom_fields": {},
                    "description_html": None,
                    "email": None,
                    "logo_url": None,
                    "site_url": "https://example.com",
                    "is_verified": False,
                    "facebook_url": None,
                    "google_user_id": None,
                    "id": 298086,
                    "is_approved": True,
                    "is_member": False,
                    "is_published": True,
                    "is_verified": False,
                    "linkedin_url": None,
                    "linkedin_user_id": None,
                    "logo_small_url": "https://s3.amazonaws.com/static.niceboard.co/boards/auditfriendly1/companies/tesla-BLrRiudKvUP-s.png",
                    "logo_url": "https://s3.amazonaws.com/static.niceboard.co/boards/auditfriendly1/companies/tesla-BLrRiudKvUP.png",
                    "name": "Tesla",
                    "password": None,
                    "reset_password_uid": None,
                    "site_url": "https://www.tesla.com",
                    "slug": "tesla",
                    "sso_profile_id": None,
                    "sso_raw_attributes": None,
                    "stripe_customer_id": None,
                    "tagline": None,
                    "tax_id": None,
                    "twitter_handle": None,
                    "uid": "wDKvAcJCbdc",
                    "updated_at": "2024-03-14T06:59:57.053Z",
                }
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        # Execute test
        company = mock_client.companies.get(298086)

        # Assertions
        assert company["id"] == 298086
        assert company["name"] == "Tesla"
        assert "logo_small_url" in company
        assert "stripe_customer_id" in company
        assert isinstance(company["custom_fields"], dict)

    def test_create_company(self, mock_client, mock_session):
        # Test input data
        company_data = {
            "name": "Test Company Integration",
            "site_url": "https://example.com",
            "description": "<p>Test company created by integration tests</p>",
            "tagline": "Testing company creation",
            "custom_fields": [{"id": "test-field", "value": "test-value"}],
        }

        # Full response data
        response_data = {
            "success": True,
            "results": {
                "company": {
                    "anonymity_enabled": False,
                    "contact_name": None,
                    "created_at": "2025-01-30T00:52:54.397Z",
                    "custom_fields": None,
                    "description_html": "<p>Test company created by integration tests</p>",
                    "email": None,
                    "facebook_url": None,
                    "google_user_id": None,
                    "id": 355242,
                    "is_approved": True,
                    "is_member": False,
                    "is_published": True,
                    "is_verified": False,
                    "jobboard_id": 3297,
                    "last_indexed_at": None,
                    "linkedin_url": None,
                    "linkedin_user_id": None,
                    "logo_small_url": None,
                    "logo_url": None,
                    "name": "Test Company Integration",
                    "password": None,
                    "reset_password_uid": None,
                    "site_url": "https://example.com",
                    "slug": "test-company-integration",
                    "sso_profile_id": None,
                    "sso_raw_attributes": None,
                    "stripe_customer_id": None,
                    "tagline": "Testing company creation",
                    "tax_id": None,
                    "twitter_handle": None,
                    "uid": "0NKJCWoUInW",
                    "updated_at": "2025-01-30T00:52:54.397Z",
                }
            },
        }

        mock_session.return_value.request.return_value.json.return_value = response_data

        created = mock_client.companies.create(**company_data)

        assert created["success"] is True
        assert created["results"]["company"]["id"] == 355242
        assert created["results"]["company"]["name"] == company_data["name"]
        assert created["results"]["company"]["tagline"] == company_data["tagline"]
        assert (
            created["results"]["company"]["description_html"]
            == company_data["description"]
        )
        assert "jobboard_id" in created["results"]["company"]
        assert "last_indexed_at" in created["results"]["company"]

    def test_delete_company(self, mock_client, mock_session):
        response_data = {"error": False, "results": {"deleted": True}}

        mock_session.return_value.request.return_value.json.return_value = response_data

        response = mock_client.companies.delete(355242)

        assert response["error"] is False
        assert response["results"]["deleted"] is True
