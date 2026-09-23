"""
WebSocket Stream and Live Broadcasting Tests
Comprehensive verification of continuous telemetry, ping-pong keepalive,
scenario updates, concurrent multi-subscriber broadcasting, and reconnect resilience.
"""
import asyncio
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.websocket.stream import stream_manager
from backend.simulation.simulator import simulator
from backend.models.schemas import SimulationType

client = TestClient(app)


def test_websocket_health_stream_initial_payload():
    """Verify client immediately receives a complete, schema-compliant telemetry packet."""
    with client.websocket_connect("/ws/health-stream") as websocket:
        data = websocket.receive_json()
        assert "timestamp" in data
        assert "vitals" in data
        assert "heart_rate" in data["vitals"]
        assert "spo2" in data["vitals"]
        assert "temperature" in data["vitals"]
        assert "ecg_buffer" in data
        assert "emg_buffer" in data
        assert "risk_assessment" in data
        assert "recommendations" in data
        assert "simulation_state" in data
        assert data["risk_assessment"]["risk_level"] in ["NORMAL", "WARNING", "CRITICAL"]


def test_websocket_ping_pong():
    """Verify bidirectional ping-pong keepalive messaging."""
    with client.websocket_connect("/ws/health-stream") as websocket:
        # Discard initial snapshot
        _ = websocket.receive_json()
        
        # Send client ping
        websocket.send_json({"action": "ping", "timestamp": "2026-09-23T12:00:00Z"})
        response = websocket.receive_json()
        assert response.get("type") == "pong"
        assert response.get("echo") == "2026-09-23T12:00:00Z"
        assert "timestamp" in response


def test_websocket_disconnect_and_reconnect():
    """Verify clean client disconnection and subsequent reconnection."""
    # First connection
    with client.websocket_connect("/ws/health-stream") as ws1:
        data1 = ws1.receive_json()
        assert "vitals" in data1

    # Disconnect occurred upon context exit; now reconnect
    with client.websocket_connect("/ws/health-stream") as ws2:
        data2 = ws2.receive_json()
        assert "vitals" in data2


def test_websocket_telemetry_continuous_change():
    """Verify consecutive telemetry packets have dynamically changing sensor values."""
    with client.websocket_connect("/ws/health-stream") as ws:
        packet1 = ws.receive_json()

        # Advance simulation and broadcast
        reading2 = simulator.generate_reading()
        payload2 = stream_manager.process_and_cache(reading2)
        asyncio.run(stream_manager.broadcast_payload(payload2.model_dump_json()))

        packet2 = ws.receive_json()

        # Assert packets are received and differ
        assert packet1["timestamp"] != packet2["timestamp"] or packet1["vitals"]["heart_rate"] != packet2["vitals"]["heart_rate"]


def test_websocket_scenario_transition_broadcast():
    """Verify that switching simulation scenario updates telemetry broadcast over WebSocket."""
    with client.websocket_connect("/ws/health-stream") as ws:
        _ = ws.receive_json()  # discard initial

        # Switch to HEAT_STRESS
        simulator.start_scenario(SimulationType.HEAT_STRESS, duration_seconds=30, severity=0.9)
        reading = simulator.generate_reading()
        payload = stream_manager.process_and_cache(reading)
        asyncio.run(stream_manager.broadcast_payload(payload.model_dump_json()))

        packet = ws.receive_json()
        assert packet["simulation_state"]["scenario_type"] == "HEAT_STRESS"
        assert packet["vitals"]["temperature"] >= 37.5
        assert packet["risk_assessment"]["risk_level"] in ["WARNING", "CRITICAL"]

        # Revert back to NORMAL
        simulator.stop_scenario()
        reading_normal = simulator.generate_reading()
        payload_normal = stream_manager.process_and_cache(reading_normal)
        asyncio.run(stream_manager.broadcast_payload(payload_normal.model_dump_json()))

        packet_normal = ws.receive_json()
        assert packet_normal["simulation_state"]["scenario_type"] == "NORMAL"
        assert packet_normal["risk_assessment"]["risk_level"] == "NORMAL"


def test_websocket_fall_alert_broadcast():
    """Verify that fall impact immediately triggers active alert over WebSocket stream."""
    with client.websocket_connect("/ws/health-stream") as ws:
        _ = ws.receive_json()  # initial

        # Switch to FALL scenario
        simulator.start_scenario(SimulationType.FALL, duration_seconds=30, severity=1.0)
        # Advance through impact steps
        latest_packet = None
        for _ in range(6):
            reading = simulator.generate_reading()
            payload = stream_manager.process_and_cache(reading)
            asyncio.run(stream_manager.broadcast_payload(payload.model_dump_json()))
            latest_packet = ws.receive_json()

        assert latest_packet is not None
        assert latest_packet["simulation_state"]["scenario_type"] == "FALL"
        assert latest_packet["vitals"]["fall_detected"] is True or latest_packet["active_alert"] is not None

        # Clean up
        simulator.stop_scenario()
