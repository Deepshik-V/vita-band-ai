"""
AI Pipeline, Feature Extraction, and Risk Detection Tests
"""
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
from ai.risk_detection.engine import RiskDetectionEngine
from ai.recommendation.engine import RecommendationEngine
from ai.models.base_model import PyTorchRiskModel, TFLiteRiskModel
from backend.models.schemas import SensorReading, RiskLevel


def test_preprocessing_filters():
    raw_signal = [0.1 * i + (i % 3) for i in range(50)]
    filtered = bandpass_filter(raw_signal)
    assert len(filtered) == len(raw_signal)

    emg_raw = [-10.0, 15.0, -25.0, 30.0, -15.0, 12.0, -5.0, 8.0, -3.0, 5.0]
    envelope = compute_emg_envelope(emg_raw)
    assert len(envelope) == len(emg_raw)
    assert all(v >= 0 for v in envelope)

    mag = compute_accel_magnitude(0.0, 0.0, 1.0)
    assert abs(mag - 1.0) < 1e-4


def test_feature_extractors():
    hi = calculate_heat_index(38.0, 75.0)
    assert hi > 38.0

    hrv = calculate_hrv_metrics(75.0)
    assert "rmssd_ms" in hrv
    assert hrv["rmssd_ms"] > 0

    resting_emg = [5.0, -4.0, 6.0, -5.0, 4.0]
    fatigue_res = calculate_emg_fatigue_index(resting_emg)
    assert fatigue_res["fatigue_status"] == "normal"
    assert fatigue_res["fatigue_index"] < 0.3


def test_risk_detection_normal_state():
    engine = RiskDetectionEngine()
    reading = SensorReading(
        heart_rate=72.0,
        spo2=98.5,
        temperature=36.7,
        humidity=48.0,
        activity="resting",
        fall_detected=False,
    )
    assessment = engine.assess_reading(reading)
    assert assessment.risk_level == RiskLevel.NORMAL
    assert assessment.risk_score < 38.0


def test_risk_detection_heat_stress():
    engine = RiskDetectionEngine()
    reading = SensorReading(
        heart_rate=128.0,
        spo2=96.0,
        temperature=39.2,
        humidity=82.0,
        activity="unsteady",
        fall_detected=False,
    )
    assessment = engine.assess_reading(reading)
    assert assessment.risk_level in [RiskLevel.WARNING, RiskLevel.CRITICAL]
    assert "HEAT_STRESS" in assessment.detected_risks
    assert assessment.risk_score >= 38.0


def test_risk_detection_fall_acute_alert():
    engine = RiskDetectionEngine()
    reading = SensorReading(
        heart_rate=110.0,
        spo2=97.0,
        temperature=36.8,
        humidity=50.0,
        accel_x=2.5,
        accel_y=1.8,
        accel_z=3.8,
        activity="fall_impact",
        fall_detected=True,
    )
    assessment = engine.assess_reading(reading)
    assert assessment.risk_level == RiskLevel.CRITICAL
    assert "FALL" in assessment.detected_risks
    assert assessment.risk_score >= 80.0


def test_recommendation_engine_mapping():
    engine = RiskDetectionEngine()
    rec_engine = RecommendationEngine()
    reading = SensorReading(
        heart_rate=130.0,
        spo2=95.0,
        temperature=39.4,
        humidity=85.0,
        activity="unsteady",
        fall_detected=False,
    )
    assessment = engine.assess_reading(reading)
    recs = rec_engine.generate_recommendations(assessment)
    assert len(recs) > 0
    categories = [r.risk_category for r in recs]
    assert "HEAT_STRESS" in categories
    assert any("cooler" in step.lower() for r in recs for step in r.guidance)


def test_pytorch_and_tflite_risk_models():
    # Test PyTorch model wrapper
    pt_model = PyTorchRiskModel()
    features = {
        "heart_rate": 80.0,
        "spo2": 98.0,
        "temperature": 36.8,
        "heat_index": 32.0,
        "accel_magnitude": 1.0,
        "emg_fatigue_index": 0.1,
    }
    level, score, metadata = pt_model.predict_risk(features)
    assert level in ["NORMAL", "WARNING", "CRITICAL"]
    assert 0.0 <= score <= 100.0

    # Test TFLite model interface
    tflite_model = TFLiteRiskModel()
    tf_level, tf_score, tf_meta = tflite_model.predict_risk(features)
    assert tf_level in ["NORMAL", "WARNING", "CRITICAL"]
    assert 0.0 <= tf_score <= 100.0
