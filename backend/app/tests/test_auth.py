from app.main import app
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings

client = TestClient(app)

def test_user_register(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "testuser2",
            "email": "testuser2@example.com",
            "password": "Testuser123"
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == "testuser2"
    assert "hashed_password" not in response.json()

def test_duplicate_registration(client):
    user_data = {
        "name": "testuser3",
        "email": "testuser3@example.com",
        "password": "Testuser123"
    }

    first_response = client.post("/auth/register", json=user_data)
    second_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409

def test_user_login(client):
    user_data = {
        "name": "loginuser",
        "email": "loginuser@example.com",
        "password": "Loginuser123"
    }

    client.post("/auth/register", json=user_data)

    response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_user_login_with_wrong_password(client):
    user_data = {
            "name": "loginuser1",
            "email": "loginuser1@example.com",
            "password": "Correctpassword123"
        }
    
    client.post("/auth/register", json=user_data)
    
    response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": "Wrongpassword123"
        }
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid Email or Password"
    )

def test_profile_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_access_profile_with_token(client):
    user_data = {
        "name": "profileuser",
        "email": "profileuser@example.com",
        "password": "TestPassword123"
    }

    client.post("/auth/register", json=user_data)

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]


def test_access_profile_with_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer invalid.fake.token"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_access_profile_with_expired_token(client):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_access_profile_with_invalid_subject(client):
    token = jwt.encode(
        {
            "sub": "not-a-user-id",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_access_profile_with_missing_subject(client):
    token = jwt.encode(
        {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_inactive_user_cannot_login(client):
    user_data = {
        "name": "inactive_login",
        "email": "inactive_login@example.com",
        "password": "TestPassword123"
    }

    client.post("/auth/register", json=user_data)

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    token = login_response.json()["access_token"]

    client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is Inactive"