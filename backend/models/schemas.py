"""
Pydantic v2 data models and schemas for VITA-BAND AI
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class SimulationType(str, Enum):
    NORMAL = "NORMAL"
    HEAT_STRESS = "HEAT_STRESS"
    DEHYDRATION = "DEHYDRATION"
    FATIGUE = "FATIGUE"
    ABNORMAL_VITALS = "ABNORMAL_VITALS"
    FALL = "FALL"
    RESPIRATORY_RISK = "RESPIRATORY_RISK"
    ENVIRONMENTAL_STRESS = "ENVIRONMENTAL_STRESS"


class ActivityType(str, Enum):
    RESTING = "resting"
    WALKING = "walking"
    RUNNING = "running"
    UNSTEADY = "unsteady"
    FALL_IMPACT = "fall_impact"
    IMMOBILE = "immobile"


class SensorReading(BaseModel):
    """Raw or simulated multi-sensor telemetry stream packet"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_id: str = Field(default="ESP32-VITABAND-01")
    heart_rate: float = Field(..., ge=30.0, le=240.0, description="Heart rate in BPM (MAX30102)")
    spo2: float = Field(..., ge=60.0, le=100.0, description="Oxygen saturation % (MAX30102)")
    temperature: float = Field(..., ge=20.0, le=50.0, description="Body/skin temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Ambient humidity % (DHT22)")
    accel_x: float = Field(default=0.0, description="MPU6050 X acceleration in g")
    accel_y: float = Field(default=0.0, description="MPU6050 Y acceleration in g")
    accel_z: float = Field(default=1.0, description="MPU6050 Z acceleration in g")
    gyro_x: float = Field(default=0.0, description="MPU6050 X gyro in deg/s")
    gyro_y: float = Field(default=0.0, description="MPU6050 Y gyro in deg/s")
    gyro_z: float = Field(default=0.0, description="MPU6050 Z gyro in deg/s")
    activity: str = Field(default="resting")
    fall_detected: bool = Field(default=False)
    ecg_signal: List[float] = Field(default_factory=list, description="Recent 1-second ECG mV sample window")
    emg_signal: List[float] = Field(default_factory=list, description="Recent 1-second EMG uV sample window")
    ecg_status: str = Field(default="normal")
    emg_status: str = Field(default="normal")
    battery_percentage: int = Field(default=95, ge=0, le=100)


class HealthSnapshot(BaseModel):
    """Aggregated physiological state snapshot"""
    timestamp: str
    heart_rate: float
    spo2: float
    temperature: float
    humidity: float
    activity: str
    fall_detected: bool
    ecg_status: str
    emg_status: str
    battery_percentage: int = 95


class RiskAssessment(BaseModel):
    """AI-based risk detection and early warning classification"""
    timestamp: str
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Composite risk score (0-100)")
    detected_risks: List[str] = Field(default_factory=list)
    contributing_factors: Dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(default=0.92, ge=0.0, le=1.0)
    anomaly_flags: List[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    """Personalized early-warning and wellness preventive guidance"""
    id: str
    timestamp: str
    risk_category: str
    urgency: str  # low, medium, high, critical
    title: str
    guidance: List[str]
    disclaimer: str = "This is general preventive guidance and not a clinical diagnosis. Seek medical assistance for emergencies."


class AlertEvent(BaseModel):
    """Emergency alert notification and dispatch event"""
    alert_id: str
    timestamp: str
    alert_type: str  # FALL_DETECTED, CRITICAL_VITALS, SOS_MANUAL, HEAT_STROKE_RISK
    severity: RiskLevel
    message: str
    acknowledged: bool = False
    countdown_seconds: int = 15
    dispatched: bool = False
    target_contact: str = "+91 9876543210"


class SimulationScenario(BaseModel):
    """Simulation configuration and current status"""
    scenario_type: SimulationType = SimulationType.NORMAL
    active: bool = False
    duration_seconds: int = 60
    elapsed_seconds: int = 0
    severity: float = 0.8
    noise_level: float = 0.05
    baseline_hr: float = 75.0
    baseline_temp: float = 36.8
    baseline_spo2: float = 98.5


class SimulationStartRequest(BaseModel):
    scenario: SimulationType
    duration_seconds: int = Field(default=60, ge=10, le=600)
    severity: float = Field(default=0.8, ge=0.1, le=1.0)
    noise_level: float = Field(default=0.05, ge=0.0, le=0.5)


class AlertTestRequest(BaseModel):
    alert_type: str = "SOS_MANUAL"
    custom_message: Optional[str] = "Manual SOS alert triggered from companion dashboard."


class AlertAcknowledgeRequest(BaseModel):
    alert_id: str


class WebSocketTelemetryPayload(BaseModel):
    """Full streaming message delivered over /ws/health-stream"""
    timestamp: str
    vitals: HealthSnapshot
    ecg_buffer: List[float] = Field(default_factory=list)
    emg_buffer: List[float] = Field(default_factory=list)
    risk_assessment: RiskAssessment
    recommendations: List[Recommendation] = Field(default_factory=list)
    active_alert: Optional[AlertEvent] = None
    simulation_state: SimulationScenario
