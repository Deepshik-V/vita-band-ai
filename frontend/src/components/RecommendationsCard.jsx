import React from 'react';
import { Compass, CheckCircle2, AlertCircle, Info } from 'lucide-react';

export default function RecommendationsCard({ recommendations = [] }) {
  if (!recommendations || recommendations.length === 0) return null;

  const urgencyColors = {
    low: { bg: 'rgba(16, 185, 129, 0.15)', text: '#10B981', border: 'rgba(16, 185, 129, 0.3)' },
    medium: { bg: 'rgba(245, 158, 11, 0.15)', text: '#F59E0B', border: 'rgba(245, 158, 11, 0.3)' },
    high: { bg: 'rgba(239, 68, 68, 0.15)', text: '#EF4444', border: 'rgba(239, 68, 68, 0.3)' },
    critical: { bg: 'rgba(239, 68, 68, 0.25)', text: '#F87171', border: 'rgba(239, 68, 68, 0.5)' },
  };

  return (
    <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '20px' }}>
      
      {/* Title Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'rgba(6, 182, 212, 0.15)',
            border: '1px solid rgba(6, 182, 212, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Compass style={{ width: '20px', height: '20px', color: '#06B6D4' }} />
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
              ADAPTIVE HEALTH & PREVENTIVE GUIDANCE
            </h3>
            <p style={{ fontSize: '0.75rem', color: '#9CA3AF' }}>
              Real-time actionable recommendations derived from multi-sensor data fusion
            </p>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {recommendations.map((rec) => {
          const uTheme = urgencyColors[rec.urgency] || urgencyColors.low;
          return (
            <div
              key={rec.id}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '12px',
                padding: '16px 20px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#F3F4F6' }}>
                  {rec.title}
                </span>
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  padding: '3px 10px',
                  borderRadius: '20px',
                  background: uTheme.bg,
                  color: uTheme.text,
                  border: `1px solid ${uTheme.border}`,
                  letterSpacing: '0.05em'
                }}>
                  {rec.urgency} Urgency
                </span>
              </div>

              {/* Action items */}
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {rec.guidance.map((step, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.85rem', color: '#D1D5DB', lineHeight: 1.4 }}>
                    <CheckCircle2 style={{ width: '16px', height: '16px', color: '#06B6D4', flexShrink: 0, marginTop: '2px' }} />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>

      {/* Non-Diagnostic Disclaimer */}
      <div style={{
        marginTop: '16px',
        padding: '10px 14px',
        borderRadius: '8px',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '0.72rem',
        color: '#9CA3AF',
      }}>
        <Info style={{ width: '14px', height: '14px', color: '#9CA3AF', flexShrink: 0 }} />
        <span>
          <strong>Medical Notice:</strong> Recommendations are computer-generated preventive early-warnings for wellness monitoring. 
          VITA-BAND AI does not diagnose disease or replace emergency healthcare professionals.
        </span>
      </div>

    </div>
  );
}
