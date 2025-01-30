# tests/test_integration.py
import pytest
from pprint import pprint


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
                "custom_fields": [{"id": "test-field", "value": "test-value"}],
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
