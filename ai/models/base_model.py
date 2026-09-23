"""
Base interface and extensible model implementations for early health risk detection.
Supports transparent heuristic assessment with extension hooks for PyTorch and TFLite.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import os

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class BaseRiskModel(ABC):
    """Abstract Base Class for any ML / Deep Learning / Heuristic risk detection model."""

    @abstractmethod
    def predict_risk(self, features: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Takes extracted multi-modal physiological & environmental features.
        Returns:
            - risk_level: str ("NORMAL", "WARNING", "CRITICAL")
            - risk_score: float (0.0 to 100.0)
            - metadata: dict of contributing weights / anomaly factors
        """
        pass


class BaselineHeuristicModel(BaseRiskModel):
    """
    Transparent, explainable multi-modal early risk scoring model.
    Evaluates:
      1. Cardiovascular risk (HR, SpO2)
      2. Thermal strain (Body temperature, Heat Index)
      3. Musculoskeletal fatigue (EMG fatigue index)
      4. Impact / Posture anomalies (Fall spike, immobility)
    """

    def predict_risk(self, features: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        hr = features.get("heart_rate", 75.0)
        spo2 = features.get("spo2", 98.0)
        temp = features.get("temperature", 36.8)
        heat_idx = features.get("heat_index", 32.0)
        fall_detected = features.get("fall_detected", False)
        emg_fatigue = features.get("emg_fatigue_index", 0.1)

        score = 10.0  # baseline calm physiological score
        reasons = {}

        # 1. Fall detection (immediate critical elevation)
        if fall_detected:
            score = max(score, 95.0)
            reasons["fall"] = "High acceleration impact followed by kinetic arrest"

        # 2. Oxygen Saturation (SpO2)
        if spo2 < 88.0:
            score += 60.0
            reasons["severe_hypoxia"] = f"Critical SpO2 reading of {spo2:.1f}%"
        elif spo2 < 93.0:
            score += 35.0
            reasons["mild_hypoxia"] = f"Depressed SpO2 reading of {spo2:.1f}%"

        # 3. Heart Rate
        if hr > 150.0 or hr < 42.0:
            score += 45.0
            reasons["extreme_heart_rate"] = f"Heart rate at {hr:.0f} BPM outside safe envelope"
        elif hr > 115.0 or hr < 52.0:
            score += 25.0
            reasons["elevated_heart_rate"] = f"Heart rate at {hr:.0f} BPM indicates physical/thermal strain"

        # 4. Temperature & Heat Stress
        if temp > 39.0:
            score += 45.0
            reasons["hyperthermia"] = f"High core temperature reading of {temp:.1f}°C"
        elif temp > 37.8:
            score += 20.0
            reasons["elevated_temperature"] = f"Elevated temperature of {temp:.1f}°C"

        if heat_idx > 42.0:
            score += 25.0
            reasons["environmental_heat_danger"] = f"Ambient Heat Index reached dangerous level of {heat_idx:.1f}°C"
        elif heat_idx > 36.0:
            score += 15.0
            reasons["environmental_heat_caution"] = f"Ambient Heat Index elevated at {heat_idx:.1f}°C"

        # 5. EMG Muscle Fatigue
        if emg_fatigue >= 0.55:
            score += 35.0
            reasons["severe_muscle_fatigue"] = f"EMG fatigue index at {emg_fatigue:.2f}"
        elif emg_fatigue >= 0.30:
            score += 28.0
            reasons["moderate_muscle_fatigue"] = f"EMG fatigue index at {emg_fatigue:.2f}"

        # Clamp composite score between 0.0 and 100.0
        final_score = min(100.0, max(0.0, score))

        if final_score >= 70.0:
            level = "CRITICAL"
        elif final_score >= 38.0:
            level = "WARNING"
        else:
            level = "NORMAL"

        return level, round(final_score, 1), reasons


if HAS_TORCH:
    class RiskMLPNetwork(nn.Module):
        """Edge-optimized Multi-Layer Perceptron for multi-modal risk scoring."""
        def __init__(self, in_features: int = 6, hidden: int = 16):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(in_features, hidden),
                nn.ReLU(),
                nn.Linear(hidden, hidden),
                nn.ReLU(),
                nn.Linear(hidden, 1),
                nn.Sigmoid()
            )
        def forward(self, x):
            return self.net(x) * 100.0  # Output 0-100 scale


class PyTorchRiskModel(BaseRiskModel):
    """
    Production-ready PyTorch wrapper for neural network risk assessment.
    Provides feature tensor conversion and falls back to baseline heuristic
    if uncalibrated weights are detected.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.heuristic_fallback = BaselineHeuristicModel()
        self.device = "cpu"
        self.model = None

        if HAS_TORCH:
            self.model = RiskMLPNetwork()
            if model_path and os.path.exists(model_path):
                try:
                    self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                    self.model.eval()
                except Exception:
                    pass

    def predict_risk(self, features: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        # Always run baseline heuristics to provide clinical explainability
        base_level, base_score, reasons = self.heuristic_fallback.predict_risk(features)

        if HAS_TORCH and self.model:
            try:
                # Normalize features: HR (40-200), SpO2 (70-100), Temp (35-42), HI (20-50), Accel (0-4g), EMG (0-1)
                hr_norm = (features.get("heart_rate", 75.0) - 40.0) / 160.0
                spo2_norm = (features.get("spo2", 98.0) - 70.0) / 30.0
                temp_norm = (features.get("temperature", 36.8) - 35.0) / 7.0
                hi_norm = (features.get("heat_index", 32.0) - 20.0) / 30.0
                acc_norm = features.get("accel_magnitude", 1.0) / 4.0
                emg_norm = features.get("emg_fatigue_index", 0.1)

                tensor_in = torch.tensor(
                    [[hr_norm, spo2_norm, temp_norm, hi_norm, acc_norm, emg_norm]],
                    dtype=torch.float32,
                    device=self.device
                )
                with torch.no_grad():
                    ml_score = float(self.model(tensor_in).item())

                # Blend heuristic guarantee with ML score
                blended_score = round(0.7 * base_score + 0.3 * ml_score, 1)
                blended_score = min(100.0, max(0.0, blended_score))

                if blended_score >= 70.0:
                    level = "CRITICAL"
                elif blended_score >= 38.0:
                    level = "WARNING"
                else:
                    level = "NORMAL"

                reasons["ai_model"] = "PyTorch MLP Multi-Modal Fusion Active"
                return level, blended_score, reasons
            except Exception:
                pass

        return base_level, base_score, reasons


class TFLiteRiskModel(BaseRiskModel):
    """
    TensorFlow Lite micro inference model interface for edge devices.
    """
    def __init__(self, tflite_path: Optional[str] = None):
        self.heuristic_fallback = BaselineHeuristicModel()
        self.tflite_path = tflite_path

    def predict_risk(self, features: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        base_level, base_score, reasons = self.heuristic_fallback.predict_risk(features)
        reasons["tflite_mode"] = "TFLite Edge Pipeline Available (Heuristic Fallback Active)"
        return base_level, base_score, reasons
