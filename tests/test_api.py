"""
API Integration tests using Flask test client.
"""

import json
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code in [200, 503]
    data = res.get_json()
    assert "status" in data
    assert "service" in data
    assert data["service"] == "GST-Verification-API"


def test_validate_gstin_endpoint_valid(client):
    res = client.get("/api/v1/gstin/27AABCR1718E1ZP/validate")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["validation"]["valid"] is True
    assert data["validation"]["pan"] == "AABCR1718E"


def test_validate_gstin_endpoint_invalid(client):
    res = client.get("/api/v1/gstin/INVALIDGSTIN123/validate")
    assert res.status_code == 400
    data = res.get_json()
    assert data["validation"]["valid"] is False


def test_verify_missing_fields(client):
    # Empty body
    res = client.post("/api/v1/verify", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert data["error"] == "MISSING_SESSION_ID"


def test_legacy_get_gst_details_invalid_session(client):
    res = client.post("/api/v1/getGSTDetails", json={
        "sessionId": "non-existent-session-id",
        "GSTIN": "27AABCR1718E1ZP",
        "captcha": "123456"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert "Invalid session id" in data.get("error", "")
