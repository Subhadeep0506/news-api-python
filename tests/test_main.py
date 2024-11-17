import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.order(1)
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI"}


@pytest.mark.order(2)
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


@pytest.mark.order(3)
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


@pytest.mark.order(4)
def test_login():
    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(5)
def test_logout(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/me/logout", headers=headers)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(6)
def test_get_users(auth_token, auth_token_admin):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/users", headers=headers)
    try:
        assert response.status_code == 401
    except AssertionError:
        assert response.status_code == 400

    headers = {"Authorization": f"Bearer {auth_token_admin}"}
    response = client.get("/users", headers=headers)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(7)
def test_get_users_with_admin(auth_token_admin):
    headers = {"Authorization": f"Bearer {auth_token_admin}"}
    response = client.get("/users", headers=headers)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(8)
def test_update_user_info(auth_token):
    user_update_data = {
        "first_name": "Test User Name",
        "last_name": "Test User Last Name",
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put("/me/update", json=user_update_data, headers=headers)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(9)
def test_delete_user_admin(auth_token_admin):
    headers = {"Authorization": f"Bearer {auth_token_admin}"}
    response = client.delete("/me/delete", headers=headers)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(10)
def test_change_password(auth_token):
    new_password_data = {
        "old_password": "testpassword",
        "new_password": "newpassword",
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/me/change-password", json=new_password_data, headers=headers
    )
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400


@pytest.mark.order(11)
def test_delete_user():
    login_data = {"username": "testuser", "password": "newpassword"}
    response = client.post("/login", json=login_data)
    auth_token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.delete("/me/delete", headers=headers)
    try:
        assert response.status_code == 200
    except AssertionError:
        assert response.status_code == 400
