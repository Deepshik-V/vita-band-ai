import React, { useState, useEffect } from 'react';
import { wsClient } from './services/websocket';
import { triggerAlertTest, fetchSensorHistory } from './services/api';

import Header from './components/Header';
import RiskStatusBanner from './components/RiskStatusBanner';
import VitalsGrid from './components/VitalsGrid';
import WaveformMonitor from './components/WaveformMonitor';
import RecommendationsCard from './components/RecommendationsCard';
import SimulationControl from './components/SimulationControl';
import EmergencyAlertModal from './components/EmergencyAlertModal';
import HistoricalTrends from './components/HistoricalTrends';

export default function App() {
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [telemetry, setTelemetry] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeAlert, setActiveAlert] = useState(null);

  // Initialize WebSocket and initial telemetry
  useEffect(() => {
    // Subscribe to connection status
    const unsubStatus = wsClient.subscribeStatus((status) => {
      setWsStatus(status);
    });

    // Subscribe to live telemetry packets
    const unsubData = wsClient.subscribe((payload) => {
      setTelemetry(payload);

      if (payload.active_alert) {
        setActiveAlert(payload.active_alert);
      } else {
        setActiveAlert(null);
      }

      // Append to local trend buffer
      if (payload.vitals) {
        setHistory((prev) => {
          const next = [...prev, payload.vitals];
          return next.slice(-30);
        });
      }
    });

    // Connect WebSocket
    wsClient.connect();

    // Fetch initial historical records from backend
    fetchSensorHistory(25)
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setHistory(data);
        }
      })
      .catch((err) => console.error('[INIT_HISTORY_ERR]', err));

    return () => {
      unsubStatus();
      unsubData();
      wsClient.disconnect();
    };
  }, []);

  const handleTriggerSos = async () => {
    try {
      const alert = await triggerAlertTest('SOS_MANUAL', 'Manual emergency SOS alert triggered from health companion dashboard.');
      setActiveAlert(alert);
    } catch (err) {
      console.error('[SOS_ERROR]', err);
    }
  };

  const vitals = telemetry?.vitals || {
    heart_rate: 74,
    spo2: 98.4,
    temperature: 36.8,
    humidity: 50.0,
    activity: 'resting',
    fall_detected: false,
    ecg_status: 'normal',
    emg_status: 'normal',
    battery_percentage: 94,
  };

  const riskAssessment = telemetry?.risk_assessment || {
    risk_level: 'NORMAL',
    risk_score: 12.0,
    detected_risks: ['NORMAL_STATE'],
    contributing_factors: {},
    confidence: 0.94,
  };

  const recommendations = telemetry?.recommendations || [];
  const simulationState = telemetry?.simulation_state;
  const isSimActive = simulationState?.active || false;
  const scenarioName = simulationState?.scenario_type || 'NORMAL';

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '24px 20px 60px' }}>
      
      {/* 1. Dashboard Header */}
      <Header
        wsStatus={wsStatus}
        battery={vitals.battery_percentage}
        onTriggerSos={handleTriggerSos}
        isSimActive={isSimActive}
        scenarioName={scenarioName}
      />

      {/* 2. Tri-State Risk Status Banner */}
      <RiskStatusBanner riskAssessment={riskAssessment} />

      {/* 3. Primary Vitals 5-Card Grid */}
      <VitalsGrid vitals={vitals} />

      {/* 4. Real-time Dual Waveform Oscilloscope (ECG & EMG) */}
      <WaveformMonitor
        ecgBuffer={telemetry?.ecg_buffer || []}
        emgBuffer={telemetry?.emg_buffer || []}
        heartRate={vitals.heart_rate}
        emgStatus={vitals.emg_status}
      />

      {/* 5. Smart Health Simulation Control Framework */}
      <SimulationControl
        simulationState={simulationState}
        onScenarioTriggered={() => {}}
      />

      {/* 6. Context-Aware Recommendations */}
      <RecommendationsCard recommendations={recommendations} />

      {/* 7. Historical Trend Visualizer */}
      <HistoricalTrends history={history} />

      {/* 8. Emergency Alert Modal (Pop-up on Fall or SOS) */}
      <EmergencyAlertModal
        activeAlert={activeAlert}
        onDismiss={() => setActiveAlert(null)}
      />

      {/* Footer */}
      <footer style={{
        marginTop: '40px',
        paddingTop: '20px',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        textAlign: 'center',
        fontSize: '0.75rem',
        color: '#6B7280',
        lineHeight: 1.6,
      }}>
        <p style={{ fontWeight: 600, color: '#9CA3AF' }}>
          VITA-BAND AI • Smart India Hackathon 2026 Project (Problem Statement ID: SIH26198)
        </p>
        <p>
          Team <strong>ALPHA MECHS</strong> • Secure, Privacy-Preserving Personal Health Companion
        </p>
        <p style={{ marginTop: '6px', fontSize: '0.7rem', color: '#4B5563' }}>
          <strong>Medical Safety Notice:</strong> This technology demonstration prototype is developed for continuous wellness monitoring, early risk identification, and simulation-based validation. It does not perform clinical diagnosis or replace licensed emergency medical services.
        </p>
      </footer>

    </div>
  );
}
