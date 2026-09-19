from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_required_api_routes_are_mounted():
    mounted_paths = {route.path for route in app.routes if hasattr(route, "path")}

    expected_paths = {
        "/api/health",
        "/api/persons",
        "/api/network/stats",
        "/api/graph/path",
        "/api/intelligence/summary",
        "/api/cases",
        "/api/agents/status",
        "/api/evidence/summary",
        "/api/graph-rag/status",
        "/api/investigate",
        "/api/anomalies",
        "/api/transactions",
        "/api/search",
        "/api/documents/search",
        "/api/documents/upload",
        "/api/workspace/dashboard",
        "/api/workspace/investigations/{investigation_id}",
    }

    missing = sorted(expected_paths - mounted_paths)
    assert not missing, f"Missing API routes: {missing}"


def test_core_health_routes_work():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    api_health = client.get("/api/health")
    assert api_health.status_code == 200
    assert api_health.json()["status"] == "healthy"
