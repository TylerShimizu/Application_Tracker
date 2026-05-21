def test_login_with_valid_credentials_returns_token(client, create_user):
    create_user(name="login_user")

    response = client.post(
        "/api/v1/login",
        json={"name": "login_user", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_errors(client, create_user):
    create_user(name="wrong_password_user")

    response = client.post(
        "/api/v1/login",
        json={"name": "wrong_password_user", "password": "wrongpass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_with_old_username_after_update_errors(client, create_user):
    created_user = create_user(name="old_login_name").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "old_login_name", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=headers,
        json={"name": "new_login_name"},
    )

    response = client.post(
        "/api/v1/login",
        json={"name": "old_login_name", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_with_new_username_after_update_works(client, create_user):
    created_user = create_user(name="before_update").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "before_update", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=headers,
        json={"name": "after_update"},
    )

    response = client.post(
        "/api/v1/login",
        json={"name": "after_update", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_create_user_with_previous_username_after_rename(client, create_user):
    created_user = create_user(name="reusable_name").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "reusable_name", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=headers,
        json={"name": "renamed_user"},
    )

    response = client.post(
        "/api/v1/users",
        json={"name": "reusable_name", "password": "newpassword123"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "reusable_name"


def test_invalid_signup_inputs_error(client):
    invalid_payloads = [
        {"name": "   ", "password": "password123"},
        {"name": "../secret", "password": "password123"},
        {"name": "valid_user", "password": "   "},
        {"name": "valid_user", "password": "short"},
    ]

    for payload in invalid_payloads:
        response = client.post("/api/v1/users", json=payload)
        assert response.status_code == 422
