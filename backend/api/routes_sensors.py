"""
Sensor Ingest and Query Routes
"""
from fastapi import APIRouter, HTTPException, status, Response
import json
from backend.models.schemas import SensorReading, HealthSnapshot
from backend.websocket.stream import stream_manager
from backend.storage.db import db_engine
from backend.simulation.simulator import simulator

router = APIRouter(prefix="/api/sensors", tags=["Sensors & Telemetry"])


@router.get("/latest", response_model=HealthSnapshot)
def get_latest_sensors():
    """Returns the most recent sensor reading snapshot."""
    if stream_manager.latest_reading:
        r = stream_manager.latest_reading
    else:
        r = simulator.generate_reading()
        stream_manager.process_and_cache(r)

    return HealthSnapshot(
        timestamp=r.timestamp.isoformat() if hasattr(r.timestamp, "isoformat") else str(r.timestamp),
        heart_rate=r.heart_rate,
        spo2=r.spo2,
        temperature=r.temperature,
        humidity=r.humidity,
        activity=r.activity,
        fall_detected=r.fall_detected,
        ecg_status=r.ecg_status,
        emg_status=r.emg_status,
        battery_percentage=r.battery_percentage,
    )


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_hardware_sensor(reading: SensorReading):
    """
    Ingestion endpoint for physical ESP32 controller.
    Validates payload against Pydantic schema, assesses AI risk, and broadcasts to dashboard.
    """
    payload = stream_manager.process_and_cache(reading)
    await stream_manager.broadcast_payload(payload.model_dump())
    return {
        "status": "ingested",
        "device_id": reading.device_id,
        "risk_level": payload.risk_assessment.risk_level.value,
        "risk_score": payload.risk_assessment.risk_score,
    }


@router.get("/history")
def get_sensor_history(limit: int = 30):
    """Returns historical sensor telemetry records."""
    return db_engine.get_recent_history(limit=limit)


@router.get("/export")
def export_health_records(limit: int = 100):
    """
    Exports local health telemetry history as JSON for offline consultation,
    telemedicine, and ABDM electronic health record portability.
    """
    records = db_engine.get_recent_history(limit=limit)
    return {
        "export_timestamp": simulator.generate_reading().timestamp.isoformat(),
        "device_id": "ESP32-VITABAND-01",
        "record_count": len(records),
        "data": records,
        "disclaimer": "Exported companion telemetry for reference. Not for clinical diagnostic certification."
    }
