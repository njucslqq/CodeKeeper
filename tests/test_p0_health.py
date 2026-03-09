"""P0 health check tests."""

def test_health_endpoint():
    from fastapi.testclient import TestClient
    from issue_analyzer.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
