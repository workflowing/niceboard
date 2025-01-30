# Niceboard Private API Documentation

Use your own private API access to retrieve, insert and manipulate all data points in your job board.

## Credentials

**Base URL:** `https://jobs.auditfriendly.co/api/v1`
**Secret Key:** `et0a78VF3m`

## Available Routes

### GET /jobs

Retrieve a list of jobs based on specified filters.

#### Parameters

| Type  | Name               | Description                                                                           | Required |
| ----- | ------------------ | ------------------------------------------------------------------------------------- | -------- |
| QUERY | key                | Your secret key                                                                       | ✓        |
| QUERY | page               | A page number                                                                         | -        |
| QUERY | limit              | Max number of items to return (defaults to 30)                                        | -        |
| QUERY | jobtype            | Filter by jobtype slug (ex: full-time)                                                | -        |
| QUERY | company            | Filter by company slug (ex: apple)                                                    | -        |
| QUERY | category           | Filter by category slug (ex: design)                                                  | -        |
| QUERY | secondary_category | Filter by secondary_category slug (ex: finance)                                       | -        |
| QUERY | tags               | Filter by tags slug. Value must be a stringified array (ex: ["tag1", "tag2"] encoded) | -        |
| QUERY | location           | Filter by location slug (ex: newyork-city)                                            | -        |
| QUERY | remote_ok          | Only display remote friendly jobs                                                     | -        |
| QUERY | is_featured        | Only display featured jobs                                                            | -        |
| QUERY | keyword            | Filter by keyword                                                                     | -        |

### GET /jobs/{job_id}

Retrieve a single job object.

#### Parameters

| Type  | Name   | Description               | Required |
| ----- | ------ | ------------------------- | -------- |
| QUERY | key    | Your secret key           | ✓        |
| PARAM | job_id | The unique job identifier | ✓        |

### GET /jobseekers

Retrieve all jobseekers.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |
| PAGE  | key  | A page number   | -        |

### POST /jobs

Insert a new job into your board.

#### Parameters

| Type  | Name                     | Description                                            | Required |
| ----- | ------------------------ | ------------------------------------------------------ | -------- |
| QUERY | key                      | Your secret key                                        | ✓        |
| BODY  | company_id               | An existing company's unique identifier                | ✓        |
| BODY  | jobtype_id               | An existing job type's unique identifier               | ✓        |
| BODY  | category_id              | An existing job category's unique identifier           | -        |
| BODY  | secondary_category_id    | An existing job secondary category's unique identifier | -        |
| BODY  | location_id              | An existing location's unique identifier               | -        |
| BODY  | tags                     | A string of tags (format: "tag, tag2, tag3")           | -        |
| BODY  | title                    | Your new job's title                                   | ✓        |
| BODY  | apply_by_form            | Accept applications via native forms                   | ✓        |
| BODY  | apply_url                | URL to apply (required if apply_email omitted)         | -        |
| BODY  | apply_email              | Email for applications                                 | -        |
| BODY  | description_html         | Job description in HTML format                         | ✓        |
| BODY  | salary_min               | Minimum salary value                                   | -        |
| BODY  | salary_max               | Maximum salary value                                   | -        |
| BODY  | salary_timeframe         | Period ("annually", "monthly", "hourly", "weekly")     | -        |
| BODY  | salary_currency          | ISO 4217 currency code                                 | -        |
| BODY  | is_remote                | Remote-friendly job                                    | -        |
| BODY  | remote_only              | Remote-only position                                   | -        |
| BODY  | remote_required_location | Required remote region/timezone                        | -        |
| BODY  | is_featured              | Highlighted in job list                                | -        |
| BODY  | is_published             | Visible in job list                                    | -        |
| BODY  | published_at             | Publication timestamp                                  | -        |
| BODY  | expires_on               | Expiration date                                        | -        |
| BODY  | custom_fields            | JSON array of custom fields                            | -        |

### GET /companies

Retrieve a list of companies.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |

### GET /companies/{company_id}

Retrieve a single company object.

#### Parameters

| Type  | Name       | Description                   | Required |
| ----- | ---------- | ----------------------------- | -------- |
| QUERY | key        | Your secret key               | ✓        |
| PARAM | company_id | The unique company identifier | ✓        |

### GET /categories

Retrieve a list of your job categories.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |

### GET /categories/{category_id}

Retrieve a single job category object.

#### Parameters

| Type  | Name        | Description                    | Required |
| ----- | ----------- | ------------------------------ | -------- |
| QUERY | key         | Your secret key                | ✓        |
| PARAM | category_id | The unique category identifier | ✓        |

### GET /secondarycategories

Retrieve a list of your job secondary categories.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |

### GET /secondarycategories/{category_id}

Retrieve a single secondary category object.

#### Parameters

| Type  | Name        | Description                    | Required |
| ----- | ----------- | ------------------------------ | -------- |
| QUERY | key         | Your secret key                | ✓        |
| PARAM | category_id | The unique category identifier | ✓        |

### GET /locations

Retrieve a list of your job locations.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |

### GET /locations/{location_id}

Retrieve a single location object.

#### Parameters

| Type  | Name        | Description                    | Required |
| ----- | ----------- | ------------------------------ | -------- |
| QUERY | key         | Your secret key                | ✓        |
| PARAM | location_id | The unique location identifier | ✓        |

### GET /tags

Retrieve a list of your job tags.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |

### GET /tags/{tag_id}

Retrieve a single tag object.

#### Parameters

| Type  | Name   | Description               | Required |
| ----- | ------ | ------------------------- | -------- |
| QUERY | key    | Your secret key           | ✓        |
| PARAM | tag_id | The unique tag identifier | ✓        |

### GET /sales

Retrieve a list of the 100 newest sales.

#### Parameters

| Type  | Name | Description     | Required |
| ----- | ---- | --------------- | -------- |
| QUERY | key  | Your secret key | ✓        |

### GET /jobalerts

Retrieve a list of the newest email subscriptions.

#### Parameters

| Type  | Name         | Description                   | Required |
| ----- | ------------ | ----------------------------- | -------- |
| QUERY | key          | Your secret key               | ✓        |
| QUERY | subscribed   | Only show subscribed emails   | -        |
| QUERY | unsubscribed | Only show unsubscribed emails | -        |

### GET /applications

Retrieve a list of job applications/clicks.

#### Parameters

| Type  | Name       | Description                                                           | Required |
| ----- | ---------- | --------------------------------------------------------------------- | -------- |
| QUERY | key        | Your secret key                                                       | ✓        |
| QUERY | native     | Whether to retrieve native applications or clicks (defaults to false) | -        |
| QUERY | start_date | Start date for retrieving applications (defaults to 3 months)         | -        |
| QUERY | end_date   | End date for retrieving applications (defaults to today)              | -        |
| QUERY | job_id     | Filter applications by job ID                                         | -        |

### POST /companies

Insert a new company into your board.

#### Parameters

| Type  | Name           | Description                                         | Required |
| ----- | -------------- | --------------------------------------------------- | -------- |
| QUERY | key            | Your secret key                                     | ✓        |
| BODY  | name           | Your new company's name                             | ✓        |
| BODY  | site_url       | The url to the company's website                    | -        |
| BODY  | twitter_handle | The company's twitter handle                        | -        |
| BODY  | linkedin_url   | The company's LinkedIn profile url                  | -        |
| BODY  | facebook_url   | The company's Facebook profile url                  | -        |
| BODY  | tagline        | The company's tagline (255 chars max)               | -        |
| BODY  | description    | A long description for the company (HTML supported) | -        |
| BODY  | email          | An email for the company account                    | -        |
| BODY  | password       | A password for the company account                  | -        |
| BODY  | logo           | Logo for the company (base64 encoded)               | -        |
| BODY  | custom_fields  | JSON array of custom fields                         | -        |

### POST /companies/users

Create new company users for an existing company account.

#### Parameters

| Type  | Name       | Description                                     | Required |
| ----- | ---------- | ----------------------------------------------- | -------- |
| QUERY | key        | Your secret key                                 | ✓        |
| BODY  | company_id | An existing company account's unique identifier | ✓        |
| BODY  | name       | Company user name                               | ✓        |
| BODY  | email      | An email for the company user account           | ✓        |
| BODY  | password   | Password for the company user account           | -        |

### POST /jobseekers

Insert a new job seeker account into your board.

#### Parameters

| Type  | Name          | Description                                | Required |
| ----- | ------------- | ------------------------------------------ | -------- |
| QUERY | key           | Your secret key                            | ✓        |
| BODY  | first_name    | Job seeker's first name                    | ✓        |
| BODY  | last_name     | Job seeker's last name                     | ✓        |
| BODY  | email         | An email for the job seeker account        | ✓        |
| BODY  | password      | A password for the job seeker account      | ✓        |
| BODY  | summary       | Job seeker's short bio text                | -        |
| BODY  | address       | Job seeker's address line 1                | -        |
| BODY  | city          | Job seeker's address city                  | -        |
| BODY  | state         | Job seeker's address state                 | -        |
| BODY  | zipcode       | Job seeker's address postal code           | -        |
| BODY  | country       | Job seeker's address country               | -        |
| BODY  | phone_number  | Job seeker's phone number                  | -        |
| BODY  | linkedin_url  | Job seeker's LinkedIn profile url          | -        |
| BODY  | is_public     | Whether profile can be viewed by employers | -        |
| BODY  | remote_ok     | Whether job seeker is remote friendly      | -        |
| BODY  | custom_fields | JSON array of custom fields                | -        |

### POST /jobtypes

Insert a new job type into your board.

#### Parameters

| Type  | Name | Description              | Required |
| ----- | ---- | ------------------------ | -------- |
| QUERY | key  | Your secret key          | ✓        |
| BODY  | name | Your new job type's name | ✓        |

### POST /locations

Insert a new job location into your board.

#### Parameters

| Type  | Name | Description                  | Required |
| ----- | ---- | ---------------------------- | -------- |
| QUERY | key  | Your secret key              | ✓        |
| BODY  | name | Your new job location's name | ✓        |

### POST /categories

Insert a new job category into your board.

#### Parameters

| Type  | Name | Description                  | Required |
| ----- | ---- | ---------------------------- | -------- |
| QUERY | key  | Your secret key              | ✓        |
| BODY  | name | Your new job category's name | ✓        |

### POST /secondarycategories

Insert a new job secondary category into your board.

#### Parameters

| Type  | Name | Description                            | Required |
| ----- | ---- | -------------------------------------- | -------- |
| QUERY | key  | Your secret key                        | ✓        |
| BODY  | name | Your new job secondary category's name | ✓        |

### POST /tags

Insert a new job tag into your board.

#### Parameters

| Type  | Name | Description             | Required |
| ----- | ---- | ----------------------- | -------- |
| QUERY | key  | Your secret key         | ✓        |
| BODY  | name | Your new job tag's name | ✓        |

### POST /jobalerts

Insert a new job alert into your board.

#### Parameters

| Type  | Name        | Description                                  | Required |
| ----- | ----------- | -------------------------------------------- | -------- |
| QUERY | key         | Your secret key                              | ✓        |
| BODY  | email       | The email to subscribe to your job alert     | ✓        |
| BODY  | frequency   | Alert frequency ("weekly", "biweekly")       | -        |
| BODY  | jobtype_id  | An existing job type's unique identifier     | -        |
| BODY  | category_id | An existing job category's unique identifier | -        |
| BODY  | location_id | An existing location's unique identifier     | -        |

### Delete Operations

#### DELETE /jobs/{job_id}

Delete a single job object.

| Type  | Name   | Description               | Required |
| ----- | ------ | ------------------------- | -------- |
| QUERY | key    | Your secret key           | ✓        |
| PARAM | job_id | The unique job identifier | ✓        |

#### DELETE /companies/{company_id}

Delete a single company object and related jobs.

| Type  | Name       | Description                   | Required |
| ----- | ---------- | ----------------------------- | -------- |
| QUERY | key        | Your secret key               | ✓        |
| PARAM | company_id | The unique company identifier | ✓        |

#### DELETE /jobseekers/{jobseeker_id}

Delete a single job seeker object and related jobs.

| Type  | Name         | Description                      | Required |
| ----- | ------------ | -------------------------------- | -------- |
| QUERY | key          | Your secret key                  | ✓        |
| PARAM | jobseeker_id | The unique job seeker identifier | ✓        |
