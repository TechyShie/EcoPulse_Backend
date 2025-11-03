import uuid

def test_register_user(client):
    # Generate a unique email each test run to avoid conflict
    email = f"shie{uuid.uuid4().hex[:6]}@example.com"
    response = client.post("/auth/register", json={
        "username": "Shie",
        "email": email,
        "password": "Password123"
    })
    # Expect a proper REST response
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["username"] == "Shie"
    assert "id" in data
    assert "email" in data


def test_login_user(client):
    # Register first
    email = f"shie{uuid.uuid4().hex[:6]}@example.com"
    client.post("/auth/register", json={
        "username": "Shie",
        "email": email,
        "password": "Password123"
    })
    response = client.post("/auth/login", json={
        "email": email,
        "password": "Password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token(client):
    email = f"shie{uuid.uuid4().hex[:6]}@example.com"
    client.post("/auth/register", json={
        "username": "Shie",
        "email": email,
        "password": "Password123"
    })
    login = client.post("/auth/login", json={
        "email": email,
        "password": "Password123"
    }).json()
    refresh = {"refresh_token": login["refresh_token"]}
    response = client.post("/auth/refresh", json=refresh)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_logout_user(client):
    email = f"shie{uuid.uuid4().hex[:6]}@example.com"
    client.post("/auth/register", json={
        "username": "Shie",
        "email": email,
        "password": "Password123"
    })
    login = client.post("/auth/login", json={
        "email": email,
        "password": "Password123"
    }).json()
    payload = {
        "access_token": login["access_token"],
        "refresh_token": login["refresh_token"]
    }
    response = client.post("/auth/logout", json=payload)
    assert response.status_code == 200
    assert response.json()["msg"] == "logged out"
