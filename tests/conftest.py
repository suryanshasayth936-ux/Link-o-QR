"""Pytest fixtures configuration."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.qr_service import QRService


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provide a TestClient instance for integration tests."""
    return TestClient(app)


@pytest.fixture(scope="session")
def qr_service() -> QRService:
    """Provide a fresh instance of QRService for unit testing."""
    return QRService()
