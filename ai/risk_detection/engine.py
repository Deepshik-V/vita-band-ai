"""
AI Risk Detection Engine for VITA-BAND AI
Performs multi-sensor data fusion and classifies physiological/environmental risk.
"""
from datetime import datetime
from typing import Dict, Any, List

from backend.models.schemas import SensorReading, RiskAssessment, RiskLevel
from ai.preprocessing.signal_filter import (
    bandpass_filter,
    notch_filter,
    compute_emg_envelope,
    compute_accel_magnitude,
)
from ai.feature_engineering.extractors import (
    calculate_heat_index,
    calculate_hrv_metrics,
    calculate_emg_fatigue_index,
    extract_statistical_features,
)
from ai.models.base_model import BaselineHeuristicModel, BaseRiskModel


class RiskDetectionEngine:
    """
    Modular engine orchestrating preprocessing, feature extraction,
    and multi-modal risk scoring.
    """

    def __init__(self, model: BaseRiskModel = None):
        self.model = model or BaselineHeuristicModel()

    def assess_reading(self, reading: SensorReading) -> RiskAssessment:
        """Processes incoming SensorReading and yields RiskAssessment."""
        # 1. Preprocessing
        filtered_ecg = []
        if reading.ecg_signal and len(reading.ecg_signal) > 0:
            filtered_ecg = bandpass_filter(reading.ecg_signal)
            filtered_ecg = notch_filter(filtered_ecg)

        filtered_emg = []
        if reading.emg_signal and len(reading.emg_signal) > 0:
            filtered_emg = compute_emg_envelope(reading.emg_signal)

        accel_mag = compute_accel_magnitude(reading.accel_x, reading.accel_y, reading.accel_z)

        # 2. Feature Extraction
        # Estimate ambient temperature for apparent Heat Index calculation
        if reading.temperature >= 40.0:
            amb_temp = reading.temperature
        elif reading.temperature >= 38.0:
            amb_temp = 32.0 + (reading.temperature - 38.0) * 3.0
        else:
            amb_temp = 24.5 + max(0.0, reading.temperature - 36.8) * 2.0

        heat_idx = calculate_heat_index(amb_temp, reading.humidity)
        hrv_metrics = calculate_hrv_metrics(reading.heart_rate)
        emg_fatigue = calculate_emg_fatigue_index(filtered_emg if filtered_emg else reading.emg_signal)
        ecg_stats = extract_statistical_features(filtered_ecg if filtered_ecg else reading.ecg_signal)

        features = {
            "heart_rate": reading.heart_rate,
            "spo2": reading.spo2,
            "temperature": reading.temperature,
            "humidity": reading.humidity,
            "heat_index": heat_idx,
            "accel_magnitude": accel_mag,
            "fall_detected": reading.fall_detected,
            "emg_fatigue_index": emg_fatigue["fatigue_index"],
            "hrv_rmssd": hrv_metrics["rmssd_ms"],
        }

        # 3. Model Inference
        raw_level, risk_score, reasons = self.model.predict_risk(features)

        # 4. Multi-modal Anomaly & Specific Condition Tagging
        detected_risks: List[str] = []
        anomaly_flags: List[str] = []

        if reading.fall_detected:
            detected_risks.append("FALL")
            anomaly_flags.append("impact_vector_spike")

        if reading.temperature >= 41.0 or (heat_idx >= 40.0 and reading.humidity >= 85.0 and reading.temperature >= 40.0):
            detected_risks.append("ENVIRONMENTAL_STRESS")
            anomaly_flags.append("environmental_heat_hazard")
        elif reading.temperature >= 38.5 and heat_idx >= 38.0:
            detected_risks.append("HEAT_STRESS")
            anomaly_flags.append("thermal_overload")
        elif heat_idx >= 38.0 or (reading.temperature >= 38.0 and reading.humidity >= 80.0):
            detected_risks.append("ENVIRONMENTAL_STRESS")
            anomaly_flags.append("environmental_heat_index_high")

        if reading.heart_rate > 105.0 and reading.temperature >= 37.8 and reading.humidity < 40.0:
            detected_risks.append("DEHYDRATION")
            anomaly_flags.append("elevated_hr_dry_environment")

        if (emg_fatigue["fatigue_status"] in ["moderate_fatigue", "high_fatigue"] or
            reading.emg_status in ["high_fatigue", "fatigue"] or
            emg_fatigue["fatigue_index"] >= 0.35):
            detected_risks.append("FATIGUE")
            anomaly_flags.append("elevated_emg_power")

        if reading.spo2 < 92.0:
            detected_risks.append("RESPIRATORY_RISK")
            anomaly_flags.append("hypoxemia")

        if (reading.heart_rate > 130.0 or reading.heart_rate < 48.0 or
            reading.ecg_status in ["tachycardia", "bradycardia", "arrhythmic"]):
            detected_risks.append("ABNORMAL_VITALS")
            anomaly_flags.append("cardiac_rhythm_deviation")

        if not detected_risks and raw_level == "NORMAL":
            detected_risks.append("NORMAL_STATE")

        # Map to enum
        level_enum = RiskLevel(raw_level)

        return RiskAssessment(
            timestamp=datetime.utcnow().isoformat(),
            risk_level=level_enum,
            risk_score=risk_score,
            detected_risks=detected_risks,
            contributing_factors=reasons,
            confidence=0.94 if reading.fall_detected or reading.spo2 < 90.0 else 0.88,
            anomaly_flags=anomaly_flags,
        )
