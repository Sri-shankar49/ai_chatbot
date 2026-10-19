
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

ALLOWED_ORIGIN = "http://localhost:5173"


def test_frontend_origin_is_allowed():
    response = client.options(
        "/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("access-control-allow-origin") == (
        ALLOWED_ORIGIN
    )


def test_untrusted_origin_is_not_allowed():
    response = client.options(
        "/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers
