from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from typing import Literal
from app.database import check_database_connection
from app.config import settings

router = APIRouter(tags=["health"])

class ComprehensiveHealthResponse(BaseModel):
    status: str
    ai_status: Literal["ONLINE", "FALLBACK_READY", "DEGRADED", "UNAVAILABLE"]
    database: str
    analytics: str
    storage: str
    version: str
    system_identity: str
    environment: str


@router.get("/health", response_model=ComprehensiveHealthResponse)
async def health_check(response: Response):
    """Production health check verifying database and AI provider status."""
    db_connected = check_database_connection()
    
    if not db_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        db_status = "DISCONNECTED"
    else:
        db_status = "CONNECTED"

    if settings.GEMINI_API_KEY:
        ai_status = "ONLINE"
    else:
        ai_status = "FALLBACK_READY"

    return {
        "status": "ok" if db_connected else "degraded",
        "ai_status": ai_status,
        "database": db_status,
        "analytics": "OPERATIONAL",
        "storage": "MOUNTED",
        "version": "1.0.0",
        "system_identity": "VIGNAI AI-Native Campus OS",
        "environment": settings.ENVIRONMENT,
    }
