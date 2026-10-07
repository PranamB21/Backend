from fastapi import Path
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def _test_client(tmp_path) -> TestClient:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'errors.db'}",
        cors_origins="",
        log_level="CRITICAL",
    )
    app = create_app(settings)

    def validate_value(value: int = Path(ge=1)) -> dict[str, int]:
        return {"value": value}

    def raise_unexpected_error() -> None:
        raise RuntimeError("private implementation detail")

    app.add_api_route("/test/values/{value}", validate_value)
    app.add_api_route("/test/failure", raise_unexpected_error)
    return TestClient(app, raise_server_exceptions=False)


def test_validation_errors_use_standard_contract(tmp_path) -> None:
    with _test_client(tmp_path) as client:
        response = client.get("/test/values/0", headers={"X-Request-ID": "invalid-value"})

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Request validation failed"
    assert payload["error"]["request_id"] == "invalid-value"
    assert payload["error"]["details"][0]["location"] == ["path", "value"]


def test_unexpected_errors_hide_internal_details(tmp_path) -> None:
    with _test_client(tmp_path) as client:
        response = client.get("/test/failure", headers={"X-Request-ID": "unexpected"})

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "An unexpected error occurred",
            "request_id": "unexpected",
        }
    }
    assert response.headers["X-Request-ID"] == "unexpected"
    assert "private implementation detail" not in response.text


def test_unknown_routes_use_standard_contract(client: TestClient) -> None:
    response = client.get("/missing", headers={"X-Request-ID": "missing-route"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Not Found",
            "request_id": "missing-route",
        }
    }
