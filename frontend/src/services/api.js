/**
 * REST API Client for VITA-BAND AI
 */
/**
 * Resolves the target backend REST API base URL.
 * Prioritizes VITE_API_URL environment variable, followed by window origin resolution.
 */
export const getBaseUrl = () => {
  const envUrl = import.meta.env?.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim() !== '') {
    return envUrl.trim().replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined') {
    const loc = window.location;
    // Local development fallback
    if (loc.port === '3000' || loc.port === '5173') {
      const hostname = (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1')
        ? '127.0.0.1'
        : loc.hostname;
      return `${loc.protocol}//${hostname}:8000`;
    }
    // Production / reverse proxy fallback (relative URLs to same host)
    return '';
  }

  return 'http://127.0.0.1:8000';
};

const BASE_URL = getBaseUrl();

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

export async function fetchLatestSensors() {
  const res = await fetch(`${BASE_URL}/api/sensors/latest`);
  return res.json();
}

export async function fetchCurrentRisk() {
  const res = await fetch(`${BASE_URL}/api/risk/current`);
  return res.json();
}

export async function fetchRecommendations() {
  const res = await fetch(`${BASE_URL}/api/recommendations`);
  return res.json();
}

export async function startSimulation(scenario, duration = 60, severity = 0.8, noiseLevel = 0.05) {
  const res = await fetch(`${BASE_URL}/api/simulation/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario,
      duration_seconds: duration,
      severity,
      noise_level: noiseLevel,
    }),
  });
  return res.json();
}

export async function stopSimulation() {
  const res = await fetch(`${BASE_URL}/api/simulation/stop`, {
    method: 'POST',
  });
  return res.json();
}

export async function triggerAlertTest(alertType = 'SOS_MANUAL', customMessage = null) {
  const res = await fetch(`${BASE_URL}/api/alerts/test`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      alert_type: alertType,
      custom_message: customMessage,
    }),
  });
  return res.json();
}

export async function acknowledgeAlert(alertId) {
  const res = await fetch(`${BASE_URL}/api/alerts/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_id: alertId }),
  });
  return res.json();
}

export async function fetchSensorHistory(limit = 30) {
  const res = await fetch(`${BASE_URL}/api/sensors/history?limit=${limit}`);
  return res.json();
}
