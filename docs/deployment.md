# VITA-BAND AI: Production Public Deployment Guide

**Team**: ALPHA MECHS  
**Problem Statement**: SIH26198 — AI-Powered Personal Health Companion  
**System Architecture**: FastAPI (Backend) + React/Vite (Frontend) + PyTorch/SciPy (Edge AI Engine) + WebSockets

---

## Architecture Overview

```
                      +---------------------------------------+
                      |           VITA-BAND AI UI             |
                      |      Hosted on Netlify (CDN)          |
                      |   https://<your-app>.netlify.app      |
                      +-------------------+-------------------+
                                          |
                        +-----------------+-----------------+
                        | HTTPS REST                        | WSS WebSocket
                        | (CRUD / Simulation / Contact)     | (2 Hz Telemetry & ECG)
                        v                                   v
+---------------------------------------------------------------------------------+
|                         FastAPI Backend Web Service                              |
|           Hosted on Render / Railway / Fly.io / AWS ECS / VPS                   |
|                   https://<your-backend-service>.onrender.com                   |
|                   wss://<your-backend-service>.onrender.com/ws/health-stream    |
+---------------------------------------+-----------------------------------------+
                                        |
                    +-------------------+-------------------+
                    |                                       |
          +---------v---------+                   +---------v---------+
          |   Biometric AI    |                   |  Telemetry Stream |
          |   Risk Engine     |                   |  & Anomaly Detect |
          +-------------------+                   +-------------------+
```

---

## 1. How to Deploy the Backend

The backend is built with FastAPI and runs on Python 3.11+. It is container-ready (`Dockerfile.backend`) and includes a `Procfile` and `render.yaml`.

### Option A: Render (Recommended — Free Tier & Native WebSocket Support)

1. **Sign Up / Log In**: Go to [render.com](https://render.com) and sign in with GitHub.
2. **New Web Service**:
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository: `VITA-BAND-AI`.
3. **Configure Service Details**:
   - **Name**: `vita-band-ai-backend`
   - **Region**: Select closest to your audience (e.g., Singapore or Frankfurt/Oregon).
   - **Branch**: `main`
   - **Root Directory**: `.` (leave blank or enter `.`)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. **Environment Variables**:
   Under **Advanced** -> **Add Environment Variable**:
   - `PYTHON_VERSION`: `3.11.8`
   - `HOST`: `0.0.0.0`
   - `OPERATION_MODE`: `DEMO`
   - `CORS_ORIGINS`: `*` (or your Netlify URL once deployed)
   - `DEBUG`: `false`
5. **Click "Deploy Web Service"**.
6. Wait 2–3 minutes for the build to finish. Once live, Render displays a green checkmark with your public URL.

### Option B: Railway

1. Go to [railway.app](https://railway.app) and click **New Project** -> **Deploy from GitHub repo**.
2. Select your repository. Railway automatically detects `Procfile` and `requirements.txt`.
3. Go to **Settings** -> **Networking** -> **Generate Domain** (e.g. `vita-band-ai.up.railway.app`).
4. Set environment variables:
   - `PORT`: `8000` (or Railway default)
   - `OPERATION_MODE`: `DEMO`
   - `CORS_ORIGINS`: `*`

### Option C: Docker (Any Cloud Provider / VPS)

```bash
docker build -f Dockerfile.backend -t vita-band-backend .
docker run -d -p 8000:8000 -e PORT=8000 -e CORS_ORIGINS="*" vita-band-backend
```

---

## 2. How to Obtain the Public Backend URL

Once your backend deployment finishes:

1. Copy the public domain from your hosting dashboard:
   - Example: `https://vita-band-ai-backend.onrender.com`
2. Test the root health check in your browser or terminal:
   ```bash
   curl -I https://vita-band-ai-backend.onrender.com/health
   ```
   Expected response: `HTTP/2 200` with JSON `{"status":"ok","timestamp":"..."}`.
3. Test Swagger API documentation:
   Open `https://vita-band-ai-backend.onrender.com/docs` in your browser.

---

## 3. How to Configure Frontend Environment Variables

The React/Vite frontend relies on two environment variables:

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| `VITE_API_URL` | Public HTTPS REST API base URL (no trailing slash) | `https://vita-band-ai-backend.onrender.com` |
| `VITE_WS_URL` | *(Optional)* Public WSS WebSocket streaming URL | `wss://vita-band-ai-backend.onrender.com/ws/health-stream` |

> **Note**: If `VITE_WS_URL` is omitted, the frontend automatically derives `wss://<host>/ws/health-stream` directly from `VITE_API_URL`.

---

## 4. How to Deploy the Frontend to Netlify

### Method A: Netlify Git Continuous Deployment (Recommended)

1. Log into [netlify.com](https://www.netlify.com).
2. Click **Add new site** -> **Import an existing project** -> **GitHub**.
3. Select your repository: `VITA-BAND-AI`.
4. Netlify will detect `netlify.toml` automatically:
   - **Base directory**: `frontend` (or leave default if reading root `netlify.toml`)
   - **Build command**: `npm run build`
   - **Publish directory**: `dist` (or `frontend/dist` if base is root)
5. **Configure Environment Variables**:
   Under **Site configuration** -> **Environment variables**:
   - Click **Add a variable**.
   - Key: `VITE_API_URL`
   - Value: `https://<your-backend-app>.onrender.com`
   - Key: `VITE_WS_URL`
   - Value: `wss://<your-backend-app>.onrender.com/ws/health-stream`
6. Click **Deploy Site**.
7. Netlify assigns a URL like `https://vita-band-ai-alphamechs.netlify.app`.

### Method B: Netlify CLI Manual Deploy

If deploying manually from your terminal:

```bash
# 1. Build the production bundle with production environment variables
cd frontend
export VITE_API_URL="https://<your-backend-app>.onrender.com"
export VITE_WS_URL="wss://<your-backend-app>.onrender.com/ws/health-stream"
npm run build

# 2. Deploy dist directory via Netlify CLI
npx netlify-cli deploy --prod --dir=dist
```

---

## 5. How to Verify REST API Connectivity

From your terminal or browser, execute the following smoke tests against your public backend:

```bash
# 1. System Health
curl -s https://<your-backend-app>.onrender.com/health | jq .

# 2. Current Multi-Sensor Telemetry
curl -s https://<your-backend-app>.onrender.com/api/sensors/latest | jq .

# 3. AI Risk Assessment & Environmental Fusion
curl -s https://<your-backend-app>.onrender.com/api/risk/current | jq .

# 4. Trigger a Simulation Scenario (HEAT_STRESS)
curl -s -X POST https://<your-backend-app>.onrender.com/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "HEAT_STRESS", "duration_seconds": 30, "severity": 0.85}' | jq .
```

---

## 6. How to Verify WebSocket Connectivity

Public WebSockets require `wss://` (WebSocket Secure) over TLS.

You can verify connection using Python or `wscat`:

```bash
# Using python websockets client:
python -c "
import asyncio, websockets, json
async def test():
    uri = 'wss://<your-backend-app>.onrender.com/ws/health-stream'
    async with websockets.connect(uri) as ws:
        msg = await ws.recv()
        data = json.loads(msg)
        print('Connected! Received HR:', data['biometrics']['heart_rate'], 'BPM | Risk:', data['risk']['level'])
asyncio.run(test())
"
```

Expected output:
```
Connected! Received HR: 72.4 BPM | Risk: NORMAL
```

---

## 7. How to Verify the Live Dashboard

1. Open your Netlify public URL: `https://<your-site>.netlify.app`.
2. Inspect the top header status pills:
   - **System Status**: Should display green `System Normal` (or corresponding risk level).
   - **Connection**: Green pulsing dot with `Live Streaming`.
3. Observe real-time widgets:
   - **Heart Rate**: Updating continuously at 2 Hz (~70–75 BPM in normal mode).
   - **ECG Waveform Canvas**: Real-time sweeping biological trace.
   - **Environmental Widget**: Ambient temperature, humidity, and heat index updating.
4. Test Simulation Controls:
   - Click the **Simulation Control** dropdown in the dashboard.
   - Select **Heat Stress** -> Click **Trigger Scenario**.
   - Observe instantaneous UI reaction: risk level elevates to `CRITICAL`, alerts trigger, clinical guidance renders without refreshing page.
   - Click **Normal Baseline** to restore telemetry.

---

## 8. Common Deployment Problems and Fixes

### Issue 1: CORS Error in Browser Console (`Access-Control-Allow-Origin`)
- **Symptom**: Browser console shows `CORS policy: No 'Access-Control-Allow-Origin' header is present`.
- **Cause**: Backend `CORS_ORIGINS` does not allow your Netlify domain.
- **Fix**: In your backend hosting settings (e.g. Render Dashboard), add your Netlify domain to `CORS_ORIGINS`:
  ```
  CORS_ORIGINS=https://<your-app>.netlify.app,http://localhost:3000
  ```
  Or set `CORS_ORIGINS="*"` for open hackathon demo access.

### Issue 2: Mixed Content Error (`Mixed Content: The page was loaded over HTTPS...`)
- **Symptom**: Browser blocks HTTP requests or `ws://` connections.
- **Cause**: The Netlify frontend is served over HTTPS, but `VITE_API_URL` uses `http://` instead of `https://`.
- **Fix**: Always use `https://` for `VITE_API_URL` and `wss://` for `VITE_WS_URL`.

### Issue 3: WebSocket Connection Fails / Hangs
- **Symptom**: UI shows `Connecting...` or falls back to polling.
- **Cause**: Some edge CDN proxies do not support persistent WebSockets.
- **Fix**: Direct the WebSocket client to the origin backend (`wss://<your-backend>.onrender.com/ws/health-stream`) rather than routing WebSockets through Netlify CDN.

### Issue 4: Page Refresh Gives 404 on Netlify
- **Symptom**: Navigating directly to a deep link or refreshing returns `Page Not Found`.
- **Cause**: Static host attempting to locate a file path rather than falling back to `index.html`.
- **Fix**: Handled automatically by `netlify.toml` and `public/_redirects`:
  ```
  /*    /index.html   200
  ```

### Issue 5: Render Free Tier Cold Starts
- **Symptom**: The first API or WebSocket request takes 45–60 seconds to connect after 15 minutes of inactivity.
- **Cause**: Free tier web services spin down after inactivity.
- **Fix**: Ping the `/health` endpoint before your live SIH demo to wake up the container, or use a health-check monitor (e.g. UptimeRobot or cron job) every 10 minutes.
