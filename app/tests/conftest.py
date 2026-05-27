import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.api.dependencies import get_db
from app.api.v1 import assistant, job, user
from app.core.config import config
from app.db.schema import Base


@pytest.fixture()
def client(tmp_path):
    original_openai_api_key = config.OPENAI_API_KEY
    config.OPENAI_API_KEY = None

    test_db_path = tmp_path / "test.db"
    test_engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(user.router, prefix="/api/v1")
    app.include_router(job.router, prefix="/api/v1")
    app.include_router(assistant.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    config.OPENAI_API_KEY = original_openai_api_key


@pytest.fixture()
def create_user(client):
    def _create_user(name="test_user", password="password123"):
        return client.post(
            "/api/v1/users",
            json={"name": name, "password": password},
        )

    return _create_user


@pytest.fixture()
def auth_headers(client, create_user):
    def _auth_headers(name="test_user", password="password123"):
        create_user(name=name, password=password)
        response = client.post(
            "/api/v1/login",
            json={"name": name, "password": password},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers
