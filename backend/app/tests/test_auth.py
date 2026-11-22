from app.main import app
from fastapi.testclient import TestClient

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

def test_update_my_profile(client):
    user_data = {
        "name": "profiletest",
        "email": "profiletest@example.com",
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

    response = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "updatedprofile",
            "bio": "I love anime!"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "updatedprofile"
    assert response.json()["bio"] == "I love anime!"

def test_update_profile_empty_data(client):
    user_data = {
        "name": "emptyprofile",
        "email": "emptyprofile@example.com",
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

    response = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No Field Provided for update"

def test_update_profile_duplicate_name(client):
    user1 = {
        "name": "firstuser",
        "email": "first@example.com",
        "password": "TestPassword123"
    }

    user2 = {
        "name": "seconduser",
        "email": "second@example.com",
        "password": "TestPassword123"
    }

    client.post("/auth/register", json=user1)
    client.post("/auth/register", json=user2)

    login_response = client.post(
        "/auth/login",
        json={
            "email": user2["email"],
            "password": user2["password"]
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "firstuser"}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Display name is already in use"

def test_deactivate_account(client):
    user_data = {
        "name": "deactivateuser",
        "email": "deactivate@example.com",
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
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["is_active"] is False

def test_deactivated_user_cannot_access_profile(client):
    user_data = {
        "name": "inactiveuser",
        "email": "inactive@example.com",
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
    headers = {"Authorization": f"Bearer {token}"}

    delete_response = client.delete("/users/me", headers=headers)
    assert delete_response.status_code == 200

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive User"