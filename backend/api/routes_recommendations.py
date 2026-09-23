"""
Recommendation Engine Routes
"""
from typing import List
from fastapi import APIRouter
from backend.models.schemas import Recommendation
from backend.websocket.stream import stream_manager
from backend.simulation.simulator import simulator

router = APIRouter(prefix="/api/recommendations", tags=["Health Recommendations"])


@router.get("", response_model=List[Recommendation])
def get_recommendations():
    """Returns the current contextual wellness and early-warning guidance."""
    if stream_manager.latest_recommendations:
        return stream_manager.latest_recommendations

    reading = simulator.generate_reading()
    payload = stream_manager.process_and_cache(reading)
    return payload.recommendations
