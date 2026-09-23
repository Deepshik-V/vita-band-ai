import React, { useState } from 'react';
import { Play, Square, Flame, Droplet, BatteryLow, HeartPulse, UserX, AlertOctagon, CloudRain, RotateCcw } from 'lucide-react';
import { startSimulation, stopSimulation } from '../services/api';

export default function SimulationControl({ simulationState, onScenarioTriggered }) {
  const [loading, setLoading] = useState(false);

  const activeScenario = simulationState?.scenario_type || 'NORMAL';
  const isRunning = simulationState?.active || false;
  const elapsed = simulationState?.elapsed_seconds || 0;
  const totalDuration = simulationState?.duration_seconds || 60;

  const scenarios = [
    { id: 'NORMAL', label: '1. Normal', icon: RotateCcw, color: '#10B981', desc: 'Resting baseline parameters' },
    { id: 'HEAT_STRESS', label: '2. Heat Stress', icon: Flame, color: '#F97316', desc: 'High temp, tachycardia, sweat' },
    { id: 'DEHYDRATION', label: '3. Dehydration', icon: Droplet, color: '#F59E0B', desc: 'Elevated HR, dry ambient air' },
    { id: 'FATIGUE', label: '4. Fatigue', icon: BatteryLow, color: '#A855F7', desc: 'High EMG muscle strain' },
    { id: 'ABNORMAL_VITALS', label: '5. Abnormal Vitals', icon: HeartPulse, color: '#EC4899', desc: 'Arrhythmia, SpO2 swings' },
    { id: 'FALL', label: '6. Fall Impact', icon: UserX, color: '#EF4444', desc: 'High-g shock & immobility' },
    { id: 'RESPIRATORY_RISK', label: '7. Respiratory Risk', icon: AlertOctagon, color: '#38BDF8', desc: 'Severe hypoxemia (SpO2 < 88%)' },
    { id: 'ENVIRONMENTAL_STRESS', label: '8. Env Stress', icon: CloudRain, color: '#EAB308', desc: 'Extreme Heat Index (>42°C)' },
  ];

  const handleSelectScenario = async (scenarioId) => {
    setLoading(true);
    try {
      if (scenarioId === 'NORMAL') {
        await stopSimulation();
      } else {
        await startSimulation(scenarioId, 60, 0.85, 0.05);
      }
      if (onScenarioTriggered) onScenarioTriggered(scenarioId);
    } catch (err) {
      console.error('[SIM_TRIGGER_ERROR]', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopSimulation();
      if (onScenarioTriggered) onScenarioTriggered('NORMAL');
    } catch (err) {
      console.error('[SIM_STOP_ERROR]', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '20px' }}>
      
      {/* Header and Status */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{
              background: 'rgba(245, 158, 11, 0.15)',
              color: '#F59E0B',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '0.7rem',
              fontWeight: 700,
            }}>
              SIH DEMO FRAMEWORK
            </span>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
              SMART HEALTH SIMULATION CONTROLS
            </h3>
          </div>
          <p style={{ fontSize: '0.75rem', color: '#9CA3AF', marginTop: '2px' }}>
            Test multi-sensor AI risk detection across 8 deterministic stress scenarios without physical hardware
          </p>
        </div>

        {/* Reset / Stop Button */}
        <button
          id="btn-sim-reset"
          onClick={handleStop}
          disabled={loading || activeScenario === 'NORMAL'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: activeScenario !== 'NORMAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.05)',
            border: `1px solid ${activeScenario !== 'NORMAL' ? 'rgba(239, 68, 68, 0.4)' : 'rgba(255, 255, 255, 0.1)'}`,
            color: activeScenario !== 'NORMAL' ? '#EF4444' : '#6B7280',
            padding: '6px 14px',
            borderRadius: '8px',
            fontSize: '0.78rem',
            fontWeight: 700,
            cursor: activeScenario !== 'NORMAL' ? 'pointer' : 'default',
            transition: 'all 0.2s ease',
          }}
        >
          <Square style={{ width: '14px', height: '14px' }} />
          <span>RESET TO NORMAL</span>
        </button>
      </div>

      {/* Scenarios Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
      }}>
        {scenarios.map((sc) => {
          const isActive = activeScenario === sc.id;
          const IconComp = sc.icon;

          return (
            <button
              key={sc.id}
              id={`btn-sim-${sc.id.toLowerCase()}`}
              onClick={() => handleSelectScenario(sc.id)}
              disabled={loading}
              className="glass-card-interactive"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                padding: '12px 14px',
                borderRadius: '12px',
                background: isActive ? `${sc.color}22` : 'rgba(255, 255, 255, 0.02)',
                border: `1.5px solid ${isActive ? sc.color : 'rgba(255, 255, 255, 0.08)'}`,
                boxShadow: isActive ? `0 0 16px ${sc.color}44` : 'none',
                color: '#FFFFFF',
                textAlign: 'left',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: '6px' }}>
                <div style={{
                  padding: '6px',
                  borderRadius: '8px',
                  background: `${sc.color}20`,
                  color: sc.color
                }}>
                  <IconComp style={{ width: '16px', height: '16px' }} />
                </div>
                {isActive && (
                  <span style={{
                    fontSize: '0.65rem',
                    fontWeight: 800,
                    color: sc.color,
                    background: `${sc.color}20`,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    textTransform: 'uppercase'
                  }}>
                    ACTIVE
                  </span>
                )}
              </div>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: isActive ? sc.color : '#F3F4F6' }}>
                {sc.label}
              </span>
              <span style={{ fontSize: '0.7rem', color: '#9CA3AF', marginTop: '2px' }}>
                {sc.desc}
              </span>
            </button>
          );
        })}
      </div>

      {/* Progress Bar for Active Scenario */}
      {isRunning && activeScenario !== 'NORMAL' && (
        <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9CA3AF', marginBottom: '4px' }}>
            <span>Scenario Progression: <strong>{activeScenario}</strong></span>
            <span>{elapsed}s / {totalDuration}s</span>
          </div>
          <div style={{ width: '100%', height: '4px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{
              width: `${Math.min(100, (elapsed / totalDuration) * 100)}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #F59E0B 0%, #EF4444 100%)',
              transition: 'width 0.5s ease',
            }} />
          </div>
        </div>
      )}

    </div>
  );
}
