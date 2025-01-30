# tests/test_companies.py
import pytest
from niceboard.resources import Companies


class TestCompanies:
    def test_list_companies(self, mock_client, mock_session):
        mock_session.return_value.get.return_value.json.return_value = {
            "error": False,
            "results": {
                "total_count": 1,
                "companies": [
                    {
                        "id": 1,
                        "name": "Test Company",
                        "slug": "test-company",
                        "email": None,
                        "logo_url": None,
                        "site_url": "https://example.com",
                        "is_verified": False,
                        "is_approved": True,
                        "is_published": True,
                    }
                ],
            },
        }

        companies = mock_client.companies.list()
        assert len(companies) == 1
        assert companies[0]["name"] == "Test Company"

    def test_get_company(self, mock_client, mock_session):
        company_id = 1
        mock_session.return_value.get.return_value.json.return_value = {
            "error": False,
            "results": {
                "company": {
                    "id": company_id,
                    "name": "Test Company",
                    "slug": "test-company",
                    "email": None,
                    "logo_url": None,
                    "site_url": "https://example.com",
                    "is_verified": False,
                    "is_approved": True,
                    "is_published": True,
                }
            },
        }

        company = mock_client.companies.get(company_id)
        assert company["id"] == company_id
        assert company["name"] == "Test Company"

    def test_create_company(self, mock_client, mock_session):
        company_data = {
            "name": "New Company",
            "site_url": "https://example.com",
            "description": "Test description",
        }

        mock_session.return_value.post.return_value.json.return_value = {
            "error": False,
            "results": {
                "company": {
                    "id": 1,
                    "name": "New Company",
                    "slug": "new-company",
                    "site_url": "https://example.com",
                    "description_html": "Test description",
                    "is_verified": False,
                    "is_approved": True,
                    "is_published": True,
                }
            },
        }

        created = mock_client.companies.create(**company_data)
        assert created["results"]["company"]["id"] == 1
        assert created["results"]["company"]["name"] == company_data["name"]
