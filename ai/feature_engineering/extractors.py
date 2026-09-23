"""
Feature Engineering Module for VITA-BAND AI
Calculates physiological and environmental indices including:
- Heat Index (NOAA Rothfusz regression)
- HRV time-domain metrics (RMSSD, SDNN)
- EMG RMS & Fatigue Index
- Kinematic Motion & Jerk metrics
"""
import numpy as np
from typing import Dict, List, Any


def calculate_heat_index(temp_c: float, humidity_pct: float) -> float:
    """
    Calculates apparent temperature / Heat Index (°C) based on ambient temperature
    and relative humidity using the standard NOAA equation.
    """
    # Convert Celsius to Fahrenheit
    t = (temp_c * 9.0 / 5.0) + 32.0
    r = humidity_pct

    # Simple equation first
    hi = 0.5 * (t + 61.0 + ((t - 68.0) * 1.2) + (r * 0.094))

    if hi >= 80.0:
        # Full Rothfusz regression
        hi = (-42.379 +
              2.04901523 * t +
              10.14333127 * r -
              0.22475541 * t * r -
              0.00683783 * t * t -
              0.05481717 * r * r +
              0.00122874 * t * t * r +
              0.00085282 * t * r * r -
              0.00000199 * t * t * r * r)

        if r < 13.0 and 80.0 <= t <= 112.0:
            adj = ((13.0 - r) / 4.0) * np.sqrt((17.0 - abs(t - 95.0)) / 17.0)
            hi -= adj
        elif r > 85.0 and 80.0 <= t <= 87.0:
            adj = ((r - 85.0) / 10.0) * ((87.0 - t) / 5.0)
            hi += adj

    # Convert back to Celsius
    hi_c = (hi - 32.0) * 5.0 / 9.0
    return float(np.round(hi_c, 2))


def extract_statistical_features(signal: List[float]) -> Dict[str, float]:
    """Extracts fundamental statistical features from a 1D signal buffer."""
    if not signal or len(signal) == 0:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "p2p": 0.0, "rms": 0.0}

    arr = np.asarray(signal, dtype=float)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    p2p_val = float(max_val - min_val)
    rms_val = float(np.sqrt(np.mean(arr**2)))

    return {
        "mean": round(mean_val, 4),
        "std": round(std_val, 4),
        "min": round(min_val, 4),
        "max": round(max_val, 4),
        "p2p": round(p2p_val, 4),
        "rms": round(rms_val, 4),
    }


def calculate_hrv_metrics(heart_rate: float, rr_intervals_ms: List[float] = None) -> Dict[str, float]:
    """
    Computes surrogate or genuine Heart Rate Variability (HRV) metrics.
    RMSSD (Root Mean Square of Successive Differences)
    SDNN (Standard Deviation of NN intervals)
    """
    if rr_intervals_ms and len(rr_intervals_ms) >= 3:
        arr = np.asarray(rr_intervals_ms, dtype=float)
        diffs = np.diff(arr)
        rmssd = float(np.sqrt(np.mean(diffs**2)))
        sdnn = float(np.std(arr))
    else:
        # Approximate baseline surrogate from instantaneous heart rate
        # Higher resting HR typically correlates with depressed parasympathetic tone / lower RMSSD
        base_rr = 60000.0 / max(40.0, min(200.0, heart_rate))
        rmssd = float(max(15.0, 75.0 - (heart_rate - 60.0) * 0.5))
        sdnn = float(rmssd * 1.2)

    return {
        "rmssd_ms": round(rmssd, 2),
        "sdnn_ms": round(sdnn, 2),
    }


def calculate_emg_fatigue_index(emg_signal: List[float]) -> Dict[str, Any]:
    """
    Analyzes EMG signal power to quantify muscle contraction amplitude and fatigue level.
    """
    if not emg_signal or len(emg_signal) == 0:
        return {"rms_uv": 0.0, "fatigue_index": 0.0, "fatigue_status": "normal"}

    arr = np.asarray(emg_signal, dtype=float)
    rms = float(np.sqrt(np.mean(arr**2)))
    
    # Baseline resting RMS is ~10-25uV; active contraction is 40-90uV; sustained exhaustion > 100uV
    fatigue_index = min(1.0, max(0.0, (rms - 20.0) / 140.0))

    if fatigue_index >= 0.55:
        status = "high_fatigue"
    elif fatigue_index >= 0.30:
        status = "moderate_fatigue"
    else:
        status = "normal"

    return {
        "rms_uv": round(rms, 2),
        "fatigue_index": round(fatigue_index, 3),
        "fatigue_status": status,
    }
