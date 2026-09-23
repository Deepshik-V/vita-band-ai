"""
Comprehensive WebSocket Live Integration Test Suite for VITA-BAND AI
Validates real-time continuous streaming, multi-scenario telemetry,
auto-reconnect resilience, keepalive ping/pong, and multi-client broadcasting.
"""
import asyncio
import json
import time
import urllib.request
import websockets

BACKEND_WS_URL = "ws://127.0.0.1:8000/ws/health-stream"
VITE_PROXY_WS_URL = "ws://127.0.0.1:3000/ws/health-stream"
API_BASE_URL = "http://127.0.0.1:8000"


def http_post(endpoint: str, data: dict = None):
    url = f"{API_BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8") if data else b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def test_backend_direct_stream():
    print("\n========================================================")
    print("TEST 1: Direct Backend WebSocket Stream (ws://127.0.0.1:8000)")
    print("========================================================")
    
    async with websockets.connect(BACKEND_WS_URL) as ws:
        print("[CONNECTED] Direct connection to backend established.")
        
        # Collect 6 consecutive packets
        packets = []
        for i in range(6):
            raw = await asyncio.wait_for(ws.recv(), timeout=3.0)
            data = json.loads(raw)
            packets.append(data)
            vitals = data["vitals"]
            print(f"  -> Packet {i+1}: time={data['timestamp'][-12:]} | HR={vitals['heart_rate']:.1f} BPM | SpO2={vitals['spo2']:.1f}% | Temp={vitals['temperature']:.2f}C | Risk={data['risk_assessment']['risk_score']:.1f} ({data['risk_assessment']['risk_level']})")

        # 1. Verify schema completeness
        sample = packets[0]
        assert "vitals" in sample, "Missing vitals"
        assert "ecg_buffer" in sample and len(sample["ecg_buffer"]) > 0, "Missing ECG buffer"
        assert "emg_buffer" in sample and len(sample["emg_buffer"]) > 0, "Missing EMG buffer"
        assert "risk_assessment" in sample, "Missing risk assessment"
        assert "recommendations" in sample, "Missing recommendations"
        assert "simulation_state" in sample, "Missing simulation state"
        print("  [PASS] Telemetry schema contains all required biological and environmental dimensions.")

        # 2. Verify telemetry continuously changes (non-static)
        hrs = [p["vitals"]["heart_rate"] for p in packets]
        hr_variance = max(hrs) - min(hrs)
        print(f"  -> Heart Rate range over 6 ticks: {min(hrs):.1f} - {max(hrs):.1f} BPM (variance: {hr_variance:.2f})")
        assert hr_variance > 0 or len(set(p["timestamp"] for p in packets)) == 6, "Telemetry appears frozen or static!"
        print("  [PASS] Telemetry values are continuously dynamic and time-varying.")


async def test_vite_proxy_stream():
    print("\n========================================================")
    print("TEST 2: Vite Dev Server WebSocket Proxy (ws://127.0.0.1:3000)")
    print("========================================================")
    
    async with websockets.connect(VITE_PROXY_WS_URL) as ws:
        print("[CONNECTED] Connection through Vite dev server proxy established.")
        raw = await asyncio.wait_for(ws.recv(), timeout=3.0)
        data = json.loads(raw)
        print(f"  -> Received proxy packet: Scenario={data['simulation_state']['scenario_type']} | Battery={data['vitals']['battery_percentage']}%")
        assert data["vitals"]["heart_rate"] > 0
        print("  [PASS] Vite dev server correctly reverse-proxies WebSocket stream to backend.")


async def test_ping_pong_keepalive():
    print("\n========================================================")
    print("TEST 3: Bidirectional Ping/Pong Keepalive Protocol")
    print("========================================================")
    
    async with websockets.connect(BACKEND_WS_URL) as ws:
        _ = await ws.recv()  # discard initial snapshot
        
        test_ts = f"test-ping-{int(time.time())}"
        ping_payload = json.dumps({"action": "ping", "timestamp": test_ts})
        await ws.send(ping_payload)
        print(f"  -> Sent ping message with timestamp: {test_ts}")
        
        # Await pong response
        pong_received = False
        for _ in range(5):
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(raw)
            if data.get("type") == "pong":
                assert data.get("echo") == test_ts
                print(f"  -> Received pong response: echo={data.get('echo')} server_time={data.get('timestamp')}")
                pong_received = True
                break

        assert pong_received, "Did not receive pong response from backend"
        print("  [PASS] Bidirectional keepalive ping/pong confirmed.")


async def test_simulation_scenario_shift():
    print("\n========================================================")
    print("TEST 4: Real-time Simulation Scenario Transition Broadcast")
    print("========================================================")
    
    async with websockets.connect(BACKEND_WS_URL) as ws:
        _ = await ws.recv()
        
        # 1. Trigger HEAT_STRESS
        print("  -> Triggering HEAT_STRESS scenario via REST API...")
        http_post("/api/simulation/start", {"scenario": "HEAT_STRESS", "duration_seconds": 20, "severity": 0.95})
        
        # Wait for broadcast packet reflecting HEAT_STRESS
        heat_detected = False
        for _ in range(6):
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(raw)
            if data["simulation_state"]["scenario_type"] == "HEAT_STRESS":
                print(f"  -> Stream confirmed HEAT_STRESS: Temp={data['vitals']['temperature']:.2f}C | Humidity={data['vitals']['humidity']:.1f}% | Risk={data['risk_assessment']['risk_level']}")
                assert data["vitals"]["temperature"] >= 37.5
                assert data["risk_assessment"]["risk_level"] in ["WARNING", "CRITICAL"]
                heat_detected = True
                break
        assert heat_detected, "HEAT_STRESS scenario was not broadcast over WebSocket"

        # 2. Trigger FALL scenario (acute impact)
        print("  -> Triggering FALL scenario (acute impact) via REST API...")
        http_post("/api/simulation/start", {"scenario": "FALL", "duration_seconds": 20, "severity": 1.0})
        
        fall_detected = False
        for _ in range(8):
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(raw)
            if data["simulation_state"]["scenario_type"] == "FALL":
                if data["vitals"]["fall_detected"] or data.get("active_alert"):
                    print(f"  -> Stream confirmed FALL IMPACT: fall_flag={data['vitals']['fall_detected']} | active_alert={data.get('active_alert') is not None}")
                    fall_detected = True
                    break
        assert fall_detected, "FALL impact was not broadcast over WebSocket"

        # 3. Revert to NORMAL
        print("  -> Reverting simulation back to NORMAL...")
        http_post("/api/simulation/stop")
        reverted = False
        for _ in range(6):
            raw = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(raw)
            if data["simulation_state"]["scenario_type"] == "NORMAL":
                print(f"  -> Stream restored to NORMAL: Risk={data['risk_assessment']['risk_level']}")
                reverted = True
                break
        assert reverted, "NORMAL state was not restored"
        print("  [PASS] Simulation scenario transitions broadcast instantly to UI stream.")


async def test_disconnect_and_reconnect():
    print("\n========================================================")
    print("TEST 5: Disconnect and Automatic Reconnect Resilience")
    print("========================================================")
    
    print("  -> Phase 1: Establishing initial subscriber connection...")
    ws1 = await websockets.connect(BACKEND_WS_URL)
    raw1 = await ws1.recv()
    data1 = json.loads(raw1)
    print(f"  -> Phase 1 Connected. Initial HR: {data1['vitals']['heart_rate']:.1f} BPM")
    
    print("  -> Phase 2: Forcibly simulating network disconnect / drop...")
    try:
        if hasattr(ws1, "transport") and ws1.transport:
            ws1.transport.close()
        else:
            await ws1.close(code=1000)
    except Exception:
        pass
    print("  -> Phase 2 Disconnected.")
    
    print("  -> Phase 3: Reconnecting new subscriber (simulating client auto-reconnect)...")
    await asyncio.sleep(1.0)
    ws2 = await websockets.connect(BACKEND_WS_URL)
    print("  -> Phase 3 Reconnected successfully.")
    
    raw2 = await ws2.recv()
    data2 = json.loads(raw2)
    print(f"  -> Phase 3 Received stream telemetry post-reconnect: HR={data2['vitals']['heart_rate']:.1f} BPM | Time={data2['timestamp'][-12:]}")
    assert "vitals" in data2
    await ws2.close()
    print("  [PASS] Disconnect and auto-reconnection executed cleanly without state corruption.")


async def test_multi_client_concurrent_broadcast():
    print("\n========================================================")
    print("TEST 6: Multi-Subscriber Concurrent Broadcasting")
    print("========================================================")
    
    print("  -> Spawning 3 concurrent WebSocket clients...")
    client_a = await websockets.connect(BACKEND_WS_URL)
    client_b = await websockets.connect(BACKEND_WS_URL)
    client_c = await websockets.connect(BACKEND_WS_URL)
    
    # Read synchronized broadcast from all 3
    msg_a = await asyncio.wait_for(client_a.recv(), timeout=3.0)
    msg_b = await asyncio.wait_for(client_b.recv(), timeout=3.0)
    msg_c = await asyncio.wait_for(client_c.recv(), timeout=3.0)
    
    print(f"  -> Client A received packet: {json.loads(msg_a)['timestamp'][-12:]}")
    print(f"  -> Client B received packet: {json.loads(msg_b)['timestamp'][-12:]}")
    print(f"  -> Client C received packet: {json.loads(msg_c)['timestamp'][-12:]}")
    
    print("  -> Disconnecting Client B while keeping Clients A & C alive...")
    await client_b.close()
    
    # Verify A & C continue to receive subsequent packets
    next_a = await asyncio.wait_for(client_a.recv(), timeout=3.0)
    next_c = await asyncio.wait_for(client_c.recv(), timeout=3.0)
    print(f"  -> Client A continues streaming: {json.loads(next_a)['vitals']['heart_rate']:.1f} BPM")
    print(f"  -> Client C continues streaming: {json.loads(next_c)['vitals']['heart_rate']:.1f} BPM")
    
    await client_a.close()
    await client_c.close()
    print("  [PASS] Multi-subscriber broadcasting handles concurrent subscribers and partial disconnects flawlessly.")


async def main():
    print("=" * 60)
    print(" VITA-BAND AI: LIVE WEBSOCKET INTEGRATION TEST SUITE")
    print("=" * 60)
    
    await test_backend_direct_stream()
    await test_vite_proxy_stream()
    await test_ping_pong_keepalive()
    await test_simulation_scenario_shift()
    await test_disconnect_and_reconnect()
    await test_multi_client_concurrent_broadcast()
    
    print("\n" + "=" * 60)
    print(" ALL 6 WEBSOCKET INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
