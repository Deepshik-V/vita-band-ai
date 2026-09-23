import React from 'react';
import { Activity, ShieldAlert, Wifi, BatteryCharging, Radio, Bell } from 'lucide-react';

export default function Header({ wsStatus, battery = 94, onTriggerSos, isSimActive, scenarioName }) {
  const isConnected = wsStatus === 'connected';

  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand & Team ID */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)'
          }}>
            <Activity style={{ width: '26px', height: '26px', color: '#FFFFFF' }} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFFFFF' }}>
                VITA-BAND <span style={{ color: '#06B6D4' }}>AI</span>
              </h1>
              <span style={{
                background: 'rgba(6, 182, 212, 0.15)',
                color: '#38BDF8',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                padding: '2px 8px',
                borderRadius: '6px',
                fontSize: '0.7rem',
                fontWeight: 700,
                letterSpacing: '0.05em'
              }}>
                SIH26198
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#9CA3AF', marginTop: '2px' }}>
              Personal Health Companion • <span style={{ color: '#E5E7EB', fontWeight: 600 }}>ALPHA MECHS</span>
            </p>
          </div>
        </div>

        {/* Telemetry Status Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          
          {/* Active Mode */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '0.75rem',
            border: '1px solid var(--border-subtle)'
          }}>
            <Radio style={{ width: '14px', height: '14px', color: isSimActive ? '#F59E0B' : '#10B981' }} />
            <span style={{ color: '#9CA3AF' }}>Mode:</span>
            <span style={{ color: '#F3F4F6', fontWeight: 600 }}>
              {isSimActive ? `SIM: ${scenarioName}` : 'LIVE STREAM'}
            </span>
          </div>

          {/* Connection Status */}
          {(() => {
            let bg = 'rgba(239, 68, 68, 0.1)';
            let border = 'rgba(239, 68, 68, 0.3)';
            let color = '#EF4444';
            let label = 'DISCONNECTED';

            if (wsStatus === 'connected') {
              bg = 'rgba(16, 185, 129, 0.1)';
              border = 'rgba(16, 185, 129, 0.3)';
              color = '#10B981';
              label = 'STREAM CONNECTED';
            } else if (wsStatus === 'reconnecting') {
              bg = 'rgba(245, 158, 11, 0.15)';
              border = 'rgba(245, 158, 11, 0.4)';
              color = '#F59E0B';
              label = 'RECONNECTING...';
            } else if (wsStatus === 'connecting') {
              bg = 'rgba(6, 182, 212, 0.15)';
              border = 'rgba(6, 182, 212, 0.4)';
              color = '#06B6D4';
              label = 'CONNECTING...';
            }

            return (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: bg,
                padding: '6px 14px',
                borderRadius: '20px',
                fontSize: '0.75rem',
                fontWeight: 600,
                border: `1px solid ${border}`,
                color: color,
                transition: 'all 0.3s ease',
              }}>
                <span className="badge-dot" style={{ background: color }} />
                <Wifi style={{ width: '14px', height: '14px' }} />
                <span>{label}</span>
              </div>
            );
          })()}

          {/* Battery */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.05)',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '0.75rem',
            border: '1px solid var(--border-subtle)'
          }}>
            <BatteryCharging style={{ width: '15px', height: '15px', color: '#10B981' }} />
            <span style={{ fontWeight: 600 }}>{battery}%</span>
          </div>

          {/* SOS Trigger Button */}
          <button
            id="btn-header-sos"
            onClick={onTriggerSos}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
              color: '#FFFFFF',
              border: 'none',
              padding: '8px 18px',
              borderRadius: '10px',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: 'pointer',
              boxShadow: '0 0 15px rgba(239, 68, 68, 0.4)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.04)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <ShieldAlert style={{ width: '16px', height: '16px' }} />
            <span>TRIGGER SOS</span>
          </button>

        </div>
      </div>
    </header>
  );
}
