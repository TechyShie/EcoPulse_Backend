import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # Recreate tables for isolation if using sqlite in-memory or simple engine
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def create_user_and_token():
    # Register
    register_payload = {
        "username": "tester",
        "email": "tester@example.com",
        "password": "password123",
    }
    r = client.post("/api/auth/register", json=register_payload)
    assert r.status_code in (200, 201)

    # Login
    login_payload = {"email": register_payload["email"], "password": register_payload["password"]}
    r = client.post("/api/auth/login", json=login_payload)
    assert r.status_code == 200
    token = r.json()["access_token"]
    return token


def test_create_log_computes_eco_points_from_provided_carbon_output():
    token = create_user_and_token()

    payload = {
        "name": "Cycling to office",
        "category": "Transportation",
        "description": "Morning commute",
        "carbon_output": 1.2,
    }
    r = client.post("/api/logs/", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert "eco_points" in data
    assert isinstance(data["eco_points"], (int, float))
    # With low carbon emissions, eco_points should be relatively high
    assert data["eco_points"] > 0
    assert data["carbon_output"] == pytest.approx(1.2, rel=1e-3)


def test_create_log_computes_emissions_when_structured_inputs_provided():
    token = create_user_and_token()

    # Provide distance and mode so EmissionsCalculator is used.
    # For car: factor ~ 0.21 kg/km => 10 km -> 2.1 kg
    payload = {
        "name": "Drive to store",
        "category": "Transportation",
        "description": "Grocery run",
        "carbon_output": 999.0,  # should be ignored due to structured inputs
        "distance": 10,
        "mode": "car",
    }
    r = client.post("/api/logs/", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["carbon_output"] == pytest.approx(2.1, rel=1e-3)
    assert data["eco_points"] >= 0


def test_update_log_recomputes_eco_points_and_emissions_when_structured_inputs_provided():
    token = create_user_and_token()

    # create initial
    create_payload = {
        "name": "Bus ride",
        "category": "Transportation",
        "description": "Commute",
        "carbon_output": 5.0,
    }
    r = client.post("/api/logs/", headers={"Authorization": f"Bearer {token}"}, json=create_payload)
    assert r.status_code == 201
    created = r.json()

    # update with structured inputs to trigger recalculation (bus factor 0.05 * 20km = 1.0kg)
    update_payload = {
        "name": "Bus ride",
        "category": "Transportation",
        "description": "Commute",
        "carbon_output": 123.0,  # should be overridden
        "distance": 20,
        "mode": "bus",
    }
    r = client.put(f"/api/logs/{created['id']}", headers={"Authorization": f"Bearer {token}"}, json=update_payload)
    assert r.status_code == 200, r.text
    updated = r.json()
    assert updated["carbon_output"] == pytest.approx(1.0, rel=1e-3)
    assert updated["eco_points"] >= 0


def test_get_logs_includes_eco_points():
    token = create_user_and_token()

    payload = {
        "name": "Walking",
        "category": "Transportation",
        "description": "Park walk",
        "carbon_output": 0.0,
    }
    r = client.post("/api/logs/", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert r.status_code == 201

    r = client.get("/api/logs/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert "eco_points" in items[0]
