import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, BrainCircuit } from 'lucide-react';

export default function RiskStatusBanner({ riskAssessment }) {
  if (!riskAssessment) return null;

  const {
    risk_level = 'NORMAL',
    risk_score = 12.0,
    detected_risks = ['NORMAL_STATE'],
    contributing_factors = {},
    confidence = 0.94,
  } = riskAssessment;

  const isCritical = risk_level === 'CRITICAL';
  const isWarning = risk_level === 'WARNING';
  const isNormal = risk_level === 'NORMAL';

  let theme = {
    bg: 'rgba(16, 185, 129, 0.08)',
    border: 'rgba(16, 185, 129, 0.35)',
    color: '#10B981',
    glow: 'rgba(16, 185, 129, 0.25)',
    icon: ShieldCheck,
    title: 'PHYSIOLOGICAL EQUILIBRIUM STABLE',
    sub: 'All multi-modal vital parameters are within safe bounds.',
  };

  if (isWarning) {
    theme = {
      bg: 'rgba(245, 158, 11, 0.1)',
      border: 'rgba(245, 158, 11, 0.45)',
      color: '#F59E0B',
      glow: 'rgba(245, 158, 11, 0.35)',
      icon: AlertTriangle,
      title: 'ELEVATED RISK DETECTED',
      sub: 'Thermal strain, dehydration, or muscle fatigue indicators present.',
    };
  } else if (isCritical) {
    theme = {
      bg: 'rgba(239, 68, 68, 0.12)',
      border: 'rgba(239, 68, 68, 0.6)',
      color: '#EF4444',
      glow: 'rgba(239, 68, 68, 0.5)',
      icon: AlertOctagon,
      title: 'CRITICAL HEALTH HAZARD ALERT',
      sub: 'Acute threshold breach, fall impact, or vital destabilization!',
    };
  }

  const IconComponent = theme.icon;

  return (
    <div
      className={`glass-panel ${isCritical ? 'alarm-active' : ''}`}
      style={{
        padding: '20px 24px',
        marginBottom: '20px',
        background: theme.bg,
        borderColor: theme.border,
        boxShadow: `0 8px 32px ${theme.glow}`,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
        
        {/* Left: Icon & Status Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
          <div style={{
            width: '52px',
            height: '52px',
            borderRadius: '14px',
            background: `radial-gradient(circle, ${theme.color}22 0%, ${theme.color}44 100%)`,
            border: `1px solid ${theme.color}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <IconComponent style={{ width: '30px', height: '30px', color: theme.color }} />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{
                background: theme.color,
                color: '#090D16',
                padding: '3px 10px',
                borderRadius: '6px',
                fontWeight: 800,
                fontSize: '0.75rem',
                letterSpacing: '0.05em'
              }}>
                {risk_level}
              </span>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                {theme.title}
              </h2>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#D1D5DB', marginTop: '4px' }}>
              {theme.sub}
            </p>
          </div>
        </div>

        {/* Right: Risk Score & AI Confidence */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          
          {/* Detected conditions tags */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', maxWidth: '320px', justifyContent: 'flex-end' }}>
            {detected_risks.map((risk) => (
              <span
                key={risk}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#F3F4F6',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  padding: '3px 8px',
                  borderRadius: '6px',
                  textTransform: 'uppercase'
                }}
              >
                {risk.replace('_', ' ')}
              </span>
            ))}
          </div>

          {/* Risk Score Gauge */}
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.7rem', color: '#9CA3AF', fontWeight: 600, textTransform: 'uppercase' }}>
              Risk Index
            </div>
            <div className="num-telemetry" style={{ fontSize: '2rem', fontWeight: 800, color: theme.color, lineHeight: 1.1 }}>
              {risk_score.toFixed(0)}<span style={{ fontSize: '1rem', color: '#9CA3AF' }}>/100</span>
            </div>
            <div style={{ fontSize: '0.7rem', color: '#9CA3AF', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end', marginTop: '2px' }}>
              <BrainCircuit style={{ width: '12px', height: '12px', color: '#06B6D4' }} />
              <span>AI Conf: {(confidence * 100).toFixed(0)}%</span>
            </div>
          </div>

        </div>

      </div>

      {/* Contributing Factors Explanation */}
      {Object.keys(contributing_factors).length > 0 && (
        <div style={{
          marginTop: '14px',
          paddingTop: '12px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          gap: '12px',
          flexWrap: 'wrap'
        }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase' }}>
            Early Indicators:
          </span>
          {Object.entries(contributing_factors).map(([key, msg]) => (
            <span key={key} style={{ fontSize: '0.75rem', color: '#E5E7EB' }}>
              • {msg}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
