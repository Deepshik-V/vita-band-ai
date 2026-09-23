import React, { useRef, useEffect } from 'react';
import { History, TrendingUp } from 'lucide-react';

export default function HistoricalTrends({ history = [] }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Background
    ctx.fillStyle = '#060B14';
    ctx.fillRect(0, 0, width, height);

    if (!history || history.length < 2) {
      ctx.fillStyle = '#6B7280';
      ctx.font = '12px Plus Jakarta Sans, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Accumulating continuous telemetry trend points...', width / 2, height / 2);
      return;
    }

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let y = 30; y < height; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const n = history.length;
    const stepX = width / (n - 1);

    // Plot Heart Rate (Red/Coral)
    ctx.strokeStyle = '#EF4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    history.forEach((pt, i) => {
      const hr = pt.heart_rate || 75;
      // Map 40..180 BPM to height
      const y = height - ((hr - 40) / (180 - 40)) * (height - 30) - 15;
      const x = i * stepX;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Plot SpO2 (Cyan)
    ctx.strokeStyle = '#06B6D4';
    ctx.lineWidth = 2;
    ctx.beginPath();
    history.forEach((pt, i) => {
      const spo2 = pt.spo2 || 98;
      // Map 75..100 % to height
      const y = height - ((spo2 - 75) / (100 - 75)) * (height - 30) - 15;
      const x = i * stepX;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Plot Temperature (Amber)
    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 2;
    ctx.beginPath();
    history.forEach((pt, i) => {
      const temp = pt.temperature || 36.8;
      // Map 34..42 C to height
      const y = height - ((temp - 34) / (42 - 34)) * (height - 30) - 15;
      const x = i * stepX;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

  }, [history]);

  return (
    <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            padding: '8px',
            borderRadius: '10px',
            background: 'rgba(59, 130, 246, 0.15)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
          }}>
            <TrendingUp style={{ width: '18px', height: '18px', color: '#60A5FA' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>
              PHYSIOLOGICAL TREND TELEMETRY
            </h3>
            <p style={{ fontSize: '0.72rem', color: '#9CA3AF' }}>
              Multi-parameter rolling window (Last 30 data snapshots)
            </p>
          </div>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', fontWeight: 600 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#EF4444' }} />
            <span style={{ color: '#E5E7EB' }}>Heart Rate (BPM)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#06B6D4' }} />
            <span style={{ color: '#E5E7EB' }}>SpO2 (%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#F59E0B' }} />
            <span style={{ color: '#E5E7EB' }}>Temp (°C)</span>
          </div>
        </div>
      </div>

      <div style={{ borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
        <canvas
          ref={canvasRef}
          width={900}
          height={140}
          style={{ width: '100%', height: '140px', display: 'block' }}
        />
      </div>
    </div>
  );
}
