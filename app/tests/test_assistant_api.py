from datetime import date, timedelta


def create_job(client, headers, title, company, status="applied", date_applied=None):
    payload = {
        "title": title,
        "company": company,
        "status": status,
    }
    if date_applied:
        payload["date_applied"] = date_applied.isoformat()

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
    assert response.json()["jobs"] == []


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
