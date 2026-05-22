import json
from datetime import datetime, timezone

from app.core.security import _base64url_encode, _encode_jwt


def test_get_current_user_with_valid_token(client, auth_headers):
    headers = auth_headers(name="current_user")

    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "current_user"
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


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


def test_jwt_with_changed_payload_but_old_signature_errors(client, auth_headers):
    headers = auth_headers(name="payload_user")
    token = headers["Authorization"].replace("Bearer ", "")
    header_text, _payload_text, signature = token.split(".")
    changed_payload_text = _base64url_encode(
        json.dumps({"sub": "999", "exp": 9999999999}, separators=(",", ":")).encode()
    )
    changed_token = f"{header_text}.{changed_payload_text}.{signature}"

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {changed_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_jwt_missing_parts_errors(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer only-two.parts"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_jwt_with_missing_subject_errors(client):
    token = _encode_jwt(
        {
            "exp": int(datetime.now(timezone.utc).timestamp()) + 60,
        }
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_jwt_with_non_numeric_subject_errors(client):
    token = _encode_jwt(
        {
            "sub": "not-a-number",
            "exp": int(datetime.now(timezone.utc).timestamp()) + 60,
        }
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_jwt_with_missing_expiration_errors(client):
    token = _encode_jwt({"sub": "1"})

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_jwt_for_nonexistent_user_errors(client):
    token = _encode_jwt(
        {
            "sub": "999",
            "exp": int(datetime.now(timezone.utc).timestamp()) + 60,
        }
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
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


def test_token_for_one_user_cannot_delete_another_user(client, create_user):
    create_user(name="delete_first_user")
    second_user = create_user(name="delete_second_user").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "delete_first_user", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.delete(f"/api/v1/users/{second_user['id']}", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this user"


def test_old_token_still_works_after_username_change(client, create_user):
    created_user = create_user(name="old_token_name").json()
    login = client.post(
        "/api/v1/login",
        json={"name": "old_token_name", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.put(
        f"/api/v1/users/{created_user['id']}",
        headers=headers,
        json={"name": "new_token_name"},
    )
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "new_token_name"
