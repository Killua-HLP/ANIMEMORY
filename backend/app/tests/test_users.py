from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

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

def test_update_profile_invalid_name(client):
    user_data = {
        "name": "validuser",
        "email": "valid@example.com",
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
        json={"name": "A"}
    )

    assert response.status_code == 422

def test_update_profile_null_name(client):
    user_data = {
        "name": "nulltestuser",
        "email": "nulltest@example.com",
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
        json={"name": None}
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Display name cannot be null"

def test_update_profile_long_bio(client):
    user_data = {
        "name": "biotestuser",
        "email": "bio@example.com",
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
        json={"bio": "A" * 501}
    )

    assert response.status_code == 422

def test_user_can_only_update_own_profile(client):
    user1 = {
            "name": "firstuser1",
            "email": "first1@example.com",
            "password": "TestPassword123"
        }
    
    user2 = {
            "name": "seconduser2",
            "email": "second1@example.com",
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
        json={
                "name": "updateduser2",
                "bio": "updatedbio"
            }
        )

    assert response.status_code == 200

    updated_data = response.json()
    assert updated_data["name"] == "updateduser2"
    assert updated_data["bio"] == "updatedbio"
    assert updated_data["email"] == user2["email"]

    user1_login = client.post(
    "/auth/login",
    json={
        "email": user1["email"],
        "password": user1["password"]
        }
    )

    user1_token = user1_login.json()["access_token"]

    user1_profile = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {user1_token}"}
    )

    assert user1_profile.status_code == 200
    assert user1_profile.json()["name"] == "firstuser1"
        

