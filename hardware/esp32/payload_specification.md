# VITA-BAND AI: Hardware Ingestion Specification

**Project**: VITA-BAND AI  
**Team**: ALPHA MECHS  
**SIH Problem Statement ID**: SIH26198  

---

## 1. Ingestion Endpoint Overview

The backend exposes a high-throughput, validated HTTP endpoint for physical ESP32 hardware telemetry ingestion:

- **Endpoint**: `POST /api/sensors/ingest`
- **Content-Type**: `application/json`
- **Expected Transmission Rate**: 1 Hz to 5 Hz (default 2 Hz)
- **Response Code**: `201 Created`

---

## 2. Expected JSON Payload Schema

```json
{
  "device_id": "ESP32-VITABAND-PHYSICAL-01",
  "heart_rate": 78.5,
  "spo2": 98.2,
  "temperature": 36.8,
  "humidity": 52.0,
  "accel_x": 0.045,
  "accel_y": 0.082,
  "accel_z": 0.995,
  "gyro_x": 0.0,
  "gyro_y": 0.0,
  "gyro_z": 0.0,
  "activity": "resting",
  "fall_detected": false,
  "ecg_signal": [12.4, 25.1, 140.2, -35.0, 48.0],
  "emg_signal": [15.2, 18.0, 12.1, 24.5],
  "ecg_status": "normal",
  "emg_status": "normal",
  "battery_percentage": 92
}
```

### Parameter Reference

| Field | Type | Valid Range | Sensor Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| `device_id` | String | Non-empty | Firmware | Unique hardware MAC / identifier |
| `heart_rate` | Float | 30.0 – 240.0 | MAX30102 | Optical pulse rate (BPM) |
| `spo2` | Float | 60.0 – 100.0 | MAX30102 | Arterial blood oxygen saturation (%) |
| `temperature`| Float | 20.0 – 50.0 | DHT22 / Skin | Body/ambient temperature (°C) |
| `humidity` | Float | 0.0 – 100.0 | DHT22 | Relative ambient humidity (%) |
| `accel_x/y/z`| Float | -16.0 – 16.0 | MPU6050 | Linear acceleration vectors in $g$ |
| `gyro_x/y/z` | Float | -2000 – 2000 | MPU6050 | Angular velocity in °/s |
| `activity` | String | Enum / String | IMU heuristic | "resting", "walking", "fall_impact", "immobile" |
| `fall_detected`| Boolean| true / false | IMU heuristic | High-g impact indicator |
| `ecg_signal` | Array[Float] | $\pm 500$ mV | AD8232 | Rolling ADC buffer (10 to 100 samples) |
| `emg_signal` | Array[Float] | 0 to 500 $\mu$V | Muscle Sensor | Rectified muscle tone samples |

---

## 3. Server Response Format

Upon validation, the backend evaluates the AI risk classification and broadcasts the updated state to all connected dashboard WebSocket clients.

### Success Response (`201 Created`):
```json
{
  "status": "ingested",
  "device_id": "ESP32-VITABAND-PHYSICAL-01",
  "risk_level": "NORMAL",
  "risk_score": 12.0
}
```

### Validation Error (`422 Unprocessable Entity`):
If a sensor generates physically impossible values (e.g., $HR = -15$), the server rejects the corrupted frame:
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "heart_rate"],
      "msg": "Input should be greater than or equal to 30",
      "input": -15.0
    }
  ]
}
```
