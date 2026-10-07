from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError


def test_health_reports_application_and_database_ready(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    assert response.headers["X-Request-ID"]


def test_health_preserves_valid_request_id(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "demo-request-42"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "demo-request-42"


def test_health_replaces_invalid_request_id(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "contains spaces"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "contains spaces"


def test_health_returns_safe_error_when_database_is_unavailable(
    client: TestClient, monkeypatch
) -> None:
    def fail_connection_check() -> None:
        raise OperationalError("SELECT 1", {}, Exception("database details"))

    monkeypatch.setattr(client.app.state.database, "check_connection", fail_connection_check)

    response = client.get("/api/v1/health", headers={"X-Request-ID": "db-failure"})

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "database_unavailable",
            "message": "The database is unavailable",
            "request_id": "db-failure",
        }
    }
    assert "database details" not in response.text
