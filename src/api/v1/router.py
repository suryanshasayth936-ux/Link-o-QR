"""API v1 master router."""

from fastapi import APIRouter
from src.api.v1.endpoints import qr

api_v1_router = APIRouter()
api_v1_router.include_router(qr.router)
