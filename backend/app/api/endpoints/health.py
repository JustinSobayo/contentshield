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
    from datetime import datetime
    return {
        "status": "online",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "model_configured": MODEL_NAME,
        "api_key_status": "present" if settings.GEMINI_API_KEY else "missing",
        "frontend_origin_configured": settings.FRONTEND_ORIGIN,
        "request_origin": request.headers.get("origin"),
        "timestamp": datetime.now().isoformat()
    }
