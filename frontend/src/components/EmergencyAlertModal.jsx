import React, { useState } from 'react';
import { AlertOctagon, PhoneCall, Check, X, ShieldAlert } from 'lucide-react';
import { acknowledgeAlert } from '../services/api';

export default function EmergencyAlertModal({ activeAlert, onDismiss }) {
  const [loading, setLoading] = useState(false);

  if (!activeAlert || activeAlert.acknowledged) return null;

  const {
    alert_id,
    alert_type = 'FALL_DETECTED',
    message = 'Sudden high acceleration impact followed by immobility!',
    countdown_seconds = 15,
    target_contact = '+91 9876543210',
    dispatched = false,
  } = activeAlert;

  const handleAcknowledge = async () => {
    setLoading(true);
    try {
      await acknowledgeAlert(alert_id);
      if (onDismiss) onDismiss();
    } catch (err) {
      console.error('[ACK_ERROR]', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 7, 13, 0.85)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px',
    }}>
      <div
        className="alarm-active"
        style={{
          background: '#0F172A',
          border: '2px solid #EF4444',
          borderRadius: '24px',
          maxWidth: '520px',
          width: '100%',
          padding: '32px 28px',
          textAlign: 'center',
          boxShadow: '0 0 60px rgba(239, 68, 68, 0.6)',
        }}
      >
        {/* Pulsing Icon */}
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.2)',
          border: '2px solid #EF4444',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
          boxShadow: '0 0 30px rgba(239, 68, 68, 0.5)'
        }}>
          <AlertOctagon style={{ width: '40px', height: '40px', color: '#EF4444' }} />
        </div>

        {/* Title */}
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '8px' }}>
          {alert_type === 'FALL_DETECTED' ? 'FALL IMPACT DETECTED!' : 'EMERGENCY HEALTH ALERT'}
        </h2>

        {/* Message */}
        <p style={{ fontSize: '0.95rem', color: '#E2E8F0', marginBottom: '20px', lineHeight: 1.5 }}>
          {message}
        </p>

        {/* Countdown display */}
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '16px',
          padding: '16px',
          marginBottom: '24px',
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#F87171', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {dispatched ? 'EMERGENCY DISPATCH INITIATED' : 'AUTOMATIC DISPATCH COUNTDOWN'}
          </div>
          <div className="num-telemetry" style={{ fontSize: '3rem', fontWeight: 900, color: '#EF4444', lineHeight: 1.1, margin: '6px 0' }}>
            {countdown_seconds}s
          </div>
          <div style={{ fontSize: '0.8rem', color: '#94A3B8', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
            <PhoneCall style={{ width: '14px', height: '14px', color: '#38BDF8' }} />
            <span>Target Contact: <strong>{target_contact}</strong></span>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          
          {/* I am fine button (cancel) */}
          <button
            id="btn-alert-dismiss"
            onClick={handleAcknowledge}
            disabled={loading}
            style={{
              flex: 1,
              minWidth: '180px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              background: 'rgba(16, 185, 129, 0.2)',
              border: '1.5px solid #10B981',
              color: '#34D399',
              padding: '14px 20px',
              borderRadius: '12px',
              fontWeight: 800,
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(16, 185, 129, 0.35)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(16, 185, 129, 0.2)'}
          >
            <Check style={{ width: '18px', height: '18px' }} />
            <span>I'M OK (CANCEL ALERT)</span>
          </button>

          {/* Confirm SOS button */}
          <button
            id="btn-alert-dispatch-now"
            onClick={handleAcknowledge}
            disabled={loading}
            style={{
              flex: 1,
              minWidth: '180px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              background: '#DC2626',
              border: '1.5px solid #EF4444',
              color: '#FFFFFF',
              padding: '14px 20px',
              borderRadius: '12px',
              fontWeight: 800,
              fontSize: '0.9rem',
              cursor: 'pointer',
              boxShadow: '0 0 20px rgba(239, 68, 68, 0.6)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <ShieldAlert style={{ width: '18px', height: '18px' }} />
            <span>DISPATCH SOS NOW</span>
          </button>

        </div>

        <p style={{ fontSize: '0.7rem', color: '#64748B', marginTop: '16px' }}>
          * Safe Demo Mode: Does not dial public 112/911. Dispatches mock test notification to registered companion webhook.
        </p>

      </div>
    </div>
  );
}
