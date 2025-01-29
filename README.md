# Niceboard API Client

A Python client for interacting with the Niceboard API.

## Installation

```bash
pip install niceboard
```

## Quickstart

from niceboard import Client

# Initialize the client

client = Client(api_key="your_api_key")

# List all jobs

jobs = client.jobs.list()

# Create a company

company = client.companies.create(
name="Example Corp",
site_url="https://example.com",
description="An awesome company"
)

# Create a job posting

job = client.jobs.create(
company_id=company["id"],
jobtype_id=1,
title="Senior Developer",
description_html="<p>Join our team!</p>",
location_id=client.locations.get_or_create("San Francisco, CA")
)

# Update a job

updated_job = client.jobs.update(
job_id=job["id"],
title="Senior Software Developer"
)
