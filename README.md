# Niceboard API Client

A Python client for interacting with the Niceboard API.

[![LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/workflowing/niceboard/blob/main/LICENSE)
[![PyPi](https://img.shields.io/pypi/v/niceboard)](https://pypi.org/project/niceboard/)
[![GitHub](https://img.shields.io/badge/github-repo-blue.svg)](https://github.com/workflowing/niceboard)

## Installation

```bash
pip install niceboard
```

## Quickstart

```python
from niceboard import Client
from niceboard.services.search import NiceBoardSearchService

# Initialize the basic client
client = Client(api_key="your_api_key")

# Initialize the search service
search_service = NiceBoardSearchService(api_key="your_api_key")

# List all jobs
jobs = client.jobs.list()

# Search jobs with specific fields
job_results = search_service.search_jobs(
    fields=["title", "company", "location"],
    display="all"
)

# Search companies
company_results = search_service.search_companies(
    fields=["id", "name", "site_url"],
    display="all"
)
```

## Search Service Features

The search service provides advanced search capabilities with:

### Search Types

- Jobs (`search_jobs`)
- Companies (`search_companies`)
- Locations (`search_locations`)
- Categories (`search_categories`)
- Job Types (`search_jobtypes`)

### Filtering Options

- Remote jobs (`remote_ok`)
- Company filters
- Location filters
- Category filters
- Job type filters
- Pagination (`limit` and `page`)
- Keyword search (for companies)

## Tests

This project uses pytest for testing and includes both unit tests and integration tests.

### Test Types

- **Unit Tests**: Tests individual components in isolation using mocks
- **Integration Tests**: Tests actual API interactions
  - Safe tests: Read-only operations (listing, searching, and getting resources)
  - Each test category (jobs, companies, etc.) has dedicated test cases

### Environment Setup

Integration tests require:

- `NICEBOARD_API_KEY`: Required for authentication
- `NICEBOARD_BASE_URL`: Optional custom API URL

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only integration tests
pytest -v -m "integration"

# Run only non-integration tests (what CI will run)
pytest -v -k "not integration"

# Run with print statement output
pytest -v -s

# Run a specific test file
pytest tests/test_services_integration.py

# Run a specific test
pytest tests/test_services_integration.py::TestSearchService::test_search_jobs_basic
```

### Test Categories

| Category       | Description                               | Example Tests                     |
| -------------- | ----------------------------------------- | --------------------------------- |
| Job Search     | Tests job search functionality            | Basic search, filters, pagination |
| Company Search | Tests company search functionality        | Name search, ID search            |
| Display Modes  | Tests different result display options    | Summary, sample, all entries      |
| Error Handling | Tests invalid inputs and error conditions | Invalid fields, query types       |
| Pagination     | Tests result pagination                   | Page limits, result consistency   |

### CI/CD Testing Setup

Our CI pipeline is configured to:

1. Run all unit tests but skip integration tests
2. This is achieved using the `-k "not integration"` flag in pytest
3. Integration tests should only be run locally or in environments with proper API keys

### Helper Scripts

The repository includes helper scripts for testing:

```bash
# Check test coverage excluding integration tests
./scripts/check_coverage.sh

# Run only integration tests (requires API keys)
./scripts/run_integration_tests.sh
```

### Best Practices

1. Always run unit tests during development
2. Run integration tests before committing changes that affect API interaction
3. Use environment variables for configuration
4. Handle rate limits and API quotas appropriately
5. Use `-s` flag to see print outputs for debugging
6. Mark integration tests with `@pytest.mark.integration` decorator
7. Mark destructive tests with `@pytest.mark.destructive` decorator
