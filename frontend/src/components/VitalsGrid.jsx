import React from 'react';
import { Heart, Droplets, Thermometer, Wind, Footprints, AlertCircle } from 'lucide-react';

export default function VitalsGrid({ vitals }) {
  if (!vitals) return null;

  const {
    heart_rate = 75,
    spo2 = 98.5,
    temperature = 36.8,
    humidity = 52.0,
    activity = 'resting',
    fall_detected = false,
    ecg_status = 'normal',
    emg_status = 'normal',
  } = vitals;

  const hrStatusColor = heart_rate > 115 || heart_rate < 50 ? '#EF4444' : (heart_rate > 95 ? '#F59E0B' : '#10B981');
  const spo2Color = spo2 < 90 ? '#EF4444' : (spo2 < 95 ? '#F59E0B' : '#06B6D4');
  const tempColor = temperature > 38.5 ? '#EF4444' : (temperature > 37.5 ? '#F59E0B' : '#10B981');
  const fallColor = fall_detected ? '#EF4444' : '#10B981';

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
      gap: '16px',
      marginBottom: '20px'
    }}>
      
      {/* 1. Heart Rate (MAX30102) */}
      <div className="glass-panel" style={{ padding: '18px 20px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Heart Rate
            </span>
            <div className="num-telemetry" style={{ fontSize: '2.4rem', fontWeight: 800, color: hrStatusColor, lineHeight: 1.1, marginTop: '4px' }}>
              {heart_rate.toFixed(0)} <span style={{ fontSize: '0.9rem', color: '#9CA3AF', fontWeight: 500 }}>BPM</span>
            </div>
          </div>
          <div style={{
            background: `${hrStatusColor}1A`,
            padding: '10px',
            borderRadius: '12px',
            border: `1px solid ${hrStatusColor}40`
          }}>
            <Heart style={{ width: '22px', height: '22px', color: hrStatusColor }} />
          </div>
        </div>
        <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#9CA3AF' }}>MAX30102 Optical</span>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            color: hrStatusColor,
            background: `${hrStatusColor}20`,
            padding: '2px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase'
          }}>
            {ecg_status}
          </span>
        </div>
      </div>

      {/* 2. SpO2 Oxygen (MAX30102) */}
      <div className="glass-panel" style={{ padding: '18px 20px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Blood Oxygen (SpO2)
            </span>
            <div className="num-telemetry" style={{ fontSize: '2.4rem', fontWeight: 800, color: spo2Color, lineHeight: 1.1, marginTop: '4px' }}>
              {spo2.toFixed(1)} <span style={{ fontSize: '0.9rem', color: '#9CA3AF', fontWeight: 500 }}>%</span>
            </div>
          </div>
          <div style={{
            background: `${spo2Color}1A`,
            padding: '10px',
            borderRadius: '12px',
            border: `1px solid ${spo2Color}40`
          }}>
            <Droplets style={{ width: '22px', height: '22px', color: spo2Color }} />
          </div>
        </div>
        <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#9CA3AF' }}>Arterial Saturation</span>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            color: spo2Color,
            background: `${spo2Color}20`,
            padding: '2px 8px',
            borderRadius: '4px',
          }}>
            {spo2 >= 95 ? 'OPTIMAL' : (spo2 >= 90 ? 'MILD HYPOXIA' : 'CRITICAL')}
          </span>
        </div>
      </div>

      {/* 3. Body Temperature (DHT22 / Skin) */}
      <div className="glass-panel" style={{ padding: '18px 20px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Temperature
            </span>
            <div className="num-telemetry" style={{ fontSize: '2.4rem', fontWeight: 800, color: tempColor, lineHeight: 1.1, marginTop: '4px' }}>
              {temperature.toFixed(1)} <span style={{ fontSize: '0.9rem', color: '#9CA3AF', fontWeight: 500 }}>°C</span>
            </div>
          </div>
          <div style={{
            background: `${tempColor}1A`,
            padding: '10px',
            borderRadius: '12px',
            border: `1px solid ${tempColor}40`
          }}>
            <Thermometer style={{ width: '22px', height: '22px', color: tempColor }} />
          </div>
        </div>
        <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#9CA3AF' }}>Thermal Index</span>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            color: tempColor,
            background: `${tempColor}20`,
            padding: '2px 8px',
            borderRadius: '4px',
          }}>
            {temperature > 38.5 ? 'HYPERTHERMIA' : (temperature > 37.5 ? 'ELEVATED' : 'NORMAL')}
          </span>
        </div>
      </div>

      {/* 4. Ambient Humidity (DHT22) */}
      <div className="glass-panel" style={{ padding: '18px 20px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Ambient Humidity
            </span>
            <div className="num-telemetry" style={{ fontSize: '2.4rem', fontWeight: 800, color: '#38BDF8', lineHeight: 1.1, marginTop: '4px' }}>
              {humidity.toFixed(0)} <span style={{ fontSize: '0.9rem', color: '#9CA3AF', fontWeight: 500 }}>%</span>
            </div>
          </div>
          <div style={{
            background: 'rgba(56, 189, 248, 0.1)',
            padding: '10px',
            borderRadius: '12px',
            border: '1px solid rgba(56, 189, 248, 0.25)'
          }}>
            <Wind style={{ width: '22px', height: '22px', color: '#38BDF8' }} />
          </div>
        </div>
        <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#9CA3AF' }}>DHT22 Environmental</span>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 700,
            color: '#38BDF8',
            background: 'rgba(56, 189, 248, 0.15)',
            padding: '2px 8px',
            borderRadius: '4px',
          }}>
            {humidity > 70 ? 'HIGH MOISTURE' : (humidity < 30 ? 'DRY' : 'COMFORT')}
          </span>
        </div>
      </div>

      {/* 5. Activity & Fall Posture (MPU6050) */}
      <div className="glass-panel" style={{ padding: '18px 20px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Activity & Kinematics
            </span>
            <div style={{ fontSize: '1.45rem', fontWeight: 800, color: fallColor, lineHeight: 1.2, marginTop: '8px', textTransform: 'uppercase' }}>
              {activity.replace('_', ' ')}
            </div>
          </div>
          <div style={{
            background: `${fallColor}1A`,
            padding: '10px',
            borderRadius: '12px',
            border: `1px solid ${fallColor}40`
          }}>
            <Footprints style={{ width: '22px', height: '22px', color: fallColor }} />
          </div>
        </div>
        <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.7rem', color: '#9CA3AF' }}>MPU6050 IMU</span>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: 800,
            color: fallColor,
            background: `${fallColor}20`,
            padding: '2px 8px',
            borderRadius: '4px',
          }}>
            {fall_detected ? 'IMPACT DETECTED' : 'NORMAL POSTURE'}
          </span>
        </div>
      </div>

    </div>
  );
}
