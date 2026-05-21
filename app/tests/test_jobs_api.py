def test_create_job_for_current_user(client, auth_headers):
    headers = auth_headers(name="job_owner")

    response = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "title": "Backend Developer",
            "company": "Acme",
            "status": "applied",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Backend Developer"
    assert response.json()["company"] == "Acme"
    assert response.json()["user_id"] == 1


def test_create_job_without_token_errors(client):
    response = client.post(
        "/api/v1/jobs",
        json={
            "title": "Backend Developer",
            "company": "Acme",
            "status": "applied",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_list_jobs_only_returns_current_users_jobs(client, auth_headers):
    first_headers = auth_headers(name="first_job_owner")
    second_headers = auth_headers(name="second_job_owner")

    client.post(
        "/api/v1/jobs",
        headers=first_headers,
        json={"title": "First Job", "company": "Acme"},
    )
    client.post(
        "/api/v1/jobs",
        headers=second_headers,
        json={"title": "Second Job", "company": "Beta"},
    )

    response = client.get("/api/v1/jobs", headers=first_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "First Job"


def test_get_update_and_delete_own_job(client, auth_headers):
    headers = auth_headers(name="job_crud_owner")
    created_job = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={"title": "Original Title", "company": "Acme"},
    ).json()

    get_response = client.get(f"/api/v1/jobs/{created_job['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Original Title"

    update_response = client.put(
        f"/api/v1/jobs/{created_job['id']}",
        headers=headers,
        json={"title": "Updated Title", "status": "interviewing"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"
    assert update_response.json()["status"] == "interviewing"

    delete_response = client.delete(f"/api/v1/jobs/{created_job['id']}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Job deleted successfully"

    missing_response = client.get(f"/api/v1/jobs/{created_job['id']}", headers=headers)
    assert missing_response.status_code == 404


def test_user_cannot_access_another_users_job(client, auth_headers):
    first_headers = auth_headers(name="job_owner_one")
    second_headers = auth_headers(name="job_owner_two")
    created_job = client.post(
        "/api/v1/jobs",
        headers=first_headers,
        json={"title": "Private Job", "company": "Acme"},
    ).json()

    get_response = client.get(f"/api/v1/jobs/{created_job['id']}", headers=second_headers)
    update_response = client.put(
        f"/api/v1/jobs/{created_job['id']}",
        headers=second_headers,
        json={"title": "Wrong User Edit"},
    )
    delete_response = client.delete(
        f"/api/v1/jobs/{created_job['id']}",
        headers=second_headers,
    )

    assert get_response.status_code == 404
    assert update_response.status_code == 404
    assert delete_response.status_code == 404
