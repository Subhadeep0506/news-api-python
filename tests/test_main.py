import pytest

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI"}


def test_register_user():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "role": "user",
        "first_name": "test",
        "last_name": "user",
    }
    response = client.post("/register", json=user_data)
    print(response.json())
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400

def test_register_admin():
    user_data = {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "password": "testadminpassword",
        "role": "admin",
        "first_name": "test",
        "last_name": "admin",
    }
    response = client.post("/register", json=user_data)
    print(response.json())
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400

@pytest.fixture
def auth_token():
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_token_admin():
    login_data = {"username": "testadmin", "password": "testadminpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login():
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200


def test_logout(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200


def test_get_users(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/users", headers=headers)
    assert response.status_code == 401

def test_get_users_with_admin(auth_token_admin):
    headers = {"Authorization": f"Bearer {auth_token_admin}"}
    response = client.get("/users", headers=headers)
    assert response.status_code == 200
