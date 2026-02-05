"""
Pytest Configuration and Fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app as fastapi_app

# Import all models so they're registered with Base
from app import models  # This imports all models from __init__.py


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client, db_session):
    """Create authenticated user and return auth headers"""
    from app.models.user import User
    from app.auth.password import hash_password

    # Create test user
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_password("testpassword123")
    )
    db_session.add(user)
    db_session.commit()

    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={
            "username_or_email": "testuser",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
