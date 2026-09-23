# VITA-BAND AI: Core Data Flow & Pipeline

**Project**: VITA-BAND AI  
**Team**: ALPHA MECHS  
**SIH Problem Statement ID**: SIH26198  

---

## 1. End-to-End Data Pipeline

The data flow executes seamlessly from raw acquisition through multi-stage processing to live visual presentation:

```mermaid
sequenceDiagram
    autonumber
    participant Hardware as ESP32 / Simulator
    participant Backend as FastAPI Ingestion
    participant Pre as Signal Preprocessing
    participant AI as AI Risk Engine
    participant Rec as Recommendation Engine
    participant Alert as Emergency Alert Engine
    participant DB as SQLite Storage
    participant Stream as WebSocket Streamer
    participant UI as Companion Dashboard

    Hardware->>Backend: Telemetry Stream (2 Hz)
    Backend->>Pre: Raw ECG, EMG, Vitals & Motion
    Pre->>AI: Filtered Envelopes & Extracted Features
    AI->>AI: Multi-Modal Fusion & Risk Classification
    AI->>Rec: Risk Assessment (Score 0-100, Level)
    Rec-->>Backend: Context-Aware Preventive Actions
    AI->>Alert: Check Acute Triggers (Fall, Vitals Outlier)
    Alert-->>Backend: Active Alert / Countdown Status
    Backend->>DB: Persist Snapshot & History Buffer
    Backend->>Stream: Assemble Full Telemetry Payload
    Stream-->>UI: Live WebSocket Broadcast (/ws/health-stream)
    UI->>UI: Real-Time Waveform Render & Gauge Update
```

---

## 2. Ingestion & Validation Stage

1. **Ingestion Channel**:
   - In DEMO MODE: `SmartHealthSimulator` generates packets internally.
   - In HARDWARE MODE: The ESP32 sends HTTP POST `/api/sensors/ingest`.
2. **Data Validation**:
   - All payloads are strictly parsed and validated against the Pydantic `SensorReading` schema.
   - Values outside biological bounds (e.g. $HR < 30$ or $HR > 240$) are rejected with HTTP 422.

---

## 3. Storage & Dissemination Stage

- **In-Memory Ring Buffer**: Stores the latest 120 seconds of telemetry for instant retrieval and low latency.
- **Local SQLite Persistence**: Appends timestamped records to `telemetry_records` and `alert_records` for long-term health history without cloud reliance.
- **Broadcasting Engine**: Concurrently serializes and pushes updates to all connected dashboard WebSocket clients.
