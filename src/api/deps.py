"""API dependency injectors for clean inversion of control."""

from functools import lru_cache
from src.services.qr_service import QRService


@lru_cache()
def get_qr_service() -> QRService:
    """Provide a singleton instance of QRService."""
    return QRService()
