"""Pydantic schemas and validation for QR code generation."""

import re
from enum import Enum
from typing import Literal
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator
from src.core.config import settings

HEX_COLOR_REGEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class ErrorCorrectionLevel(str, Enum):
    """Standard QR Code error correction capability tiers."""

    LOW = "L"  # ~7% recovery
    MEDIUM = "M"  # ~15% recovery
    QUARTILE = "Q"  # ~25% recovery
    HIGH = "H"  # ~30% recovery


class QRFormat(str, Enum):
    """Supported output formats for QR code rendering."""

    PNG = "png"
    SVG = "svg"


class QRGenerateRequest(BaseModel):
    """Incoming payload for QR code generation with strict input validation."""

    url: str = Field(
        ...,
        min_length=1,
        max_length=settings.MAX_URL_LENGTH,
        description="Target destination URL for the QR code.",
        examples=["https://example.com/products/123"],
    )
    box_size: int = Field(
        default=settings.DEFAULT_BOX_SIZE,
        ge=1,
        le=40,
        description="Pixel dimensions of each QR code module.",
    )
    border: int = Field(
        default=settings.DEFAULT_BORDER,
        ge=0,
        le=20,
        description="Quiet zone module border width around the QR code.",
    )
    error_correction: ErrorCorrectionLevel = Field(
        default=ErrorCorrectionLevel.MEDIUM,
        description="Error correction level: L (7%), M (15%), Q (25%), H (30%).",
    )
    fill_color: str = Field(
        default=settings.DEFAULT_FILL_COLOR,
        description="Foreground hex color (e.g., #000000).",
    )
    back_color: str = Field(
        default=settings.DEFAULT_BACK_COLOR,
        description="Background hex color (e.g., #ffffff).",
    )
    format: QRFormat = Field(
        default=QRFormat.PNG,
        description="Image output format: png or svg.",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL scheme, host, and formatting strictly."""
        cleaned_url = v.strip()
        if not cleaned_url:
            raise ValueError("URL cannot be empty or whitespace only.")

        parsed = urlparse(cleaned_url)

        # Enforce strict http/https schemes (prevent javascript:, file:, data:, etc.)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("URL scheme must strictly be 'http' or 'https'.")

        # Must have a valid network host
        if not parsed.netloc:
            raise ValueError("URL must include a valid host/domain name (e.g., https://example.com).")

        # Hostname validation: reject single dots, invalid chars, or spaces
        host = parsed.netloc.split(":")[0]  # Strip port if present
        if not host or len(host) > 253 or " " in host or "." not in host and host != "localhost":
            raise ValueError(f"Malformed or invalid domain host: '{host}'.")

        return cleaned_url

    @field_validator("fill_color", "back_color")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        """Validate color strings to be strictly valid hex codes."""
        cleaned_color = v.strip()
        if not HEX_COLOR_REGEX.match(cleaned_color):
            raise ValueError(f"Invalid hex color format: '{v}'. Expected format like #000000 or #ffffff.")
        return cleaned_color


class QRResponse(BaseModel):
    """Response payload containing generated QR metadata and base64 image data URI."""

    success: bool = True
    url: str
    format: QRFormat
    data_uri: str = Field(description="Base64 encoded data URI for immediate inline display.")
    box_size: int
    border: int
    error_correction: ErrorCorrectionLevel
    fill_color: str
    back_color: str


class ErrorResponse(BaseModel):
    """Standardized error response payload."""

    success: bool = False
    error_type: str
    message: str
    details: dict = Field(default_factory=dict)
