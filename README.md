# Application Tracker API

Application Tracker API is a FastAPI backend for tracking job applications by user. It supports authenticated user accounts, user-owned job records, job status tracking, and a chatbot assistant integration that can answer natural-language questions about a user's applications.

The chatbot is designed to answer questions like:

- Which companies have I not heard back from yet?
- How many jobs have I applied to?
- How many times did I apply to a specific company or role?
- When was the last time I applied to a role?
- How long ago did I apply to a company?

The assistant should translate natural-language questions into structured query plans, then let the application execute safe queries.

## Features

- User signup and login
- JWT bearer-token authentication
- Password hashing before storage
- User-owned job records
- Create, read, update, and delete job applications
- Job status tracking
- Temporary SQLite test database setup
- API tests for auth, users, JWT behavior, and jobs
- Project context docs for future AI-assisted development

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Pytest
- JWT-style bearer authentication

## Project Structure

```text
app/
  api/
    dependencies.py
    v1/
      user.py
      job.py
  core/
    config.py
    security.py
    logging.py
  db/
    schema.py
  models/
    user.py
    job.py
  services/
    user_service.py
    job_service.py
  tests/
    conftest.py
    test_auth_login.py
    test_jwt_tokens.py
    test_user_crud.py
    test_jobs_api.py
Context/
  AI_CONTEXT.md
  ARCHITECTURE.md
  CONVENTIONS.md
Agent_Logs/
  AI_LOG.md
  DECISIONS.md
main.py
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

## Local Setup

Create a `.env` file in the project root:

```env
APP_NAME="My Application Tracker"
APP_VERSION="1.0.0"
DB_URL="sqlite:///./test.db"
SECRET_KEY="replace-this-with-a-long-random-secret"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Install dependencies in your Python environment. This project currently assumes FastAPI, SQLAlchemy, Pydantic, pydantic-settings, python-dotenv, and pytest are available.

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
  "location": "Remote",
  "date_applied": "2026-05-28",
  "job_url": "https://example.com/job"
}
```

## Chatbot Integration

The chatbot feature is intended to let users ask plain-English questions about their own job applications.

Examples:

```text
Which companies have I not heard back from yet?
How many jobs have I applied to?
How many times did I apply to backend roles?
When was the last time I applied to Acme?
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
- Update `Context/` and `Agent_Logs/` when making important architectural or AI-assisted changes.
