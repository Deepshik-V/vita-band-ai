"""
Signal Preprocessing Module for VITA-BAND AI
Applies digital filtering, artifact suppression, and envelope extraction
on raw physiological and kinetic signals (ECG, EMG, Accelerometer).
"""
import numpy as np
from typing import List, Union

try:
    from scipy.signal import butter, filtfilt, iirnotch
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def bandpass_filter(
    data: Union[List[float], np.ndarray],
    lowcut: float = 0.5,
    highcut: float = 45.0,
    fs: float = 100.0,
    order: int = 2
) -> List[float]:
    """
    Butterworth bandpass filter for ECG signals.
    Attenuates baseline wander (<0.5Hz) and high-frequency muscle noise (>45Hz).
    """
    arr = np.asarray(data, dtype=float)
    if len(arr) < 15:
        return arr.tolist()

    if HAS_SCIPY:
        nyq = 0.5 * fs
        low = max(0.01, lowcut / nyq)
        high = min(0.99, highcut / nyq)
        if low >= high:
            return arr.tolist()
        b, a = butter(order, [low, high], btype='band')
        try:
            filtered = filtfilt(b, a, arr)
            return filtered.tolist()
        except Exception:
            return arr.tolist()
    else:
        # Fallback moving average detrending
        window = 5
        trend = np.convolve(arr, np.ones(window)/window, mode='same')
        return (arr - trend).tolist()


def notch_filter(
    data: Union[List[float], np.ndarray],
    notch_freq: float = 50.0,
    fs: float = 100.0,
    q: float = 30.0
) -> List[float]:
    """
    Notch filter to suppress 50Hz mains powerline interference.
    """
    arr = np.asarray(data, dtype=float)
    if len(arr) < 15 or not HAS_SCIPY:
        return arr.tolist()

    nyq = 0.5 * fs
    freq = notch_freq / nyq
    if freq >= 1.0 or freq <= 0.0:
        return arr.tolist()

    try:
        b, a = iirnotch(freq, q)
        filtered = filtfilt(b, a, arr)
        return filtered.tolist()
    except Exception:
        return arr.tolist()


def compute_emg_envelope(
    emg_data: Union[List[float], np.ndarray],
    fs: float = 100.0,
    cutoff: float = 5.0
) -> List[float]:
    """
    Computes EMG linear envelope by full-wave rectification followed by lowpass smoothing.
    Quantifies muscle activity and fatigue onset.
    """
    arr = np.asarray(emg_data, dtype=float)
    if len(arr) == 0:
        return []

    # Full-wave rectification
    rectified = np.abs(arr)
    
    if len(arr) < 10:
        return rectified.tolist()

    if HAS_SCIPY:
        nyq = 0.5 * fs
        normal_cutoff = min(0.99, cutoff / nyq)
        b, a = butter(2, normal_cutoff, btype='low')
        try:
            envelope = filtfilt(b, a, rectified)
            return envelope.tolist()
        except Exception:
            pass

    # Simple moving average fallback
    window = min(7, len(arr))
    envelope = np.convolve(rectified, np.ones(window)/window, mode='same')
    return envelope.tolist()


def compute_accel_magnitude(
    ax: float,
    ay: float,
    az: float
) -> float:
    """
    Calculates total acceleration magnitude vector in g:
    sqrt(ax^2 + ay^2 + az^2)
    """
    return float(np.sqrt(ax**2 + ay**2 + az**2))
