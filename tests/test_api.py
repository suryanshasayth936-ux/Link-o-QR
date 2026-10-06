"""Integration tests for FastAPI endpoints and validation rules."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Verify system health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Link'o'QR" in data["service"]


def test_index_ui_endpoint(client: TestClient):
    """Verify HTML UI is served correctly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Link'o'QR" in response.text
    assert "Target Destination URL" in response.text


def test_api_generate_success(client: TestClient):
    """Verify QR code generation via JSON POST endpoint."""
    payload = {
        "url": "https://fastapi.tiangolo.com",
        "box_size": 10,
        "border": 4,
        "error_correction": "M",
        "fill_color": "#000000",
        "back_color": "#ffffff",
        "format": "png",
    }
    response = client.post("/api/v1/qr/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["url"] == "https://fastapi.tiangolo.com"
    assert data["format"] == "png"
    assert data["data_uri"].startswith("data:image/png;base64,")


def test_api_generate_svg_success(client: TestClient):
    """Verify SVG format generation via JSON POST endpoint."""
    payload = {
        "url": "https://python.org",
        "format": "svg",
    }
    response = client.post("/api/v1/qr/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "svg"
    assert data["data_uri"].startswith("data:image/svg+xml;base64,")


def test_api_generate_invalid_schemes(client: TestClient):
    """Verify malicious or unsupported schemes are rejected."""
    bad_urls = [
        "javascript:alert('xss')",
        "file:///etc/passwd",
        "data:text/html;base64,PHNjcmlwdD4=",
        "ftp://files.example.com",
        "mailto:user@example.com",
        "just-a-plain-string",
    ]
    for bad_url in bad_urls:
        response = client.post("/api/v1/qr/generate", json={"url": bad_url})
        assert response.status_code == 422, f"Failed to reject invalid URL: {bad_url}"
        data = response.json()
        assert data["success"] is False
        assert data["error_type"] == "ValidationError"


def test_api_generate_invalid_color_format(client: TestClient):
    """Verify malformed hex colors are rejected."""
    payload = {
        "url": "https://example.com",
        "fill_color": "not-a-color",
    }
    response = client.post("/api/v1/qr/generate", json=payload)
    assert response.status_code == 422


def test_api_raw_streaming(client: TestClient):
    """Verify GET /api/v1/qr/raw streams image directly from memory."""
    response = client.get("/api/v1/qr/raw?url=https://example.com")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_api_download_attachment(client: TestClient):
    """Verify GET /api/v1/qr/download serves attachment header."""
    response = client.get("/api/v1/qr/download?url=https://example.com&filename=my_qr")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert 'attachment; filename="my_qr.png"' in response.headers["content-disposition"]
