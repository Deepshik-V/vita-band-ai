"""
Real-Time WebSocket Stream Engine for VITA-BAND AI
Maintains active client connections and broadcasts physiological telemetry,
AI risk scores, recommendations, and emergency alerts at sub-second intervals.
"""
import asyncio
import json
from datetime import datetime
from typing import List, Set, Optional

from fastapi import WebSocket, WebSocketDisconnect

from backend.models.schemas import (
    SensorReading,
    HealthSnapshot,
    RiskAssessment,
    Recommendation,
    AlertEvent,
    WebSocketTelemetryPayload,
    SimulationScenario,
)
from backend.simulation.simulator import simulator
from ai.risk_detection.engine import RiskDetectionEngine
from ai.recommendation.engine import RecommendationEngine
from backend.alerts.alert_engine import alert_engine
from backend.storage.db import db_engine
from backend.config import settings


class StreamManager:
    """Manages active dashboard WebSocket subscribers and continuous data dissemination."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.risk_engine = RiskDetectionEngine()
        self.rec_engine = RecommendationEngine()
        self.latest_reading: Optional[SensorReading] = None
        self.latest_risk: Optional[RiskAssessment] = None
        self.latest_recommendations: List[Recommendation] = []
        self._streaming_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accepts and registers incoming client WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)

        # Immediately send fresh telemetry packet matching current simulation state upon connection
        reading = simulator.generate_reading()
        payload = self.process_and_cache(reading)
        try:
            await websocket.send_text(payload.model_dump_json())
        except Exception:
            pass

        print(f"[WS_CONNECT] Dashboard client connected. Total clients: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Unregisters disconnected client."""
        async with self._lock:
            self.active_connections.discard(websocket)
        print(f"[WS_DISCONNECT] Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_payload(self, payload):
        """Broadcasts JSON payload to all connected clients concurrently."""
        if not self.active_connections:
            return

        if isinstance(payload, str):
            json_text = payload
        elif hasattr(payload, "model_dump_json"):
            json_text = payload.model_dump_json()
        else:
            json_text = json.dumps(payload)

        async with self._lock:
            connections = list(self.active_connections)

        if not connections:
            return

        # Broadcast concurrently across all active clients
        tasks = [conn.send_text(json_text) for conn in connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        dead_connections = []
        for conn, res in zip(connections, results):
            if isinstance(res, Exception):
                dead_connections.append(conn)
                print(f"[WS_BROADCAST_DEAD] Removing disconnected client: {type(res).__name__}: {res}")

        if dead_connections:
            async with self._lock:
                for dead in dead_connections:
                    self.active_connections.discard(dead)


    def process_and_cache(self, reading: SensorReading) -> WebSocketTelemetryPayload:
        """Processes reading through AI, recommendation, alert, and persistence layers."""
        # 1. AI Risk Assessment
        risk = self.risk_engine.assess_reading(reading)
        
        # 2. Recommendations
        recs = self.rec_engine.generate_recommendations(risk)
        
        # 3. Emergency Alert Triggers
        alert = alert_engine.evaluate_triggers(reading, risk)

        # 4. Storage Persistence
        db_engine.save_snapshot(reading, risk)
        if alert:
            db_engine.save_alert(alert)

        # 5. Cache
        self.latest_reading = reading
        self.latest_risk = risk
        self.latest_recommendations = recs

        # 6. Assemble WebSocket Payload
        vitals = HealthSnapshot(
            timestamp=reading.timestamp.isoformat() if hasattr(reading.timestamp, "isoformat") else str(reading.timestamp),
            heart_rate=reading.heart_rate,
            spo2=reading.spo2,
            temperature=reading.temperature,
            humidity=reading.humidity,
            activity=reading.activity,
            fall_detected=reading.fall_detected,
            ecg_status=reading.ecg_status,
            emg_status=reading.emg_status,
            battery_percentage=reading.battery_percentage,
        )

        return WebSocketTelemetryPayload(
            timestamp=datetime.utcnow().isoformat(),
            vitals=vitals,
            ecg_buffer=reading.ecg_signal,
            emg_buffer=reading.emg_signal,
            risk_assessment=risk,
            recommendations=recs,
            active_alert=alert,
            simulation_state=simulator.get_status(),
        )

    async def start_background_loop(self):
        """Continuous background generator and broadcast loop."""
        while True:
            try:
                reading = simulator.generate_reading()
                payload = self.process_and_cache(reading)
                await self.broadcast_payload(payload.model_dump_json())
            except Exception as e:
                print(f"[STREAM_LOOP_ERROR] {e}")

            await asyncio.sleep(settings.DEFAULT_SIMULATION_INTERVAL_SEC)


stream_manager = StreamManager()
