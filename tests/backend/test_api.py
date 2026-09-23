"""
Backend API and Schema Validation Tests
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VITA-BAND AI"
    assert "uptime_seconds" in data


def test_latest_sensors():
    response = client.get("/api/sensors/latest")
    assert response.status_code == 200
    data = response.json()
    assert "heart_rate" in data
    assert "spo2" in data
    assert "temperature" in data
    assert "humidity" in data
    assert 30 <= data["heart_rate"] <= 240
    assert 60 <= data["spo2"] <= 100


def test_sensor_payload_validation_rejects_out_of_bounds():
    invalid_payload = {
        "heart_rate": -15.0,
        "spo2": 98.0,
        "temperature": 36.8,
        "humidity": 50.0,
    }
    response = client.post("/api/sensors/ingest", json=invalid_payload)
    assert response.status_code == 422


def test_sensor_payload_ingest_valid():
    valid_payload = {
        "device_id": "ESP32-VITABAND-TEST",
        "heart_rate": 76.0,
        "spo2": 98.5,
        "temperature": 36.7,
        "humidity": 52.0,
        "accel_x": 0.05,
        "accel_y": 0.02,
        "accel_z": 0.99,
        "gyro_x": 0.0,
        "gyro_y": 0.0,
        "gyro_z": 0.0,
        "activity": "resting",
        "fall_detected": False,
        "ecg_signal": [0.1, 0.2, 1.0, -0.2, 0.3],
        "emg_signal": [12.0, 15.0, 10.0],
        "ecg_status": "normal",
        "emg_status": "normal",
        "battery_percentage": 92,
    }
    response = client.post("/api/sensors/ingest", json=valid_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ingested"
    assert "risk_level" in data
    assert "risk_score" in data


def test_sensors_export_endpoint():
    response = client.get("/api/sensors/export?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "export_timestamp" in data
    assert "data" in data
    assert "record_count" in data


def test_risk_current_endpoint():
    response = client.get("/api/risk/current")
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["NORMAL", "WARNING", "CRITICAL"]
    assert 0.0 <= data["risk_score"] <= 100.0
    assert "detected_risks" in data


def test_recommendations_endpoint():
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "guidance" in data[0]
    assert "disclaimer" in data[0]


def test_simulation_endpoints():
    start_resp = client.post("/api/simulation/start", json={
        "scenario": "HEAT_STRESS",
        "duration_seconds": 30,
        "severity": 0.85
    })
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    assert start_data["scenario_type"] == "HEAT_STRESS"
    assert start_data["active"] is True

    stat_resp = client.get("/api/simulation/status")
    assert stat_resp.status_code == 200
    assert stat_resp.json()["scenario_type"] == "HEAT_STRESS"

    stop_resp = client.post("/api/simulation/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["scenario_type"] == "NORMAL"
    assert stop_resp.json()["active"] is False


def test_alert_test_and_acknowledge():
    test_resp = client.post("/api/alerts/test", json={
        "alert_type": "SOS_MANUAL",
        "custom_message": "Automated pytest SOS alert"
    })
    assert test_resp.status_code == 200
    alert_data = test_resp.json()
    alert_id = alert_data["alert_id"]
    assert alert_data["severity"] == "CRITICAL"
    assert alert_data["acknowledged"] is False

    active_resp = client.get("/api/alerts/active")
    assert active_resp.status_code == 200
    assert active_resp.json()["alert_id"] == alert_id

    ack_resp = client.post("/api/alerts/acknowledge", json={"alert_id": alert_id})
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "acknowledged"

    cleared_resp = client.get("/api/alerts/active")
    assert cleared_resp.status_code == 200
    assert cleared_resp.json() is None


def test_emergency_contact_endpoints():
    # Read contact
    get_resp = client.get("/api/alerts/contact")
    assert get_resp.status_code == 200
    assert "emergency_contact" in get_resp.json()

    # Update contact
    put_resp = client.put("/api/alerts/contact", json={"contact": "+91 9988776655"})
    assert put_resp.status_code == 200
    assert put_resp.json()["emergency_contact"] == "+91 9988776655"


def test_alert_history_endpoint():
    response = client.get("/api/alerts/history?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
