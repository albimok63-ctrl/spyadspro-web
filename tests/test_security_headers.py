"""
Test middleware sicurezza: presenza header X-Content-Type-Options, X-Frame-Options, X-XSS-Protection.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/v1/health"),
        ("GET", "/metrics"),
        ("POST", "/api/v1/auth/login"),
    ],
)
def test_security_headers_present_in_response(
    client: TestClient, method: str, path: str
) -> None:
    """Le risposte includono gli header di sicurezza (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)."""
    if method == "POST" and "login" in path:
        response = client.post(path, json={"username": "admin", "password": "admin"})
    else:
        response = client.get(path)
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
