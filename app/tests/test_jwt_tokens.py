from datetime import datetime, timezone

from app.core.security import _encode_jwt


def test_get_current_user_with_valid_token(client, auth_headers):
    headers = auth_headers(name="current_user")

    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "current_user"


def test_get_current_user_without_token_errors(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_manually_changed_jwt_token_errors(client, auth_headers):
    headers = auth_headers(name="token_user")
    token = headers["Authorization"].replace("Bearer ", "")
    bad_token = token[:-1] + ("x" if token[-1] != "x" else "y")

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {bad_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_expired_jwt_token_errors(client, create_user):
    create_user(name="expired_user")
    expired_token = _encode_jwt(
        {
            "sub": "1",
            "exp": int(datetime.now(timezone.utc).timestamp()) - 60,
        }
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_deleted_user_token_no_longer_works(client, create_user):
    created_user = create_user(name="delete_token_user").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "delete_token_user", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.delete(f"/api/v1/users/{created_user['id']}", headers=headers)
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_token_for_one_user_cannot_update_another_user(client, create_user):
    create_user(name="first_user")
    second_user = create_user(name="second_user").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "first_user", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.put(
        f"/api/v1/users/{second_user['id']}",
        headers=headers,
        json={"name": "changed_by_wrong_user"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this user"
