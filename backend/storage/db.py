"""
Storage Abstraction Layer & Repository Pattern for VITA-BAND AI
Provides clean Data Access Object (DAO) / Repository interfaces (ITelemetryRepository, IAlertRepository)
with SQLite implementation and in-memory ring buffer fallback.
Enables transparent future migration to PostgreSQL / TimescaleDB without application refactoring.
"""
from abc import ABC, abstractmethod
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.config import settings
from backend.models.schemas import (
    SensorReading,
    RiskAssessment,
    AlertEvent,
    HealthSnapshot,
    Recommendation,
)


class ITelemetryRepository(ABC):
    """Abstract Repository Interface for physiological and environmental telemetry."""

    @abstractmethod
    def save_snapshot(
        self,
        reading: SensorReading,
        risk: RiskAssessment,
        recommendations: Optional[List[Recommendation]] = None,
        alert_state: Optional[str] = "NORMAL"
    ) -> None:
        """Persists a complete telemetry and risk assessment record."""
        pass

    @abstractmethod
    def get_recent_history(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Retrieves recent rolling health history."""
        pass


class IAlertRepository(ABC):
    """Abstract Repository Interface for emergency events and alerts."""

    @abstractmethod
    def save_alert(self, alert: AlertEvent) -> None:
        """Persists an acute emergency event."""
        pass

    @abstractmethod
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves emergency dispatch and audit history."""
        pass


class SQLiteStorageEngine(ITelemetryRepository, IAlertRepository):
    """
    Production-style SQLite implementation of Telemetry and Alert Repositories.
    Features:
    - Thread-safe connection handling
    - Dual persistence: fast in-memory ring buffer + persistent SQLite DB
    - Stores: timestamp, sensor values, risk score, risk level, detected condition, recommendation, alert state
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.memory_history: List[Dict[str, Any]] = []
        self.max_memory_history = 120  # Last 120 seconds in volatile memory
        self._init_sqlite()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_sqlite(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Telemetry history table adhering to full SIH requirements
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS telemetry_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        device_id TEXT,
                        heart_rate REAL,
                        spo2 REAL,
                        temperature REAL,
                        humidity REAL,
                        activity TEXT,
                        fall_detected INTEGER,
                        risk_level TEXT,
                        risk_score REAL,
                        detected_condition TEXT,
                        recommendation TEXT,
                        alert_state TEXT
                    )
                """)
                # Emergency alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alert_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE,
                        timestamp TEXT NOT NULL,
                        alert_type TEXT,
                        severity TEXT,
                        message TEXT,
                        acknowledged INTEGER,
                        dispatched INTEGER
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"[STORAGE_WARNING] SQLite init error ({e}), operating in memory.")

    def save_snapshot(
        self,
        reading: SensorReading,
        risk: RiskAssessment,
        recommendations: Optional[List[Recommendation]] = None,
        alert_state: Optional[str] = None
    ) -> None:
        """Saves telemetry point to both memory ring buffer and SQLite."""
        rec_summary = ""
        if recommendations and len(recommendations) > 0:
            rec_summary = recommendations[0].title

        cur_alert = alert_state or ("CRITICAL" if reading.fall_detected or risk.risk_score >= 80 else risk.risk_level.value)

        record = {
            "timestamp": reading.timestamp.isoformat() if hasattr(reading.timestamp, "isoformat") else str(reading.timestamp),
            "heart_rate": reading.heart_rate,
            "spo2": reading.spo2,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "activity": reading.activity,
            "fall_detected": reading.fall_detected,
            "risk_level": risk.risk_level.value,
            "risk_score": risk.risk_score,
            "detected_risks": risk.detected_risks,
            "recommendation": rec_summary,
            "alert_state": cur_alert,
        }

        # Update in-memory buffer
        self.memory_history.append(record)
        if len(self.memory_history) > self.max_memory_history:
            self.memory_history.pop(0)

        # Persist to SQLite
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO telemetry_records (
                        timestamp, device_id, heart_rate, spo2, temperature, humidity,
                        activity, fall_detected, risk_level, risk_score, detected_condition,
                        recommendation, alert_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record["timestamp"],
                    reading.device_id,
                    reading.heart_rate,
                    reading.spo2,
                    reading.temperature,
                    reading.humidity,
                    reading.activity,
                    1 if reading.fall_detected else 0,
                    record["risk_level"],
                    record["risk_score"],
                    json.dumps(record["detected_risks"]),
                    rec_summary,
                    cur_alert,
                ))
                conn.commit()
        except Exception:
            pass

    def save_alert(self, alert: AlertEvent) -> None:
        """Persists emergency alert event."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO alert_records (
                        alert_id, timestamp, alert_type, severity, message, acknowledged, dispatched
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp,
                    alert.alert_type,
                    alert.severity.value,
                    alert.message,
                    1 if alert.acknowledged else 0,
                    1 if alert.dispatched else 0,
                ))
                conn.commit()
        except Exception:
            pass

    def get_recent_history(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Returns recent telemetry snapshots from ring buffer or database."""
        if self.memory_history:
            return self.memory_history[-limit:]
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, heart_rate, spo2, temperature, humidity,
                           activity, fall_detected, risk_level, risk_score, detected_condition,
                           recommendation, alert_state
                    FROM telemetry_records
                    ORDER BY id DESC LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                results = []
                for row in reversed(rows):
                    results.append({
                        "timestamp": row[0],
                        "heart_rate": row[1],
                        "spo2": row[2],
                        "temperature": row[3],
                        "humidity": row[4],
                        "activity": row[5],
                        "fall_detected": bool(row[6]),
                        "risk_level": row[7],
                        "risk_score": row[8],
                        "detected_risks": json.loads(row[9]) if row[9] else [],
                        "recommendation": row[10],
                        "alert_state": row[11],
                    })
                return results
        except Exception:
            return []

    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent alerts."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT alert_id, timestamp, alert_type, severity, message, acknowledged, dispatched
                    FROM alert_records
                    ORDER BY id DESC LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [
                    {
                        "alert_id": r[0],
                        "timestamp": r[1],
                        "alert_type": r[2],
                        "severity": r[3],
                        "message": r[4],
                        "acknowledged": bool(r[5]),
                        "dispatched": bool(r[6]),
                    }
                    for r in rows
                ]
        except Exception:
            return []


# Maintain StorageEngine name for backward compatibility
StorageEngine = SQLiteStorageEngine
db_engine = SQLiteStorageEngine()
