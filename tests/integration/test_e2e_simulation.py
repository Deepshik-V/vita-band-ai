"""
End-to-End Integration Tests: Sensor -> Simulation -> AI -> Alert Flow
"""
from fastapi.testclient import TestClient
from backend.main import app
from backend.simulation.simulator import simulator
from backend.alerts.alert_engine import alert_engine

client = TestClient(app)


def test_e2e_full_hackathon_demo_flow():
    # 1. Reset baseline
    simulator.stop_scenario()
    r_norm = simulator.generate_reading()
    assert r_norm.heart_rate < 90.0
    assert r_norm.temperature < 37.5
    assert not r_norm.fall_detected

    # 2. Trigger HEAT_STRESS scenario
    start_resp = client.post("/api/simulation/start", json={
        "scenario": "HEAT_STRESS",
        "duration_seconds": 60,
        "severity": 0.9,
    })
    assert start_resp.status_code == 200

    # Ingest next reading generated under heat stress
    r_heat = simulator.generate_reading()
    assert r_heat.temperature > 38.0
    assert r_heat.heart_rate > 115.0

    # Ingest through backend pipeline
    ingest_heat = client.post("/api/sensors/ingest", json=r_heat.model_dump(mode="json"))
    assert ingest_heat.status_code == 201
    assert ingest_heat.json()["risk_level"] in ["WARNING", "CRITICAL"]

    # Verify recommendations reflect heat stress
    recs_resp = client.get("/api/recommendations")
    assert recs_resp.status_code == 200
    heat_rec_found = any("HEAT_STRESS" in r["risk_category"] for r in recs_resp.json())
    assert heat_rec_found

    # 3. Trigger FALL scenario
    client.post("/api/simulation/start", json={
        "scenario": "FALL",
        "duration_seconds": 60,
        "severity": 0.95,
    })

    # Step simulator to impact point
    for _ in range(5):
        r_fall = simulator.generate_reading()
        if r_fall.fall_detected:
            break

    assert r_fall.fall_detected is True
    # Ingest fall reading
    ingest_fall = client.post("/api/sensors/ingest", json=r_fall.model_dump(mode="json"))
    assert ingest_fall.status_code == 201
    assert ingest_fall.json()["risk_level"] == "CRITICAL"

    # Verify emergency alert engine triggered
    active_alert_resp = client.get("/api/alerts/active")
    assert active_alert_resp.status_code == 200
    alert_obj = active_alert_resp.json()
    assert alert_obj is not None
    assert alert_obj["alert_type"] == "FALL_DETECTED"
    assert alert_obj["countdown_seconds"] > 0

    # 4. User acknowledges/dismisses false alarm alert
    ack_resp = client.post("/api/alerts/acknowledge", json={"alert_id": alert_obj["alert_id"]})
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "acknowledged"

    # 5. Clean reset to NORMAL
    stop_resp = client.post("/api/simulation/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["scenario_type"] == "NORMAL"
