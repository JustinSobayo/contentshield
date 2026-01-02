from fastapi import APIRouter

router = APIRouter()

from fastapi import APIRouter, Request
from app.core.config import settings
from app.services.gemini_service import MODEL_NAME
import os

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/debug")
async def debug_info(request: Request):
    """Returns sanitized system status for debugging."""
    return {
        "status": "online",
        "environment": os.getenv("RAILAY_ENVIRONMENT", "development"),
        "model_configured": MODEL_NAME,
        "api_key_status": "present" if settings.GEMINI_API_KEY else "missing",
        "frontend_origin_configured": settings.FRONTEND_ORIGIN,
        "request_origin": request.headers.get("origin"),
        "cors_check": "Match" if request.headers.get("origin") == settings.FRONTEND_ORIGIN else "No Match",
        "timestamp": os.popen("date").read().strip()
    }
