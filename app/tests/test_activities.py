import uuid

def auth_header(client):
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
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_create_activity(client):
    headers = auth_header(client)
    payload = {
        "name": "Tree planting",
        "category": "environment",
        "carbon_output": 5.0
    }
    response = client.post("/activities/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["carbon_output"] == payload["carbon_output"]


def test_get_activities(client):
    headers = auth_header(client)
    client.post("/activities/", json={
        "name": "Cycling",
        "category": "fitness",
        "carbon_output": 2.5
    }, headers=headers)
    response = client.get("/activities/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
