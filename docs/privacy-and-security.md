# VITA-BAND AI: Privacy, Security, and Data Governance

**Project**: VITA-BAND AI  
**Team**: ALPHA MECHS  
**SIH Problem Statement ID**: SIH26198  

---

## 1. Privacy-by-Design Architecture

Medical and physiological data is highly confidential. VITA-BAND AI is architected from the ground up to respect user sovereignty, ensure privacy preservation, and avoid unnecessary external exposure:

1. **Local-First Processing**:
   - Signal filtering, feature engineering, and AI risk detection execute entirely on the local device / companion gateway.
   - Raw microvolt biosignals (ECG and EMG arrays) are processed in volatile memory and are not perpetually stored unless explicitly requested by the user.
2. **Zero Mandatory Cloud Transmission**:
   - The entire platform functions in offline/air-gapped mode.
   - External cloud integration is optional and modular, never a prerequisite for baseline operation.
3. **Data Minimization**:
   - The persistent SQLite store retains only high-level aggregated vitals (HR, SpO2, Temp, Humidity, Risk Score) and critical event logs, discarding high-frequency raw electrical noise buffers.

---

## 2. Secrets Management & Credential Safety

- **No Hardcoded Secrets**: All system parameters, credentials, contact phone numbers, and webhook targets are loaded via environment variables using `.env.example` as a template.
- **Git Protection**: `.gitignore` strictly excludes `.env`, `*.db`, and temporary caches.
- **Safe Mocking**: Emergency SMS dispatches and external calls are mocked in demo mode to prevent accidental telecommunication charges or false emergency calls.

---

## 3. Data Governance Table

| Data Field | Collection Purpose | Storage Location | Retention Policy | Cloud Transmission |
| :--- | :--- | :--- | :--- | :--- |
| **Heart Rate & SpO2** | Cardiovascular & hypoxia monitoring | Local SQLite / Memory | Rolling 120s buffer + hourly records | Optional |
| **ECG Waveform** | Arrhythmia verification | In-Memory stream only | Discarded after real-time canvas draw | None |
| **EMG Muscle Activity** | Fatigue index quantification | In-Memory stream only | Discarded after RMS calculation | None |
| **Temperature & Humidity** | Environmental heat stress index | Local SQLite | Rolling buffer | Optional |
| **Acceleration & Gyro** | Fall impact detection | In-Memory | Discarded unless acute fall triggered | None |
| **Emergency Contacts** | SOS alert target notification | Local configuration (`.env`) | Persistent until changed by user | Local only |

---

## 4. Production Security Hardening Recommendations

For hospital or defense deployments:
- Enforce TLS 1.3 (`https://` and `wss://`) on all external interfaces.
- Encrypt SQLite storage at rest using SQLCipher (AES-256).
- Implement mutual TLS (mTLS) or pre-shared key (PSK) token authentication for physical ESP32 hardware ingest.
- Enforce Role-Based Access Control (RBAC) separating patient and physician views.
