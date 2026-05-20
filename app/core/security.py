import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import config


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, expected_hash = stored_password.split("$", 1)
    except ValueError:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": int(expires_at.timestamp()),
    }
    return _encode_jwt(payload)


def decode_access_token(token: str) -> int | None:
    payload = _decode_jwt(token)
    if not payload:
        return None

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        return None

    if datetime.now(timezone.utc).timestamp() > expires_at:
        return None

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id.isdigit():
        return None

    return int(user_id)


def _encode_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_text = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_text = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    unsigned_token = f"{header_text}.{payload_text}"
    signature = _sign(unsigned_token)
    return f"{unsigned_token}.{signature}"


def _decode_jwt(token: str) -> dict | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None

    header_text, payload_text, signature = parts
    unsigned_token = f"{header_text}.{payload_text}"
    expected_signature = _sign(unsigned_token)

    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        return json.loads(_base64url_decode(payload_text))
    except (json.JSONDecodeError, ValueError):
        return None


def _sign(unsigned_token: str) -> str:
    signature = hmac.new(
        config.SECRET_KEY.encode("utf-8"),
        unsigned_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _base64url_encode(signature)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
