from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.security import limiter
from app.api.endpoints import analyze, health
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Content Shield API")

# Startup Log
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Content Shield API starting up in {settings.ENVIRONMENT} mode")
    if not settings.GEMINI_API_KEY:
        logger.warning("⚠️ GEMINI_API_KEY is not set. AI features will fail.")
    logger.info(f"Frontend origin allowed: {settings.FRONTEND_ORIGIN}")

# Rate Limiter Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Content Shield API",
        "docs": "/docs"
    }

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(analyze.router)
app.include_router(health.router, tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)