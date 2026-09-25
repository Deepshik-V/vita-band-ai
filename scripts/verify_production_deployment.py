"""
Production Deployment Verification Script for VITA-BAND AI
Validates Render Backend (REST + WebSocket) and Netlify Frontend.
"""
import sys
import os
import json
import time
import urllib.request
import asyncio

async def test_websocket(ws_url: str):
    import websockets
    print(f"[WS TEST] Connecting to {ws_url}...")
    async with websockets.connect(ws_url, close_timeout=5) as ws:
        print("[WS TEST] Connected successfully!")
        
        # Test ping/pong
        ping_msg = json.dumps({"action": "ping", "timestamp": time.time()})
        await ws.send(ping_msg)
        print("[WS TEST] Sent ping frame.")
        
        received_telemetry = False
        received_pong = False
        start_time = time.time()
        
        while time.time() - start_time < 8:
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(msg)
            msg_type = data.get("type")
            
            if msg_type == "telemetry":
                received_telemetry = True
                print(f"[WS TEST] Received telemetry frame:")
                print(f"   - Heart Rate: {data.get('vitals', {}).get('heart_rate')}")
                print(f"   - SpO2: {data.get('vitals', {}).get('spo2')}%")
                print(f"   - Temp: {data.get('vitals', {}).get('temperature_c')}C")
                print(f"   - Risk Score: {data.get('ai_analysis', {}).get('composite_risk_score')}")
                print(f"   - Risk Level: {data.get('ai_analysis', {}).get('risk_level')}")
            elif msg_type == "pong":
                received_pong = True
                print("[WS TEST] Received pong response.")
                
            if received_telemetry:
                break
                
        if not received_telemetry:
            raise RuntimeError("Did not receive telemetry frame within timeout")
        print("[WS TEST] PASS: WebSocket streaming verified!")

def test_rest(api_url: str):
    clean_url = api_url.rstrip("/")
    endpoints = [
        ("/", [200]),
        ("/health", [200]),
        ("/docs", [200]),
        ("/api/sensors/latest", [200]),
        ("/api/risk/current", [200]),
        ("/api/recommendations", [200]),
    ]
    
    print(f"\n[REST TEST] Testing endpoints on {clean_url}:")
    for ep, ok_codes in endpoints:
        full_url = f"{clean_url}{ep}"
        req = urllib.request.Request(full_url, headers={"User-Agent": "VitaBand-Verification/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8")
                if status in ok_codes:
                    print(f"  [OK] {ep:25} -> HTTP {status} (Length: {len(body)} bytes)")
                else:
                    print(f"  [FAIL] {ep:25} -> HTTP {status}")
                    return False
        except Exception as e:
            print(f"  [FAIL] {ep:25} -> Error: {e}")
            return False
            
    # Test simulation endpoint
    sim_url = f"{clean_url}/api/simulation/start"
    print(f"  [TEST] POST /api/simulation/start (HEAT_STRESS)...")
    payload = json.dumps({"scenario": "HEAT_STRESS", "duration_seconds": 10, "severity": 0.8}).encode("utf-8")
    req = urllib.request.Request(sim_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  [OK] POST /api/simulation/start -> {data.get('status')}: {data.get('message')}")
    except Exception as e:
        print(f"  [FAIL] POST /api/simulation/start -> {e}")
        return False
        
    stop_url = f"{clean_url}/api/simulation/stop"
    print(f"  [TEST] POST /api/simulation/stop...")
    req = urllib.request.Request(stop_url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  [OK] POST /api/simulation/stop -> {data.get('status')}")
    except Exception as e:
        print(f"  [FAIL] POST /api/simulation/stop -> {e}")
        return False
        
    print("[REST TEST] PASS: All REST endpoints verified!")
    return True

def test_frontend(frontend_url: str):
    clean_url = frontend_url.rstrip("/")
    print(f"\n[FRONTEND TEST] Checking {clean_url}:")
    req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8")
            if status == 200:
                print(f"  [OK] Frontend HTTP {status}")
                if "VITA-BAND AI" in body or "root" in body:
                    print("  [OK] Confirmed HTML contains VITA-BAND application entry point.")
                else:
                    print("  [WARN] Entry title not detected in initial HTML.")
                return True
            else:
                print(f"  [FAIL] Frontend returned status {status}")
                return False
    except Exception as e:
        print(f"  [FAIL] Frontend check error: {e}")
        return False

async def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_production_deployment.py <BACKEND_URL> [FRONTEND_URL]")
        print("Example: python verify_production_deployment.py https://vita-band-ai-backend.onrender.com https://vita-band-ai.netlify.app")
        sys.exit(1)
        
    backend_url = sys.argv[1].rstrip("/")
    frontend_url = sys.argv[2].rstrip("/") if len(sys.argv) > 2 else None
    
    ws_url = backend_url.replace("https://", "wss://").replace("http://", "ws://") + "/ws/health-stream"
    
    print("=" * 60)
    print("VITA-BAND AI PRODUCTION VERIFICATION")
    print(f"Backend URL:  {backend_url}")
    print(f"WebSocket:    {ws_url}")
    if frontend_url:
        print(f"Frontend URL: {frontend_url}")
    print("=" * 60)
    
    rest_ok = test_rest(backend_url)
    if not rest_ok:
        print("[VERIFICATION FAILED] REST checks failed.")
        sys.exit(1)
        
    try:
        await test_websocket(ws_url)
    except Exception as e:
        print(f"[VERIFICATION FAILED] WebSocket check failed: {e}")
        sys.exit(1)
        
    if frontend_url:
        fe_ok = test_frontend(frontend_url)
        if not fe_ok:
            print("[VERIFICATION FAILED] Frontend checks failed.")
            sys.exit(1)
            
    print("\n" + "=" * 60)
    print("ALL PRODUCTION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
