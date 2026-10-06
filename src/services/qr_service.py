"""In-memory QR code generation service using qrcode and Pillow."""

import base64
import io
import logging
from typing import Tuple
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)
from qrcode.image.svg import SvgPathImage

from src.core.exceptions import QRGenerationError
from src.schemas.qr import ErrorCorrectionLevel, QRFormat, QRGenerateRequest, QRResponse

logger = logging.getLogger(__name__)

ERROR_CORRECTION_MAP = {
    ErrorCorrectionLevel.LOW: ERROR_CORRECT_L,
    ErrorCorrectionLevel.MEDIUM: ERROR_CORRECT_M,
    ErrorCorrectionLevel.QUARTILE: ERROR_CORRECT_Q,
    ErrorCorrectionLevel.HIGH: ERROR_CORRECT_H,
}


class QRService:
    """Service class encapsulating pure in-memory QR code rendering logic."""

    @staticmethod
    def _create_qr_instance(request: QRGenerateRequest) -> qrcode.QRCode:
        """Instantiate configured QRCode object."""
        ec_level = ERROR_CORRECTION_MAP.get(
            request.error_correction, ERROR_CORRECT_M
        )
        return qrcode.QRCode(
            version=None,  # Automatically determine minimal required version
            error_correction=ec_level,
            box_size=request.box_size,
            border=request.border,
        )

    def generate_qr_bytes(self, request: QRGenerateRequest) -> Tuple[bytes, str]:
        """Generate QR code purely in memory and return (raw_bytes, media_type).

        Args:
            request: Validated QR generation parameters.

        Returns:
            Tuple of (raw_bytes, mime_type).

        Raises:
            QRGenerationError: If rendering or buffer operations fail.
        """
        try:
            qr = self._create_qr_instance(request)
            qr.add_data(request.url)
            qr.make(fit=True)

            buffer = io.BytesIO()

            if request.format == QRFormat.SVG:
                # Generate SVG vector graphic
                img = qr.make_image(
                    image_factory=SvgPathImage,
                    fill_color=request.fill_color,
                    back_color=request.back_color,
                )
                img.save(buffer)
                media_type = "image/svg+xml"
            else:
                # Generate standard PNG raster graphic via Pillow
                img = qr.make_image(
                    fill_color=request.fill_color,
                    back_color=request.back_color,
                )
                img.save(buffer, format="PNG")
                media_type = "image/png"

            buffer.seek(0)
            raw_bytes = buffer.getvalue()

            if not raw_bytes:
                raise QRGenerationError("QR generation produced empty byte stream.")

            return raw_bytes, media_type

        except QRGenerationError:
            raise
        except Exception as exc:
            logger.exception("Failed to generate QR code for URL: %s", request.url)
            raise QRGenerationError(
                message=f"Failed to generate QR code: {str(exc)}",
                details={"url": request.url, "format": request.format.value},
            ) from exc

    def generate_qr_base64(self, request: QRGenerateRequest) -> QRResponse:
        """Generate QR code and encode into a base64 Data URI for direct web embedding.

        Args:
            request: Validated QR generation parameters.

        Returns:
            QRResponse with metadata and data_uri string.
        """
        raw_bytes, media_type = self.generate_qr_bytes(request)
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        data_uri = f"data:{media_type};base64,{encoded}"

        return QRResponse(
            success=True,
            url=request.url,
            format=request.format,
            data_uri=data_uri,
            box_size=request.box_size,
            border=request.border,
            error_correction=request.error_correction,
            fill_color=request.fill_color,
            back_color=request.back_color,
        )
