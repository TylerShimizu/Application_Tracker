from datetime import date, timedelta


def create_job(
    client,
    headers,
    title,
    company,
    status="applied",
    date_applied=None,
    source=None,
):
    payload = {
        "title": title,
        "company": company,
        "status": status,
    }
    if date_applied:
        payload["date_applied"] = date_applied.isoformat()
    if source:
        payload["source"] = source

    return client.post("/api/v1/jobs", headers=headers, json=payload)


def test_assistant_query_requires_authentication(client):
    response = client.post(
        "/api/v1/assistant/query",
        json={"message": "Which companies have I not heard back from yet?"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_assistant_lists_companies_not_heard_back_from(client, auth_headers):
    headers = auth_headers(name="assistant_owner")
    create_job(client, headers, "Backend Developer", "Acme", status="applied")
    create_job(client, headers, "Frontend Developer", "Beta", status="interviewing")

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "Which companies have I not heard back from yet?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "list_companies"
    assert response.json()["filters"]["status"] == "applied"
    assert response.json()["companies"] == ["Acme"]
    assert response.json()["jobs"] == []
    assert response.json()["count"] == 1


def test_assistant_counts_applied_jobs(client, auth_headers):
    headers = auth_headers(name="assistant_counter")
    create_job(client, headers, "Backend Developer", "Acme", status="applied")
    create_job(client, headers, "Data Engineer", "Beta", status="applied")
    create_job(client, headers, "Designer", "Gamma", status="rejected")

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "How many jobs have I applied to?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "count_jobs"
    assert response.json()["filters"]["status"] == "applied"
    assert response.json()["count"] == 2
    assert len(response.json()["jobs"]) == 2


def test_assistant_counts_applications_to_company(client, auth_headers):
    headers = auth_headers(name="assistant_company_count")
    create_job(client, headers, "Backend Developer", "Acme", status="applied")
    create_job(client, headers, "Data Engineer", "Acme", status="rejected")
    create_job(client, headers, "Designer", "Beta", status="applied")

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "How many times did I apply to Acme?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "count_jobs"
    assert response.json()["filters"]["company"] == "acme"
    assert response.json()["count"] == 2
    assert {job["company"] for job in response.json()["jobs"]} == {"Acme"}


def test_assistant_counts_applications_to_role(client, auth_headers):
    headers = auth_headers(name="assistant_role_count")
    create_job(client, headers, "Backend Developer", "Acme", status="applied")
    create_job(client, headers, "Senior Backend Engineer", "Beta", status="applied")
    create_job(client, headers, "Designer", "Gamma", status="applied")

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "How many times did I apply to backend roles?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "count_jobs"
    assert response.json()["filters"]["title"] == "backend"
    assert response.json()["count"] == 2
    assert len(response.json()["jobs"]) == 2


def test_assistant_filters_by_company(client, auth_headers):
    headers = auth_headers(name="assistant_company")
    create_job(client, headers, "Backend Developer", "Acme", status="applied")
    create_job(client, headers, "Backend Developer", "Beta", status="applied")

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "List jobs from acme"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "list_jobs"
    assert response.json()["filters"]["company"] == "acme"
    assert response.json()["count"] == 1
    assert response.json()["jobs"][0]["company"] == "Acme"


def test_assistant_filters_by_source(client, auth_headers):
    headers = auth_headers(name="assistant_source")
    create_job(client, headers, "Backend Developer", "Acme", source="linkedin")
    create_job(client, headers, "Data Engineer", "Beta", source="indeed")

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "List jobs from LinkedIn"},
    )

    assert response.status_code == 200
    assert response.json()["filters"]["source"] == "linkedin"
    assert response.json()["count"] == 1
    assert response.json()["jobs"][0]["company"] == "Acme"


def test_assistant_returns_days_since_last_application(client, auth_headers):
    headers = auth_headers(name="assistant_how_long")
    today = date.today()
    create_job(
        client,
        headers,
        "Backend Developer",
        "Acme",
        date_applied=today - timedelta(days=10),
    )
    create_job(
        client,
        headers,
        "Data Engineer",
        "Acme",
        date_applied=today - timedelta(days=3),
    )

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "How long ago did I apply to Acme?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "days_since_last_application"
    assert response.json()["filters"]["company"] == "acme"
    assert response.json()["days_since_last_application"] == 3
    assert response.json()["last_application_date"] == (today - timedelta(days=3)).isoformat()
    assert len(response.json()["jobs"]) == 2


def test_assistant_returns_last_application_for_role(client, auth_headers):
    headers = auth_headers(name="assistant_last_role")
    today = date.today()
    create_job(
        client,
        headers,
        "Backend Developer",
        "Acme",
        date_applied=today - timedelta(days=30),
    )
    create_job(
        client,
        headers,
        "Senior Backend Engineer",
        "Beta",
        date_applied=today - timedelta(days=5),
    )
    create_job(
        client,
        headers,
        "Designer",
        "Gamma",
        date_applied=today - timedelta(days=1),
    )

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "When was the last time I applied to backend roles?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "last_application"
    assert response.json()["filters"]["title"] == "backend"
    assert response.json()["days_since_last_application"] == 5
    assert response.json()["last_application_date"] == (today - timedelta(days=5)).isoformat()


def test_assistant_filters_by_recent_applications(client, auth_headers):
    headers = auth_headers(name="assistant_recent")
    today = date.today()
    create_job(
        client,
        headers,
        "Recent Backend Developer",
        "Acme",
        status="applied",
        date_applied=today - timedelta(days=3),
    )
    create_job(
        client,
        headers,
        "Old Backend Developer",
        "Beta",
        status="applied",
        date_applied=today - timedelta(days=45),
    )

    response = client.post(
        "/api/v1/assistant/query",
        headers=headers,
        json={"message": "Companies I applied to in the last 30 days"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "list_companies"
    assert response.json()["filters"]["applied_within_days"] == 30
    assert response.json()["companies"] == ["Acme"]


def test_assistant_only_queries_current_users_jobs(client, auth_headers):
    first_headers = auth_headers(name="assistant_first")
    second_headers = auth_headers(name="assistant_second")
    create_job(client, first_headers, "Backend Developer", "Acme", status="applied")
    create_job(client, second_headers, "Backend Developer", "Beta", status="applied")

    response = client.post(
        "/api/v1/assistant/query",
        headers=first_headers,
        json={"message": "Which companies have I not heard back from yet?"},
    )

    assert response.status_code == 200
    assert response.json()["companies"] == ["Acme"]
    assert response.json()["count"] == 1
    assert "Beta" not in response.json()["companies"]
