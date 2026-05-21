def test_create_user_returns_public_user_data(client):
    response = client.post(
        "/api/v1/users",
        json={"name": "tyler", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "tyler"
    assert "id" in response.json()
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


def test_create_user_that_already_exists_errors(client, create_user):
    create_user(name="duplicate_user")

    response = client.post(
        "/api/v1/users",
        json={"name": "duplicate_user", "password": "password123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_get_user_that_exists(client, create_user):
    created_user = create_user(name="get_user").json()

    response = client.get(f"/api/v1/users/{created_user['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_user["id"]
    assert response.json()["name"] == "get_user"


def test_get_user_that_does_not_exist_errors(client):
    response = client.get("/api/v1/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_own_username(client, create_user):
    created_user = create_user(name="old_name").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "old_name", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=headers,
        json={"name": "new_name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "new_name"


def test_update_user_that_does_not_exist_errors(client, auth_headers):
    headers = auth_headers(name="existing_user")

    response = client.put(
        "/api/v1/users/999",
        headers=headers,
        json={"name": "ghost_user"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this user"


def test_update_username_to_existing_name_errors(client, create_user):
    create_user(name="taken_name")
    second_user = create_user(name="second_user").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "second_user", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.put(
        f"/api/v1/users/{second_user['id']}",
        headers=headers,
        json={"name": "taken_name"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_delete_own_user(client, create_user):
    created_user = create_user(name="delete_me").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "delete_me", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.delete(f"/api/v1/users/{created_user['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully"


def test_delete_user_that_is_not_current_user_errors(client, create_user):
    create_user(name="current_user")
    other_user = create_user(name="other_user").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "current_user", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.delete(f"/api/v1/users/{other_user['id']}", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this user"
