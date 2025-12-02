from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test if the API is running"""
    response = client.get("/")
    assert response.status_code == 200
