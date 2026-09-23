"""
Health Check and System Status Route
"""
from datetime import datetime
from fastapi import APIRouter
from backend.config import settings
from backend.websocket.stream import stream_manager

router = APIRouter(tags=["Health & Status"])
START_TIME = datetime.utcnow()


@router.get("/health")
def get_health_status():
    """Returns application health, operation mode, and active dashboard connection count."""
    uptime_sec = (datetime.utcnow() - START_TIME).total_seconds()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "operation_mode": settings.OPERATION_MODE,
        "uptime_seconds": round(uptime_sec, 1),
        "connected_dashboard_clients": len(stream_manager.active_connections),
        "timestamp": datetime.utcnow().isoformat(),
    }
