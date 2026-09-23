# VITA-BAND AI: REST API & Telemetry Endpoints

**Project**: VITA-BAND AI  
**Team**: ALPHA MECHS  
**SIH Problem Statement ID**: SIH26198  

---

## 1. Base URL & Interactive Docs

- **Local Base URL**: `http://localhost:8000`
- **Swagger Interactive UI**: `http://localhost:8000/docs`
- **ReDoc Interactive UI**: `http://localhost:8000/redoc`

---

## 2. API Endpoint Index

### 2.1 System Health
- **`GET /health`**
  - **Description**: Returns system status, operation mode, and active dashboard connections.
  - **Response 200**:
    ```json
    {
      "status": "healthy",
      "service": "VITA-BAND AI",
      "version": "1.0.0",
      "operation_mode": "DEMO",
      "uptime_seconds": 124.5,
      "connected_dashboard_clients": 1
    }
    ```

### 2.2 Sensors & Telemetry
- **`GET /api/sensors/latest`**
  - **Description**: Returns the latest aggregated health snapshot.
  - **Response 200**: `HealthSnapshot`
- **`POST /api/sensors/ingest`**
  - **Description**: Ingests physical ESP32 or simulated sensor readings.
  - **Payload**: `SensorReading`
  - **Response 201**:
    ```json
    {
      "status": "ingested",
      "device_id": "ESP32-VITABAND-01",
      "risk_level": "NORMAL",
      "risk_score": 12.0
    }
    ```
- **`GET /api/sensors/history?limit=30`**
  - **Description**: Returns recent telemetry points from the local SQLite ring buffer.

### 2.3 AI Risk Assessment
- **`GET /api/risk/current`**
  - **Description**: Evaluates current multi-modal physiological and environmental risk.
  - **Response 200**: `RiskAssessment`

### 2.4 Health Recommendations
- **`GET /api/recommendations`**
  - **Description**: Returns contextual preventive wellness guidance.
  - **Response 200**: `List[Recommendation]`

### 2.5 Simulation Controls
- **`POST /api/simulation/start`**
  - **Description**: Starts one of the 8 deterministic simulation scenarios.
  - **Payload**:
    ```json
    {
      "scenario": "HEAT_STRESS",
      "duration_seconds": 60,
      "severity": 0.85,
      "noise_level": 0.05
    }
    ```
  - **Response 200**: `SimulationScenario`
- **`POST /api/simulation/stop`**
  - **Description**: Reverts active simulation back to `NORMAL` resting baseline.
  - **Response 200**: `SimulationScenario`
- **`GET /api/simulation/status`**
  - **Description**: Returns current simulation configuration and progression.

### 2.6 Emergency Alerts
- **`GET /api/alerts/active`**
  - **Description**: Returns active unacknowledged alert event or `null`.
- **`POST /api/alerts/test`**
  - **Description**: Triggers a manual SOS or test alert event.
  - **Payload**:
    ```json
    {
      "alert_type": "SOS_MANUAL",
      "custom_message": "Manual test alert from dashboard."
    }
    ```
- **`POST /api/alerts/acknowledge`**
  - **Description**: Acknowledges and dismisses an active alert (cancels false alarm).
  - **Payload**:
    ```json
    {
      "alert_id": "alt-819aef32"
    }
    ```

### 2.7 WebSocket
- **`ws://localhost:8000/ws/health-stream`**
  - Continuous bi-directional telemetry broadcast.
