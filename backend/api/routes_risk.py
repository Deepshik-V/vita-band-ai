"""
AI Risk Assessment Routes
"""
from fastapi import APIRouter
from backend.models.schemas import RiskAssessment
from backend.websocket.stream import stream_manager
from backend.simulation.simulator import simulator

router = APIRouter(prefix="/api/risk", tags=["AI Risk Assessment"])


@router.get("/current", response_model=RiskAssessment)
def get_current_risk():
    """Returns the most current real-time AI risk assessment."""
    if stream_manager.latest_risk:
        return stream_manager.latest_risk
    
    # Generate and process reading if not cached yet
    reading = simulator.generate_reading()
    payload = stream_manager.process_and_cache(reading)
    return payload.risk_assessment
