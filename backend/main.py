"""
VITA-BAND AI: Backend Entrypoint
Production-style FastAPI Application for SIH 2026 Problem Statement SIH26198.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.websocket.stream import stream_manager
from backend.api.routes_health import router as health_router
from backend.api.routes_sensors import router as sensors_router
from backend.api.routes_risk import router as risk_router
from backend.api.routes_recommendations import router as rec_router
from backend.api.routes_simulation import router as sim_router
from backend.api.routes_alerts import router as alerts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler: starts continuous telemetry streaming loop."""
    print(f"[STARTUP] Starting {settings.PROJECT_NAME} Backend Engine (v{settings.VERSION})...")
    stream_task = asyncio.create_task(stream_manager.start_background_loop())
    yield
    print("[SHUTDOWN] Shutting down streaming loops...")
    stream_task.cancel()
    try:
        await stream_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=f"{settings.PROJECT_NAME} Backend",
    version=settings.VERSION,
    description=(
        "Production-style backend for VITA-BAND AI: A secure, AI-powered Personal Health Companion "
        "providing real-time privacy-preserving health monitoring and early risk detection.\n\n"
        "**MEDICAL DISCLAIMER**: This system is a healthcare technology prototype for early-warning "
        "and demonstration purposes. It does not provide medical diagnoses or replace licensed clinical evaluation."
    ),
    lifespan=lifespan,
)

# Enable CORS for frontend dashboard, cloud hosts, and local network devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(sensors_router)
app.include_router(risk_router)
app.include_router(rec_router)
app.include_router(sim_router)
app.include_router(alerts_router)


# Real-time WebSocket Endpoint
@app.websocket("/ws/health-stream")
async def websocket_health_stream(websocket: WebSocket):
    """
    Continuous real-time physiological & environmental telemetry stream.
    Delivers multi-sensor values, ECG/EMG buffers, risk scores, recommendations,
    and alert events to connected client dashboards.
    """
    await stream_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; accept optional control messages from client
            data = await websocket.receive_text()
            try:
                import json
                from datetime import datetime
                msg = json.loads(data)
                if isinstance(msg, dict) and msg.get("action") == "ping":
                    pong_msg = json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                        "echo": msg.get("timestamp")
                    })
                    await websocket.send_text(pong_msg)
            except Exception:
                pass
    except WebSocketDisconnect:
        await stream_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS_EXCEPTION] {e}")
        await stream_manager.disconnect(websocket)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "team": "ALPHA MECHS",
        "sih_ps_id": "SIH26198",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/health-stream",
        "disclaimer": "Early-warning prototype only. Not for clinical diagnosis.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
