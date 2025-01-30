# Niceboard API Client

A Python client for interacting with the Niceboard API.

## Installation

```bash
pip install niceboard
```

## Quickstart

from niceboard import Client

# Initialize the client

```python
client = Client(api_key="your_api_key")
```

# List all jobs

```python
jobs = client.jobs.list()
```

# Create a company

```python
company = client.companies.create(
  name="Example Corp",
  site_url="https://example.com",
  description="An awesome company"
)
```

# Create a job posting

```python
job = client.jobs.create(
  company_id=company["id"],
  jobtype_id=1,
  title="Senior Developer",
  description_html="<p>Join our team!</p>",
  location_id=client.locations.get_or_create("San Francisco, CA")
)
```

# Update a job

```python
updated_job = client.jobs.update(
  job_id=job["id"],
  title="Senior Software Developer"
)
```

## Tests

This project uses pytest for testing and includes both unit tests and integration tests.

### Test Types

- **Unit Tests**: Tests individual components in isolation using mocks
- **Integration Tests**: Tests actual API interactions
  - Safe tests: Read-only operations (listing and getting resources)
  - Destructive tests: Write operations (create, update, delete)

### Running Tests

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run only integration tests that are safe (non-destructive):

```bash
pytest -v -m "integration and not destructive"
```

Run all integration tests including destructive operations:

```bash
pytest -v -m "integration and destructive"
```

Run with print statement output:

```bash
pytest -v -s
```

Run a specific test file:

```bash
pytest tests/test_integration.py
```

Run a specific test:

```bash
pytest tests/test_integration.py::TestIntegration::test_list_companies
```

### Test Configuration

Integration tests require:

- A valid API key set in the `NICEBOARD_API_KEY` environment variable
- Optionally, a custom API URL in `NICEBOARD_BASE_URL`

### Test Categories

| Category                | Description                             | When to Run                     |
| ----------------------- | --------------------------------------- | ------------------------------- |
| Unit Tests              | Tests individual components with mocks  | During development              |
| Safe Integration        | Tests read operations against live API  | During development              |
| Destructive Integration | Tests write operations against live API | When testing data modifications |

### Best Practices

1. Always run unit tests during development
2. Run safe integration tests before committing
3. Run destructive tests in a controlled environment
4. Use `-s` flag to see print outputs for debugging
