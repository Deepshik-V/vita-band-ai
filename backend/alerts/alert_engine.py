"""
Emergency Alert Engine for VITA-BAND AI
Manages acute event detection, false-alarm cancellation countdowns,
SOS manual dispatches, alert acknowledgments, and mock notifications.
"""
from datetime import datetime
import uuid
from typing import Optional, List, Dict, Any

from backend.models.schemas import AlertEvent, RiskLevel, RiskAssessment, SensorReading
from backend.config import settings


class EmergencyAlertEngine:
    """Handles emergency detection, countdown timers, acknowledgment, and dispatch logging."""

    def __init__(self):
        self.active_alert: Optional[AlertEvent] = None
        self.alert_history: List[AlertEvent] = []
        self.emergency_contact: str = settings.PRIMARY_EMERGENCY_CONTACT

    def evaluate_triggers(self, reading: SensorReading, risk: RiskAssessment) -> Optional[AlertEvent]:
        """
        Evaluates real-time sensor streams and AI risk scores to determine
        if an acute emergency alert should be triggered.
        """
        now_str = datetime.utcnow().isoformat()

        # Auto-clear dispatched or expired alert if vitals have returned to NORMAL and no fall detected
        if self.active_alert and risk.risk_level == RiskLevel.NORMAL and not reading.fall_detected:
            if self.active_alert.dispatched or self.active_alert.countdown_seconds == 0:
                self.active_alert = None
                return None

        # Priority 1: Fall Detection (Always takes precedence over generic vitals)
        if reading.fall_detected:
            if not self.active_alert or self.active_alert.alert_type != "FALL_DETECTED":
                alert = AlertEvent(
                    alert_id=f"alt-{uuid.uuid4().hex[:8]}",
                    timestamp=now_str,
                    alert_type="FALL_DETECTED",
                    severity=RiskLevel.CRITICAL,
                    message="Sudden impact fall detected! Post-fall immobility observed.",
                    acknowledged=False,
                    countdown_seconds=settings.EMERGENCY_COUNTDOWN_SEC,
                    dispatched=False,
                    target_contact=self.emergency_contact,
                )
                self.active_alert = alert
                self.alert_history.append(alert)
                return alert

        # If an active unacknowledged alert exists, decrement countdown
        if self.active_alert and not self.active_alert.acknowledged:
            if self.active_alert.countdown_seconds > 0:
                self.active_alert.countdown_seconds -= 1
                if self.active_alert.countdown_seconds == 0:
                    self._dispatch_alert(self.active_alert)
            return self.active_alert

        # Priority 2: Critical Vitals Breach (Extreme Hypoxia or Cardiac Outlier)
        if risk.risk_level == RiskLevel.CRITICAL and risk.risk_score >= 80.0:
            alert = AlertEvent(
                alert_id=f"alt-{uuid.uuid4().hex[:8]}",
                timestamp=now_str,
                alert_type="CRITICAL_VITALS",
                severity=RiskLevel.CRITICAL,
                message=f"Critical physiological threshold breached (Score: {risk.risk_score:.0f}/100).",
                acknowledged=False,
                countdown_seconds=settings.EMERGENCY_COUNTDOWN_SEC,
                dispatched=False,
                target_contact=self.emergency_contact,
            )
            self.active_alert = alert
            self.alert_history.append(alert)
            return alert

        return None

    def trigger_test_alert(self, alert_type: str = "SOS_MANUAL", custom_message: str = None) -> AlertEvent:
        """Triggers a manual or test emergency event."""
        now_str = datetime.utcnow().isoformat()
        alert = AlertEvent(
            alert_id=f"alt-{uuid.uuid4().hex[:8]}",
            timestamp=now_str,
            alert_type=alert_type,
            severity=RiskLevel.CRITICAL,
            message=custom_message or "Manual SOS emergency alert triggered by user.",
            acknowledged=False,
            countdown_seconds=10,
            dispatched=False,
            target_contact=self.emergency_contact,
        )
        self.active_alert = alert
        self.alert_history.append(alert)
        return alert

    def acknowledge_alert(self, alert_id: str) -> Optional[AlertEvent]:
        """User cancels or acknowledges an active alert (cancels false alarm dispatch)."""
        if self.active_alert and self.active_alert.alert_id == alert_id:
            self.active_alert.acknowledged = True
            self.active_alert.countdown_seconds = 0
            ret = self.active_alert
            self.active_alert = None
            return ret
        return None

    def reset(self):
        """Clears active alert state (useful for test resets)."""
        self.active_alert = None

    def clear_active_alert(self):
        """Clears active alert state."""
        self.active_alert = None

    def _dispatch_alert(self, alert: AlertEvent) -> None:
        alert.dispatched = True
        print(f"[EMERGENCY_DISPATCH] [SAFE_MOCK] Alert {alert.alert_id} dispatched to {alert.target_contact}. Message: {alert.message}")


alert_engine = EmergencyAlertEngine()
