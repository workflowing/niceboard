# Niceboard API Client

A Python client for interacting with the Niceboard API.

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

### Display Modes

- `summary`: Returns statistics only
- `show_n`: Returns statistics and a sample of entries
- `all`: Returns statistics and all entries

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

### Field Selection

Supports nested field selection using dot notation (e.g., 'company.name', 'location.slug')

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

### Best Practices

1. Always run unit tests during development
2. Run integration tests before committing changes
3. Use environment variables for configuration
4. Handle rate limits and API quotas appropriately
5. Use `-s` flag to see print outputs for debugging
