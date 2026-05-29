# Application Tracker API

Application Tracker API is a FastAPI backend for tracking job applications by user. It supports authenticated accounts, user-owned job records, status tracking, application source/notes, and a chatbot-style assistant endpoint for natural-language questions about a user's applications.

The assistant can answer questions like:

- Which companies have I not heard back from yet?
- How many jobs have I applied to?
- How many times did I apply to a specific company or role?
- When was the last time I applied to a role?
- How long ago did I apply to a company?

The assistant translates natural-language questions into structured query plans, then the application executes safe SQLAlchemy queries scoped to the authenticated user. It does not generate or execute raw SQL.

## Features

- User signup and login
- JWT bearer-token authentication
- Password hashing before storage
- User-owned job records
- Create, read, update, and delete job applications
- Job status, source, notes, date, location, and URL tracking
- Assistant endpoint for status, frequency, source, company, role, and recency questions
- Temporary SQLite test database setup
- API tests for auth, users, JWT behavior, jobs, and assistant queries

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Pytest
- JWT-style bearer authentication
- Optional OpenAI API integration for assistant query planning

## Project Structure

```text
.
├── .env.example
├── .gitignore
├── README.md
├── main.py
└── app/
    ├── api/
    │   ├── dependencies.py
    │   └── v1/
    │       ├── assistant.py
    │       ├── job.py
    │       └── user.py
    ├── core/
    │   ├── config.py
    │   ├── logging.py
    │   └── security.py
    ├── db/
    │   └── schema.py
    ├── models/
    │   ├── assistant.py
    │   ├── job.py
    │   └── user.py
    ├── services/
    │   ├── assistant_service.py
    │   ├── job_service.py
    │   └── user_service.py
    └── tests/
        ├── conftest.py
        ├── test_assistant_api.py
        ├── test_auth_login.py
        ├── test_jobs_api.py
        ├── test_jwt_tokens.py
        └── test_user_crud.py
```

## API Overview

### Users

```text
POST   /api/v1/users
POST   /api/v1/login
GET    /api/v1/users/me
GET    /api/v1/users/{user_id}
PUT    /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}
```

Protected user update and delete routes require a bearer token. Users can only update or delete their own account.

### Jobs

```text
GET    /api/v1/jobs
POST   /api/v1/jobs
GET    /api/v1/jobs/{job_id}
PUT    /api/v1/jobs/{job_id}
DELETE /api/v1/jobs/{job_id}
```

Job routes are scoped to the authenticated user. A user cannot access another user's jobs by guessing a job ID.

Current job statuses:

```text
applied
interviewing
offered
rejected
interested
```

Current job sources:

```text
linkedin
indeed
company_site
referral
recruiter
other
```

### Assistant

```text
POST /api/v1/assistant/query
```

Assistant queries require authentication and only return data for the current user.

Supported assistant intents include:

```text
list_jobs
count_jobs
list_companies
last_application
days_since_last_application
```

## Local Setup

Create a `.env` file in the project root using `.env.example` as the starting point:

```env
APP_NAME="My Application Tracker"
APP_VERSION="1.0.0"
DB_URL="sqlite:///./test.db"
SECRET_KEY="replace-this-with-a-long-random-secret"
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=""
OPENAI_MODEL="gpt-4o-mini"
```

Install dependencies in your Python environment. This project currently assumes FastAPI, SQLAlchemy, Pydantic, pydantic-settings, python-dotenv, pytest, and uvicorn are available. The `openai` package is only needed when using OpenAI-backed assistant planning.

Run the API:

```bash
uvicorn main:app --reload
```

Open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Example Flow

Create a user:

```json
{
  "name": "tyler",
  "password": "password123"
}
```

Log in:

```json
{
  "name": "tyler",
  "password": "password123"
}
```

Use the returned token on protected routes:

```text
Authorization: Bearer <access_token>
```

Create a job:

```json
{
  "title": "Backend Developer",
  "company": "Acme",
  "status": "applied",
  "source": "linkedin",
  "location": "Remote",
  "date_applied": "2026-05-29",
  "job_url": "https://example.com/job",
  "notes": "Talked about the company mission during the interview."
}
```

Ask the assistant:

```json
{
  "message": "Which companies have I not heard back from yet?"
}
```

## Chatbot Integration

The chatbot feature lets users ask plain-English questions about their own job applications.

Examples:

```text
Which companies have I not heard back from yet?
How many jobs have I applied to?
How many times did I apply to backend roles?
When was the last time I applied to Acme?
How long ago did I apply to Acme?
List jobs from LinkedIn.
```

The safe design is:

```text
natural language question
-> structured assistant plan
-> SQLAlchemy service query
-> authenticated user's results
```

The assistant should only return structured intent and filters, such as:

```json
{
  "intent": "list_companies",
  "filters": {
    "status": "applied"
  }
}
```

Application code is responsible for executing database queries and enforcing user ownership.

If `OPENAI_API_KEY` is configured, the assistant uses OpenAI-backed structured planning. If no API key is configured, the service falls back to a small rule-based planner for supported local queries.

## Testing

Run the test suite:

```bash
pytest app/tests
```

Tests use temporary SQLite databases and override the app database dependency, so test data does not pollute the local development database.

## Development Notes

- Keep route handlers thin.
- Keep database logic in service classes.
- Keep user-owned data scoped by `current_user.id`.
- Do not return passwords or password hashes from API responses.
- Do not let AI-generated text execute raw database queries.
- Do not commit files ignored by `.gitignore`, including `.env`, caches, local databases, `Context/`, and `Agent_Logs/`.
