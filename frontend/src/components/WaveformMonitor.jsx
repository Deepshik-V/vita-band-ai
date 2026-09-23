import React, { useRef, useEffect } from 'react';
import { Activity, Zap } from 'lucide-react';

export default function WaveformMonitor({ ecgBuffer = [], emgBuffer = [], heartRate = 75, emgStatus = 'normal' }) {
  const ecgCanvasRef = useRef(null);
  const emgCanvasRef = useRef(null);

  // Draw ECG Oscilloscope
  useEffect(() => {
    const canvas = ecgCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear background
    ctx.fillStyle = '#060B14';
    ctx.fillRect(0, 0, width, height);

    // Draw Medical Grid
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.08)';
    ctx.lineWidth = 1;
    const gridSize = 20;

    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Midline
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.15)';
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    // Plot ECG Waveform
    if (ecgBuffer && ecgBuffer.length > 1) {
      ctx.strokeStyle = '#10B981';
      ctx.lineWidth = 2.2;
      ctx.shadowColor = '#10B981';
      ctx.shadowBlur = 10;
      ctx.beginPath();

      const step = width / (ecgBuffer.length - 1);
      const midY = height * 0.55;
      const scaleY = height * 0.32; // amplitude scale

      ecgBuffer.forEach((val, i) => {
        const x = i * step;
        const y = midY - (val * scaleY);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });

      ctx.stroke();
      ctx.shadowBlur = 0; // reset
    }
  }, [ecgBuffer]);

  // Draw EMG Oscilloscope
  useEffect(() => {
    const canvas = emgCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Background
    ctx.fillStyle = '#060B14';
    ctx.fillRect(0, 0, width, height);

    // Grid
    ctx.strokeStyle = 'rgba(6, 182, 212, 0.08)';
    ctx.lineWidth = 1;
    const gridSize = 20;

    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Plot EMG Waveform
    if (emgBuffer && emgBuffer.length > 1) {
      const isFatigued = emgStatus === 'high_fatigue' || emgStatus === 'moderate_fatigue';
      const emgColor = isFatigued ? '#F59E0B' : '#06B6D4';

      ctx.strokeStyle = emgColor;
      ctx.lineWidth = 1.8;
      ctx.shadowColor = emgColor;
      ctx.shadowBlur = 8;
      ctx.beginPath();

      const step = width / (emgBuffer.length - 1);
      const midY = height * 0.5;
      const maxVal = 120.0;

      emgBuffer.forEach((val, i) => {
        const x = i * step;
        const normalized = Math.max(-1, Math.min(1, val / maxVal));
        const y = midY - (normalized * (height * 0.38));
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });

      ctx.stroke();
      ctx.shadowBlur = 0;
    }
  }, [emgBuffer, emgStatus]);

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))',
      gap: '16px',
      marginBottom: '20px'
    }}>
      
      {/* ECG Cardiac Waveform */}
      <div className="glass-panel" style={{ padding: '18px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity style={{ width: '18px', height: '18px', color: '#10B981' }} />
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', letterSpacing: '0.02em' }}>
              REAL-TIME ECG LEAD MONITOR (AD8232)
            </h3>
          </div>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            background: 'rgba(16, 185, 129, 0.15)',
            color: '#10B981',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            padding: '2px 8px',
            borderRadius: '4px'
          }}>
            100 Hz • {heartRate.toFixed(0)} BPM
          </span>
        </div>
        <div style={{ borderRadius: '10px', overflow: 'hidden', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <canvas
            ref={ecgCanvasRef}
            width={600}
            height={160}
            style={{ width: '100%', height: '160px', display: 'block' }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#6B7280', marginTop: '6px' }}>
          <span>P-Q-R-S-T Sinus Rhythm</span>
          <span>Lead I/II Analog Front-End</span>
          <span>25mm/s Sweep</span>
        </div>
      </div>

      {/* EMG Muscle Activity Waveform */}
      <div className="glass-panel" style={{ padding: '18px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap style={{ width: '18px', height: '18px', color: '#06B6D4' }} />
            <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', letterSpacing: '0.02em' }}>
              REAL-TIME EMG MUSCLE ACTIVITY & FATIGUE
            </h3>
          </div>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            background: 'rgba(6, 182, 212, 0.15)',
            color: '#06B6D4',
            border: '1px solid rgba(6, 182, 212, 0.3)',
            padding: '2px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase'
          }}>
            {emgStatus.replace('_', ' ')}
          </span>
        </div>
        <div style={{ borderRadius: '10px', overflow: 'hidden', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
          <canvas
            ref={emgCanvasRef}
            width={600}
            height={160}
            style={{ width: '100%', height: '160px', display: 'block' }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#6B7280', marginTop: '6px' }}>
          <span>Motor Unit Action Potentials (uV)</span>
          <span>RMS Envelope Filtering</span>
          <span>Fatigue Spectral Analysis</span>
        </div>
      </div>

    </div>
  );
}
