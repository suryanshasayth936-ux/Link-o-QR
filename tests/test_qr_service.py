"""Unit tests for QRService business logic."""

import pytest
from src.core.exceptions import QRGenerationError
from src.schemas.qr import ErrorCorrectionLevel, QRFormat, QRGenerateRequest
from src.services.qr_service import QRService


def test_generate_png_bytes(qr_service: QRService):
    """Ensure in-memory PNG generation produces valid PNG binary data."""
    req = QRGenerateRequest(
        url="https://example.com/test",
        format=QRFormat.PNG,
    )
    raw_bytes, media_type = qr_service.generate_qr_bytes(req)

    assert media_type == "image/png"
    assert len(raw_bytes) > 0
    # PNG binary signature
    assert raw_bytes.startswith(b"\x89PNG\r\n\x1a\n")


def test_generate_svg_bytes(qr_service: QRService):
    """Ensure in-memory SVG generation produces valid vector markup."""
    req = QRGenerateRequest(
        url="https://example.com/test",
        format=QRFormat.SVG,
    )
    raw_bytes, media_type = qr_service.generate_qr_bytes(req)

    assert media_type == "image/svg+xml"
    assert len(raw_bytes) > 0
    svg_content = raw_bytes.decode("utf-8")
    assert "<svg" in svg_content
    assert "</svg>" in svg_content


def test_generate_base64_response(qr_service: QRService):
    """Ensure Base64 Data URI is properly formatted for inline embedding."""
    req = QRGenerateRequest(
        url="https://example.com/deep/link?query=123",
        box_size=12,
        border=2,
        error_correction=ErrorCorrectionLevel.HIGH,
        fill_color="#10b981",
        back_color="#ffffff",
        format=QRFormat.PNG,
    )
    resp = qr_service.generate_qr_base64(req)

    assert resp.success is True
    assert resp.url == "https://example.com/deep/link?query=123"
    assert resp.box_size == 12
    assert resp.border == 2
    assert resp.error_correction == ErrorCorrectionLevel.HIGH
    assert resp.fill_color == "#10b981"
    assert resp.back_color == "#ffffff"
    assert resp.data_uri.startswith("data:image/png;base64,")


@pytest.mark.parametrize("level", [
    ErrorCorrectionLevel.LOW,
    ErrorCorrectionLevel.MEDIUM,
    ErrorCorrectionLevel.QUARTILE,
    ErrorCorrectionLevel.HIGH,
])
def test_all_error_correction_levels(qr_service: QRService, level: ErrorCorrectionLevel):
    """Ensure all four error correction tiers render without exception."""
    req = QRGenerateRequest(
        url="https://example.com",
        error_correction=level,
    )
    raw_bytes, _ = qr_service.generate_qr_bytes(req)
    assert len(raw_bytes) > 0
