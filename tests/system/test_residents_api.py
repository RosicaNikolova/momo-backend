from fastapi.testclient import TestClient

from app.main import app

"""
System tests for the Residents API endpoints.

Tests the complete HTTP request/response cycle for:
- GET /api/residents/ (list all residents)
- GET /api/residents/{id} (get single resident)
"""

client = TestClient(app)


def test_get_residents_empty(client):
    """Should return empty list when no residents exist"""
    response = client.get("/api/residents/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_residents_with_data(client, sample_resident):
    """Should return list of residents when data exists"""
    response = client.get("/api/residents/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "John Doe"
    assert data[0]["room_number"] == "101"
    assert data[0]["id"] == sample_resident.id


def test_get_resident_by_id_success(client, sample_resident):
    """Should return resident when ID exists"""
    response = client.get(f"/api/residents/{sample_resident.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_resident.id
    assert data["name"] == "John Doe"
    assert data["room_number"] == "101"


def test_get_resident_by_id_not_found(client):
    """Should return 404 when resident doesn't exist"""
    response = client.get("/api/residents/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
