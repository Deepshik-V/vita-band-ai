# VITA-BAND AI: Secure, AI-Powered Personal Health Companion

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://sih.gov.in)
[![SIH Problem Statement ID: 26181](https://img.shields.io/badge/SIH%20PS%20ID-26181-blue.svg)](https://sih.gov.in)
[![Team ALPHA MECHS](https://img.shields.io/badge/Team-ALPHA%20MECHS-cyan.svg)](#team-information)
[![Validation Status](https://img.shields.io/badge/Tests-44%2F44%20PASSED%20(100%25)-brightgreen.svg)](#test-results)
[![AI Validation](https://img.shields.io/badge/AI%20Scenarios-8%2F8%20Validated-success.svg)](#8-validated-simulation-scenarios)
[![Backend Status](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](#backend-architecture)
[![Frontend Status](https://img.shields.io/badge/React%2019-Vite%20Production%20Build-61DAFB.svg)](#frontend-architecture)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#license)

> **SIH Problem Statement ID**: **26181** (System Configuration Mapping: `SIH26198`)  
> **Team**: **ALPHA MECHS**  
> **Category**: Software / MedTech / Disaster Management / IoT Biometrics  

---

## Medical & Hardware Implementation Disclaimer

> [!CAUTION]
> **PROTOTYPE & RESEARCH DISCLAIMER**:  
> VITA-BAND AI is an early-warning research and healthcare technology prototype developed for the Smart India Hackathon 2026. It is **NOT** a certified medical diagnostic device. It does not provide definitive clinical diagnoses, prescribe treatment, or replace licensed emergency medical practitioners.  
> 
> **SENSOR HARDWARE INTEGRATION STATUS**:  
> In the current deployment and evaluation mode, telemetry is generated using a high-fidelity **biometric simulation and signal synthesis engine** (`backend/simulation/simulator.py`) that models realistic multi-sensor physiological waveforms (ECG, PPG, EMG, Galvanic Skin Response, Accelerometer/IMU) and ambient environmental conditions (DHT22, MQ-135 Air Quality). Hardware schematics, ESP32 firmware, and pinout diagrams are provided in [`hardware/`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/hardware) for physical sensor integration over UART/BLE/MQTT, but **all demonstration numbers and dashboard streams currently utilize validated deterministic simulation**.

---

## Table of Contents

1. [Problem Statement Summary](#problem-statement-summary)
2. [Project Objective](#project-objective)
3. [Proposed Solution](#proposed-solution)
4. [Key Features](#key-features)
5. [System Architecture](#system-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Backend Architecture](#backend-architecture)
8. [AI / Risk Engine & Anomaly Detection](#ai--risk-engine--anomaly-detection)
9. [WebSocket Real-Time Communication](#websocket-real-time-communication)
10. [Environmental Monitoring & Heat Index Fusion](#environmental-monitoring--heat-index-fusion)
11. [Disaster-Specific Health Alerts](#disaster-specific-health-alerts)
12. [Emergency Assistance & Countdown Flow](#emergency-assistance--countdown-flow)
13. [Privacy-Preserving / Edge-AI Design](#privacy-preserving--edge-ai-design)
14. [8 Validated Simulation Scenarios](#8-validated-simulation-scenarios)
15. [Technology Stack](#technology-stack)
16. [Project Folder Structure](#project-folder-structure)
17. [Local Setup Instructions](#local-setup-instructions)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
18. [Testing Instructions](#testing-instructions)
19. [Production Build Instructions](#production-build-instructions)
20. [Deployment Architecture](#deployment-architecture)
    - [Render Backend Deployment](#render-backend-deployment)
    - [Netlify Frontend Deployment](#netlify-frontend-deployment)
21. [Environment Variables](#environment-variables)
22. [API & WebSocket Documentation](#api--websocket-documentation)
23. [Test Results](#test-results)
24. [Limitations](#limitations)
25. [Future Scope](#future-scope)
26. [Team Information](#team-information)

---

## Problem Statement Summary

- **Problem Statement ID**: **26181**
- **Title**: *A secure, AI-powered Personal Health Companion that delivers real-time, privacy-preserving health monitoring and early warning capabilities, helping individuals recognize health risks before they become emergencies.*
- **Core Challenge**: Modern health emergencies—such as silent cardiac events, sudden impact falls, dehydration, acute heat exhaustion, and exposure to toxic post-disaster air—often strike with little warning. Existing consumer fitness wearables are reactive, cloud-dependent, privacy-invasive, and fail to synthesize physiological biometrics with ambient environmental stressors.

---

## Project Objective

To architect and deploy an end-to-end, edge-first, AI-driven Personal Health Companion that:
1. Continuously tracks multi-modal biological and environmental signals at 2 Hz.
2. Evaluates early-warning risk levels using a hybrid 4-tier risk classification engine (Normal, Elevated, Warning, Critical).
3. Detects complex multi-factor hazards (e.g., heat-stroke risk combining high humidity, elevated ambient heat, and rising core body temperature).
4. Dispatches actionable medical countermeasures and triggers a 15-second emergency SOS workflow during life-threatening events.
5. Operates in an offline-capable, privacy-preserving manner without requiring raw biometrics to be harvested by cloud servers.

---

## Proposed Solution

VITA-BAND AI solves these challenges with a three-layer cyber-physical architecture:
- **Perception Layer (Hardware / Synthetic Stream)**: Generates multi-channel biosignals (ECG, PPG, EMG, GSR, 3-axis Accelerometer) and environmental metrics (ambient temperature, humidity, air quality).
- **Intelligence Layer (Edge AI Gateway)**: Digital signal filtering (Butterworth 0.5–45 Hz bandpass + 50 Hz notch), feature extraction (HRV, RMSSD, EMG RMS power, NOAA Heat Index), and dual-tier anomaly scoring (heuristics + PyTorch/TFLite neural inference).
- **Interaction Layer (Mission-Control UI)**: A high-aesthetic, dark glassmorphic React 19 dashboard with live ECG sweeps, real-time gauges, 8-scenario simulation controls, and emergency override mechanisms.

---

## Key Features

- **Continuous 2 Hz Telemetry**: Sub-second physiological updates streamed over resilient WebSockets.
- **Dynamic ECG & EMG Waveforms**: 100-sample live buffer rendered on HTML5 canvas with realistic P-Q-R-S-T complexes and muscle power bursts.
- **NOAA Apparent Heat Index Calculation**: Evaluates National Oceanic and Atmospheric Administration heat-stress equations to warn against hyperthermia before clinical heatstroke sets in.
- **Acute Fall Impact Detection**: Vector magnitude thresholding (`sqrt(x^2 + y^2 + z^2) > 2.8g`) paired with post-fall immobility verification.
- **4-Tier Risk Categorization**: `NORMAL` (0–24), `ELEVATED` (25–44), `WARNING` (45–69), and `CRITICAL` (70–100).
- **15-Second Emergency Countdown**: Visual & audio alert banner allowing conscious users to cancel false alarms before SMS/ambulance dispatch.
- **1-Click Clinical Simulation Matrix**: 8 validated scenarios executable from the UI or REST API to demonstrate diverse health states.
- **Zero-Cloud Privacy**: Biometric calculations occur entirely locally on the companion gateway; only encrypted emergency alerts leave the device.

---

## System Architecture

```
+-------------------------------------------------------------------------------------------------+
|                                    PERCEPTION / SENSOR LAYER                                    |
|   MAX30102 (HR/SpO2) | AD8232 (ECG) | MyoWare (EMG) | MPU6050 (IMU) | DHT22 | MQ-135 Gas       |
|            [In Hackathon Demo: High-Fidelity Synthetic Simulation Engine @ 2 Hz]                |
+-----------------------------------------------+-------------------------------------------------+
                                                | Real-time Telemetry Frame
                                                v
+-------------------------------------------------------------------------------------------------+
|                                   BACKEND / EDGE-AI ENGINE                                      |
|                                                                                                 |
|   +--------------------------+    +--------------------------+    +--------------------------+  |
|   |   DSP Preprocessing      | -> |    Feature Extraction    | -> |   Hybrid Risk Engine     |  |
|   |  - 0.5-45 Hz Bandpass    |    |  - HRV (RMSSD, SDNN)     |    |  - Multi-Sensor Fusion   |  |
|   |  - 50 Hz Notch Filter    |    |  - NOAA Heat Index       |    |  - Heuristic Rules +     |  |
|   |  - Outlier Clamp         |    |  - EMG Mean Power / RMS  |    |    PyTorch Neural Net    |  |
|   +--------------------------+    +--------------------------+    +--------------------------+  |
|                                                                                 |               |
|                                                                                 v               |
|   +--------------------------+    +--------------------------+    +--------------------------+  |
|   |   SQLite History Engine  |    |   Emergency Dispatch     |    |  Stream Broadcaster      |  |
|   |  - Encrypted storage     |    |  - 15s Countdown Timer   |    |  - WebSocket Manager     |  |
|   |  - JSON/CSV Export       |    |  - Contact: +91 987654...|    |  - 2 Hz Push Telemetry   |  |
|   +--------------------------+    +--------------------------+    +--------------------------+  |
+-----------------------------------------------+-------------------------------------------------+
                                                | ws:// (Local) or wss:// (Production)
                                                v
+-------------------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER (UI)                                      |
|                           React 19 + Vite 6 + Tailwind Glassmorphism                            |
|                                                                                                 |
|   [ Live Vitals Cards ]    [ Sweeping ECG Canvas ]   [ Environmental Heat Widget ]              |
|   [ Risk Meter (0-100) ]   [ Simulation Selector ]   [ Emergency 15s SOS Modal ]                |
+-------------------------------------------------------------------------------------------------+
```

---

## Frontend Architecture

- **Framework**: React 19 (Functional Components, Custom Hooks)
- **Bundler**: Vite 6 (Optimized production chunking, Hot Module Replacement)
- **Styling**: Vanilla Modern CSS + Glassmorphism (`backdrop-filter: blur(16px)`), curated HSL dark palette (`#0B0F17` base with `#00D26A` Emerald and `#FF3B30` Crimson accents)
- **Key Modules**:
  - [`frontend/src/services/api.js`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/frontend/src/services/api.js): Centralized REST client with automatic `VITE_API_URL` stripping and fallback handling.
  - [`frontend/src/services/websocket.js`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/frontend/src/services/websocket.js): Resilient WebSocket client with automatic exponential backoff reconnection, heartbeat keepalive, and `wss://` derivation.
  - [`frontend/src/components/WaveformDisplay.jsx`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/frontend/src/components/WaveformDisplay.jsx): High-performance HTML5 Canvas ECG trace drawer.
  - [`frontend/src/components/RiskCard.jsx`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/frontend/src/components/RiskCard.jsx): Real-time gauge and categorical indicator.
  - [`frontend/src/components/EmergencyAlert.jsx`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/frontend/src/components/EmergencyAlert.jsx): Countdown modal with alert acknowledgment and cancellation.

---

## Backend Architecture

- **Framework**: FastAPI 0.110+ on Python 3.11
- **ASGI Server**: Uvicorn with standard uvloop and WebSockets
- **Key Routers**:
  - `GET /health`: Microservice health check and uptime.
  - `GET /api/sensors/latest`: Latest 2 Hz multi-sensor reading.
  - `GET /api/sensors/history`: Historic vital time-series for trend charts.
  - `GET /api/sensors/export`: CSV and JSON telemetry export.
  - `GET /api/risk/current`: Current multi-sensor risk assessment.
  - `GET /api/recommendations`: Actionable clinical guidance steps.
  - `POST /api/simulation/start`: Trigger any of the 8 validation scenarios.
  - `POST /api/simulation/stop`: Revert to normal baseline.
  - `POST /api/alerts/test`: Trigger emergency simulation test.
  - `POST /api/alerts/acknowledge`: Acknowledge and cancel emergency countdown.
  - `GET /ws/health-stream`: Continuous real-time bi-directional streaming endpoint.

---

## AI / Risk Engine & Anomaly Detection

Located in [`ai/risk_detection/engine.py`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/ai/risk_detection/engine.py):
1. **Signal Preprocessing**:
   - Outlier rejection and physiological boundary clamping.
   - 2nd-order Butterworth bandpass filter (0.5 Hz – 45 Hz) for raw ECG/EMG de-noising.
   - 50 Hz powerline notch filtering.
2. **Feature Extraction**:
   - Time-domain HRV: Mean RR interval, RMSSD, and SDNN.
   - Muscular fatigue: EMG root-mean-square (RMS) amplitude and frequency zero-crossing rate.
   - Environmental heat load: NOAA Rothfusz apparent temperature formulation.
3. **Dual-Tier Risk Classification**:
   - **Tier 1 (Clinical Heuristics)**: Immediate flags for severe hypoxemia ($SpO_2 < 85\%$), tachycardia ($HR > 140\text{ BPM}$), bradycardia ($HR < 45\text{ BPM}$), core hyperthermia ($T > 39.5^\circ\text{C}$), and fall impact ($> 2.8g$).
   - **Tier 2 (ML Inference)**: PyTorch Feed-Forward Neural Network (`ai/models/base_model.py`) fusing multi-dimensional biometrics with ambient heat index to compute composite risk scores ($0.0 - 100.0$).

---

## WebSocket Real-Time Communication

- **Endpoint**: `/ws/health-stream`
- **Protocol**: Raw JSON framing with bidirectional keepalive protocol (`ping`/`pong`).
- **Telemetry Frequency**: 2 Hz continuous broadcast (500 ms intervals).
- **Payload Schema**:
  ```json
  {
    "timestamp": "2026-09-23T13:00:00.000Z",
    "scenario": "NORMAL",
    "biometrics": {
      "heart_rate": 72.4,
      "spo2": 98.5,
      "temperature": 36.85,
      "galvanic_skin_response": 2.1,
      "emg_amplitude": 0.12,
      "ecg_buffer": [0.0, 0.05, 0.85, -0.2, 0.0]
    },
    "environmental": {
      "ambient_temperature": 24.5,
      "humidity": 45.0,
      "air_quality_index": 42.0,
      "heat_index": 24.8
    },
    "risk": {
      "score": 10.0,
      "level": "NORMAL",
      "detected_risks": [],
      "contributing_factors": []
    },
    "active_alert": false
  }
  ```

---

## Environmental Monitoring & Heat Index Fusion

The system incorporates ambient context using the NOAA National Weather Service Heat Index equation:
$$\text{HI} = -42.379 + 2.04901523 T + 10.14333127 R - 0.22475541 T R - \dots$$
When ambient heat exceeds $35^\circ\text{C}$ and relative humidity exceeds $70\%$, the apparent heat index climbs above $42^\circ\text{C}$. The AI risk engine fuses this environmental danger with the wearer's heart rate and core temperature to flag **Heat Stress / Heat Exhaustion** before dangerous clinical collapse occurs.

---

## Disaster-Specific Health Alerts

In disaster zones (earthquake rubble, flood zones, chemical spills, forest fires), VITA-BAND AI provides distinct warning modalities:
- **Toxic Air / Smoke Inhalation**: High AQI ($> 150$) paired with dipping $SpO_2$ triggers an urgent particulate advisory.
- **Dehydration in Arid Disaster Environments**: Prolonged high GSR + elevated heart rate with low ambient humidity ($< 20\%$) flags dehydration risk.
- **Physical Trapping / Immobility**: Accelerometer zero-motion combined with high EMG stress flags potential entrapment under debris.

---

## Emergency Assistance & Countdown Flow

1. **Detection**: Fall impact vector ($> 2.8g$) or Critical Vitals ($SpO_2 < 85\%$, $HR > 150$) triggers an emergency state.
2. **Visual & Auditory Warning**: The dashboard displays a red pulsating emergency banner.
3. **15-Second Grace Countdown**: The user has 15 seconds to tap **"I'm OK — Cancel Alert"**.
4. **Automated Dispatch**: If unacknowledged after 15 seconds, the emergency event is logged and transmitted to the registered emergency contact (`+91 9876543210`) with GPS coordinates and vital telemetry.

---

## Privacy-Preserving / Edge-AI Design

- **Local Execution**: All signal filtering, feature extraction, and risk neural inference occur directly on the gateway/companion device.
- **No Third-Party Cloud Data Mining**: Raw PPG/ECG waveforms never leave the local companion device.
- **Encrypted Local Storage**: SQLite databases store historical vital summaries encrypted at rest.
- **Minimalist Emergency Egress**: In an emergency dispatch, only essential triage data (time, location, primary risk category) is transmitted.

---

## 8 Validated Simulation Scenarios

The simulator executes 8 distinct physiological states, validated across all 9 processing stages:

| # | Scenario Key | Description | Target Risk Level | Primary Triggers |
| :-: | :--- | :--- | :-: | :--- |
| **1** | `NORMAL` | Healthy resting vitals | `NORMAL` (10/100) | HR 72 BPM, SpO2 98.5%, Temp 36.8°C |
| **2** | `HEAT_STRESS` | High heat + humidity + rising temp | `CRITICAL` (100/100) | Temp 39.7°C, Humidity 86%, Heat Index >45°C |
| **3** | `DEHYDRATION` | High HR in dry environment | `WARNING` (55/100) | HR 122 BPM, Humidity 17%, Temp 38.4°C |
| **4** | `FATIGUE` | Muscle exhaustion & tremors | `WARNING` (45/100) | High EMG RMS power, unsteady motion |
| **5** | `ABNORMAL_VITALS` | Tachycardia + severe hypoxemia | `CRITICAL` (95/100) | HR 148 BPM, SpO2 87.6% |
| **6** | `FALL` | Acute impact & immobility | `CRITICAL` (95/100) | Fall impact vector spike, fall_flag=True |
| **7** | `RESPIRATORY_RISK`| Hypoxia / acute lung distress | `CRITICAL` (95/100) | SpO2 80.6%, HR 131 BPM |
| **8** | `ENVIRONMENTAL_STRESS` | Extreme ambient hazard | `CRITICAL` (80/100) | Ambient 44.5°C, Humidity 94.8% |

---

## Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Gunicorn, WebSockets, Pydantic v2
- **Data & AI**: PyTorch 2.2, SciPy 1.12, NumPy 1.26
- **Frontend**: React 19, Vite 6, Lucide React, HTML5 Canvas API
- **Deployment & Containers**: Docker, Render Blueprint (`render.yaml`), Netlify (`netlify.toml`), Procfile
- **Testing**: Pytest, Httpx, Node.js WebSocket client

---

## Project Folder Structure

```
VITA-BAND-AI/
├── .env.example                    # Backend environment variable template
├── .gitignore                      # Watertight exclusions for Python, Node, DB, secrets
├── Dockerfile.backend              # Multi-stage production container
├── Procfile                        # Cloud process definition (Render/Railway/Heroku)
├── README.md                       # Master SIH evaluation documentation
├── REQUIREMENTS_TRACEABILITY.md    # 26-point SIH requirement compliance matrix
├── docker-compose.yml              # Multi-service local container runner
├── netlify.toml                    # Root Netlify build & SPA routing configuration
├── package.json                    # Root orchestration package scripts
├── pytest.ini                      # Pytest discovery configuration
├── render.yaml                     # Render infrastructure-as-code blueprint
├── requirements.txt                # Production Python dependencies
├── ai/                             # Core AI, ML models, and DSP pipelines
│   ├── feature_engineering/        # HRV, EMG RMS, and NOAA heat index calculators
│   ├── models/                     # PyTorch Feed-Forward Neural Net & TFLite exporter
│   ├── preprocessing/              # Butterworth bandpass & 50Hz notch filters
│   ├── recommendation/             # Clinical countermeasure & protocol generator
│   └── risk_detection/             # Hybrid heuristic + ML risk assessment engine
├── backend/                        # FastAPI REST API & WebSocket server
│   ├── alerts/                     # 15s emergency countdown & contact dispatcher
│   ├── api/                        # Modular REST routes (health, sensors, risk, sim)
│   ├── config.py                   # Dynamic configuration & CORS manager
│   ├── main.py                     # Application entrypoint & ASGI lifecycle
│   ├── models/                     # Pydantic telemetry & schema validation
│   ├── simulation/                 # 8-scenario deterministic biometric synthesizer
│   ├── storage/                    # SQLite telemetry history & export engine
│   └── websocket/                  # StreamManager broadcast engine
├── docs/                           # Architecture specs & verification reports
│   ├── AI_VALIDATION_REPORT.md     # 8-scenario comprehensive test report
│   ├── DEPLOYMENT.md               # Step-by-step public cloud deployment guide
│   └── ...                         # System, hardware, and privacy docs
├── frontend/                       # React 19 + Vite 6 Dashboard
│   ├── .env.example                # Netlify frontend environment variable template
│   ├── netlify.toml                # Frontend subdirectory deployment config
│   ├── package.json                # Frontend dependencies
│   ├── public/                     # Static assets & Netlify _redirects
│   ├── src/                        # React UI components & streaming clients
│   └── vite.config.js              # Vite server & dev reverse proxy
├── hardware/                       # Physical circuit schematics & ESP32 firmware
│   ├── circuit-diagram.md          # Wiring diagrams for MAX30102, AD8232, MPU6050
│   └── esp32_firmware.ino          # ESP32 C++ sensor acquisition sketch
├── scripts/                        # Automated validation & integration test suites
│   ├── test_frontend_ws_client.mjs # Frontend client lifecycle test
│   ├── validate_8_scenarios.py     # End-to-end 8-scenario AI test runner
│   └── websocket_integration_test.py # Live WebSocket integration test suite
└── tests/                          # 25-test unit & integration suite
    ├── ai/                         # DSP and AI unit tests
    ├── backend/                    # REST API endpoint tests
    ├── integration/                # End-to-end hackathon demo tests
    └── websocket/                  # WebSocket protocol & broadcast tests
```

---

## Local Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### Backend Setup

```bash
# 1. Clone repository
git clone <your-repository-url>
cd "VITA BAND AI"

# 2. Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Start backend server (0.0.0.0:8000)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at `http://127.0.0.1:8000/docs`.

### Frontend Setup

```bash
# 1. In a new terminal, navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment (optional in local dev)
cp .env.example .env

# 4. Start Vite dev server
npm run dev -- --host 127.0.0.1 --port 3000
```
Open your browser to `http://127.0.0.1:3000`.

---

## Testing Instructions

Run the full testing matrix from the project root:

```bash
# 1. Run all Pytest backend & unit tests (25 tests)
python -m pytest tests/ -v

# 2. Run live WebSocket integration test suite (6 tests)
python scripts/websocket_integration_test.py

# 3. Run frontend WebSocket client lifecycle test (5 tests)
node scripts/test_frontend_ws_client.mjs

# 4. Run end-to-end AI 8-scenario validation suite (8 scenarios / 72 checks)
python scripts/validate_8_scenarios.py
```

---

## Production Build Instructions

To validate the frontend for production deployment:

```bash
cd frontend
npm run build
```
Build output is saved to `frontend/dist/` with optimized minification and gzip compression. To preview the production bundle locally:
```bash
npm run preview -- --port 3000
```

---

## Deployment Architecture

```
Netlify Edge CDN (Frontend)        Render Cloud (FastAPI Backend)
https://<app>.netlify.app   -----> https://<backend>.onrender.com (REST)
                            -----> wss://<backend>.onrender.com/ws/health-stream (WSS)
```

### Render Backend Deployment
1. Log in to [render.com](https://render.com) and click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configuration:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `CORS_ORIGINS`: `*` (or your Netlify domain)
   - `OPERATION_MODE`: `DEMO`
5. Click **Deploy Web Service** and note your public URL (`https://<your-backend>.onrender.com`).

### Netlify Frontend Deployment
1. Log in to [netlify.com](https://netlify.com) and click **Add new site** -> **Import an existing project**.
2. Select your repository. Netlify reads [`netlify.toml`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/netlify.toml) automatically:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
3. Add Environment Variables:
   - `VITE_API_URL`: `https://<your-backend>.onrender.com`
   - `VITE_WS_URL`: `wss://<your-backend>.onrender.com/ws/health-stream`
4. Click **Deploy Site**.

*For complete deployment troubleshooting, refer to [`docs/DEPLOYMENT.md`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/docs/DEPLOYMENT.md).*

---

## Environment Variables

### Backend (`.env`)
```ini
HOST=0.0.0.0
PORT=8000
PROJECT_NAME="VITA-BAND AI"
VERSION="1.0.0"
DEBUG=false
OPERATION_MODE=DEMO
CORS_ORIGINS="*"
PRIMARY_EMERGENCY_CONTACT="+91 9876543210"
EMERGENCY_COUNTDOWN_SEC=15
DATABASE_PATH="vita_band.db"
DEFAULT_SIMULATION_INTERVAL_SEC=0.5
SIMULATION_NOISE_LEVEL=0.05
```

### Frontend (`frontend/.env`)
```ini
VITE_API_URL=https://<your-backend>.onrender.com
VITE_WS_URL=wss://<your-backend>.onrender.com/ws/health-stream
```

---

## API & WebSocket Documentation

- **Swagger Interactive UI**: Available at `http://localhost:8000/docs` or `https://<your-backend>/docs`.
- **ReDoc Interactive UI**: Available at `http://localhost:8000/redoc`.
- **Key REST Endpoints**:
  - `GET /health` -> System health and client counter.
  - `GET /api/sensors/latest` -> Real-time biological and ambient readings.
  - `GET /api/risk/current` -> Current composite risk assessment.
  - `POST /api/simulation/start` -> `{ "scenario": "HEAT_STRESS", "duration_seconds": 60, "severity": 0.85 }`
  - `POST /api/simulation/stop` -> Restores normal baseline vitals.
  - `POST /api/alerts/acknowledge` -> Dismisses active countdown.

---

## Test Results

All test suites pass with **100% success rate (44/44 tests passing)**:

```
======================================================================
TEST SUITE SUMMARY
======================================================================
1. Pytest Unit & Integration Suite:      25 / 25 PASSED  (100%)
2. Live WebSocket Integration Suite:       6 /  6 PASSED  (100%)
3. Frontend WebSocket Lifecycle Suite:     5 /  5 PASSED  (100%)
4. AI 8-Scenario E2E Validation:           8 /  8 PASSED  (72/72 sub-checks)
----------------------------------------------------------------------
TOTAL TESTS PASSED:                      44 / 44 PASSED  (100%)
FRONTEND PRODUCTION BUILD:                SUCCEEDED (0 errors, 2.50s)
======================================================================
```

*Detailed scenario trace data is documented in [`docs/AI_VALIDATION_REPORT.md`](file:///c:/Users/deeps/OneDrive/VITA%20BAND%20AI/docs/AI_VALIDATION_REPORT.md).*

---

## Limitations

1. **Simulated Telemetry**: Physical wearable hardware connection is currently emulated using the deterministic simulation engine. Real-world noisy sensor artifacts may require adaptive threshold fine-tuning.
2. **Contact Dispatch Simulation**: Emergency contact notifications are currently dispatched via mock logging and database records rather than paid carrier SMS gateways (Twilio/Infobip).
3. **Single User Session**: The prototype dashboard tracks one primary individual profile per companion instance. Multi-patient hospital fleet management is planned for future iterations.

---

## Future Scope

1. **Hardware Fabrication**: 3D-printed ergonomic wristband housing integrating the MAX30102, AD8232, and ESP32-C3 microcontroller.
2. **Federated Learning**: Enable edge models to learn across anonymous user devices without centralizing private medical datasets.
3. **Cellular NB-IoT / LoRaWAN Fallback**: Enable emergency message transmission in remote disaster zones when cellular and WiFi infrastructures are down.
4. **ABDM / FHIR Compliance**: Standardize health summary records according to the Ayushman Bharat Digital Mission (ABDM) standards.

---

## Team Information

- **Team Name**: **ALPHA MECHS**
- **Smart India Hackathon (SIH) 2026**
- **Problem Statement ID**: **26181**
- **Project Name**: **VITA-BAND AI**

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
