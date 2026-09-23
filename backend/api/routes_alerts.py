"""
Emergency Alert and SOS Routes
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.models.schemas import AlertEvent, AlertTestRequest, AlertAcknowledgeRequest
from backend.alerts.alert_engine import alert_engine
from backend.storage.db import db_engine

router = APIRouter(prefix="/api/alerts", tags=["Emergency Alerts"])


class EmergencyContactUpdateRequest(BaseModel):
    contact: str


@router.get("/active", response_model=Optional[AlertEvent])
def get_active_alert():
    """Returns currently active emergency alert and countdown state, if any."""
    return alert_engine.active_alert


@router.get("/history", response_model=List[Dict[str, Any]])
def get_alert_history(limit: int = 20):
    """Returns historical emergency events and acknowledgment logs."""
    return db_engine.get_recent_alerts(limit=limit)


@router.get("/contact")
def get_emergency_contact():
    """Returns the currently configured primary emergency contact number."""
    return {
        "emergency_contact": alert_engine.emergency_contact,
        "countdown_seconds": 15,
        "dispatch_mode": "SAFE_MOCK",
    }


@router.put("/contact")
def update_emergency_contact(request: EmergencyContactUpdateRequest):
    """Dynamically updates the registered emergency contact recipient."""
    if not request.contact or len(request.contact.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact must be a valid phone number or dispatch address"
        )
    alert_engine.emergency_contact = request.contact.strip()
    return {
        "status": "updated",
        "emergency_contact": alert_engine.emergency_contact
    }


@router.post("/test", response_model=AlertEvent)
def trigger_alert_test(request: AlertTestRequest):
    """
    Triggers a safe mock emergency alert test or manual SOS.
    Does NOT initiate real emergency dispatches.
    """
    return alert_engine.trigger_test_alert(
        alert_type=request.alert_type,
        custom_message=request.custom_message
    )


@router.post("/acknowledge")
def acknowledge_alert(request: AlertAcknowledgeRequest):
    """
    Cancels or acknowledges an active alert.
    Halts countdown and cancels mock dispatch.
    """
    ack = alert_engine.acknowledge_alert(request.alert_id)
    if not ack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active unacknowledged alert found with ID {request.alert_id}"
        )
    return {"status": "acknowledged", "alert_id": request.alert_id}
