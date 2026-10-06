"""FastAPI endpoints for QR code generation and dynamic download."""

from urllib.parse import quote
from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import StreamingResponse
import io

from src.api.deps import get_qr_service
from src.core.config import settings
from src.schemas.qr import (
    ErrorCorrectionLevel,
    QRFormat,
    QRGenerateRequest,
    QRResponse,
)
from src.services.qr_service import QRService

router = APIRouter(prefix="/qr", tags=["QR Codes"])


@router.post(
    "/generate",
    response_model=QRResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate QR Code as JSON with Base64 URI",
    description="Validates target URL and renders in-memory QR code returned as base64 Data URI.",
)
async def generate_qr(
    payload: QRGenerateRequest,
    qr_service: QRService = Depends(get_qr_service),
) -> QRResponse:
    """Handle POST request to generate QR code and return base64 data URI."""
    return qr_service.generate_qr_base64(payload)


@router.get(
    "/raw",
    summary="Stream dynamic QR Code image bytes",
    description="Directly streams rendered QR code in-memory without saving any file on disk.",
)
async def get_raw_qr(
    url: str = Query(..., description="Target URL"),
    box_size: int = Query(settings.DEFAULT_BOX_SIZE, ge=1, le=40),
    border: int = Query(settings.DEFAULT_BORDER, ge=0, le=20),
    error_correction: ErrorCorrectionLevel = Query(ErrorCorrectionLevel.MEDIUM),
    fill_color: str = Query(settings.DEFAULT_FILL_COLOR),
    back_color: str = Query(settings.DEFAULT_BACK_COLOR),
    format: QRFormat = Query(QRFormat.PNG),
    qr_service: QRService = Depends(get_qr_service),
) -> StreamingResponse:
    """Stream raw image bytes directly from memory."""
    request_data = QRGenerateRequest(
        url=url,
        box_size=box_size,
        border=border,
        error_correction=error_correction,
        fill_color=fill_color,
        back_color=back_color,
        format=format,
    )
    raw_bytes, media_type = qr_service.generate_qr_bytes(request_data)

    return StreamingResponse(
        io.BytesIO(raw_bytes),
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get(
    "/download",
    summary="Download QR Code attachment",
    description="Dynamically streams QR code attachment directly into client's browser download manager.",
)
async def download_qr(
    url: str = Query(..., description="Target destination URL"),
    box_size: int = Query(settings.DEFAULT_BOX_SIZE, ge=1, le=40),
    border: int = Query(settings.DEFAULT_BORDER, ge=0, le=20),
    error_correction: ErrorCorrectionLevel = Query(ErrorCorrectionLevel.MEDIUM),
    fill_color: str = Query(settings.DEFAULT_FILL_COLOR),
    back_color: str = Query(settings.DEFAULT_BACK_COLOR),
    format: QRFormat = Query(QRFormat.PNG),
    filename: str = Query("qrcode", description="Base filename without extension"),
    qr_service: QRService = Depends(get_qr_service),
) -> Response:
    """Serve dynamically generated QR code as a file download attachment."""
    request_data = QRGenerateRequest(
        url=url,
        box_size=box_size,
        border=border,
        error_correction=error_correction,
        fill_color=fill_color,
        back_color=back_color,
        format=format,
    )
    raw_bytes, media_type = qr_service.generate_qr_bytes(request_data)
    ext = format.value
    safe_filename = quote(filename.strip().replace(" ", "_") or "qrcode")
    content_disposition = f'attachment; filename="{safe_filename}.{ext}"'

    return Response(
        content=raw_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": content_disposition,
            "Cache-Control": "no-store, no-cache, must-revalidate",
        },
    )
