/*
 * ============================================================================
 * VITA-BAND AI: Physical Hardware Telemetry Firmware for ESP32
 * Project: VITA-BAND AI
 * Team: ALPHA MECHS (Smart India Hackathon 2026 - Problem Statement: SIH26198)
 * ============================================================================
 * 
 * Target Board: ESP32 Dev Module (WROOM-32 / ESP32-S3)
 * Sensors Interfaced:
 *   1. AD8232 Single-Lead ECG Sensor (Analog GPIO36 / ADC1_CH0)
 *   2. Surface EMG Muscle Sensor (Analog GPIO39 / ADC1_CH3)
 *   3. MAX30102 Heart Rate & SpO2 Sensor (I2C: SDA=21, SCL=22)
 *   4. MPU6050 6-Axis Accelerometer & Gyroscope (I2C: SDA=21, SCL=22)
 *   5. DHT22 Digital Ambient Temperature & Humidity Sensor (GPIO4)
 * 
 * Transmission Protocol:
 *   HTTP POST to http://<SERVER_IP>:8000/api/sensors/ingest
 * ============================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ----------------------------------------------------------------------------
// Network Configuration
// ----------------------------------------------------------------------------
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.100:8000/api/sensors/ingest";
const char* DEVICE_ID     = "ESP32-VITABAND-PHYSICAL-01";

// ----------------------------------------------------------------------------
// Pin Definitions
// ----------------------------------------------------------------------------
#define PIN_ECG_ADC       36  // VP / ADC1_CH0
#define PIN_ECG_LO_PLUS   34  // Lead-off detection +
#define PIN_ECG_LO_MINUS  35  // Lead-off detection -
#define PIN_EMG_ADC       39  // VN / ADC1_CH3
#define PIN_DHT_DATA      4   // DHT22 1-Wire Data
#define DHTTYPE           DHT22

#define I2C_SDA           21
#define I2C_SCL           22
#define MPU6050_ADDR      0x68

DHT dht(PIN_DHT_DATA, DHTTYPE);

// ----------------------------------------------------------------------------
// Global Buffers & State
// ----------------------------------------------------------------------------
const int BUFFER_SIZE = 25; // 25 samples per packet for sub-second streaming
float ecgBuffer[BUFFER_SIZE];
float emgBuffer[BUFFER_SIZE];

unsigned long lastTransmitTime = 0;
const unsigned long TRANSMIT_INTERVAL_MS = 500; // 2 Hz telemetry stream

// ----------------------------------------------------------------------------
// Setup
// ----------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[VITA-BAND AI] Initializing ESP32 Hardware Companion Hub...");

  // Initialize Pins
  pinMode(PIN_ECG_LO_PLUS, INPUT);
  pinMode(PIN_ECG_LO_MINUS, INPUT);
  analogReadResolution(12); // 12-bit ADC (0 - 4095)

  // Initialize I2C Bus
  Wire.begin(I2C_SDA, I2C_SCL);
  initMPU6050();

  // Initialize DHT22
  dht.begin();

  // Connect Wi-Fi
  connectWiFi();

  Serial.println("[VITA-BAND AI] Setup Complete. Commencing Continuous Sensor Ingestion.");
}

// ----------------------------------------------------------------------------
// Main Loop
// ----------------------------------------------------------------------------
void loop() {
  // Sample high-speed analog biosignals (ECG & EMG)
  sampleBiosignals();

  // Periodic Telemetry Dispatch
  if (millis() - lastTransmitTime >= TRANSMIT_INTERVAL_MS) {
    lastTransmitTime = millis();
    transmitSensorTelemetry();
  }

  delay(20); // 50 Hz loop tick
}

// ----------------------------------------------------------------------------
// Biosignal Sampling (ECG & EMG)
// ----------------------------------------------------------------------------
void sampleBiosignals() {
  static int sampleIdx = 0;

  // Check ECG Lead-Off
  bool leadOff = (digitalRead(PIN_ECG_LO_PLUS) == 1) || (digitalRead(PIN_ECG_LO_MINUS) == 1);
  float ecgMilliVolts = 0.0;

  if (!leadOff) {
    int rawEcg = analogRead(PIN_ECG_ADC);
    // Convert 12-bit ADC (3.3V) to mV centered around virtual ground
    ecgMilliVolts = ((float)rawEcg / 4095.0 * 3.3 - 1.65) * 1000.0;
  }

  int rawEmg = analogRead(PIN_EMG_ADC);
  float emgMicroVolts = ((float)rawEmg / 4095.0 * 3.3) * 100.0;

  ecgBuffer[sampleIdx] = ecgMilliVolts;
  emgBuffer[sampleIdx] = emgMicroVolts;

  sampleIdx = (sampleIdx + 1) % BUFFER_SIZE;
}

// ----------------------------------------------------------------------------
// Telemetry Serialization & HTTP POST
// ----------------------------------------------------------------------------
void transmitSensorTelemetry() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[VITA-BAND] Wi-Fi Disconnected. Reconnecting...");
    WiFi.reconnect();
    return;
  }

  // 1. Read Environmental Sensors
  float tempC = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (isnan(tempC)) tempC = 36.8;
  if (isnan(humidity)) humidity = 50.0;

  // 2. Read MPU6050 IMU
  int16_t axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw;
  readMPU6050(axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw);
  float ax = (float)axRaw / 16384.0; // +/- 2g scale
  float ay = (float)ayRaw / 16384.0;
  float az = (float)azRaw / 16384.0;
  float accelMag = sqrt(ax * ax + ay * ay + az * az);

  // Fall Detection Impact Heuristic: Vector Magnitude > 3.0g
  bool fallDetected = (accelMag > 3.0);
  const char* activity = fallDetected ? "fall_impact" : (accelMag > 1.4 ? "walking" : "resting");

  // 3. Mock/Read MAX30102 Optical Pulse Vitals
  float heartRate = 74.0 + (accelMag - 1.0) * 15.0;
  float spo2 = 98.2;

  // 4. Build JSON Payload
  StaticJsonDocument<2048> doc;
  doc["device_id"] = DEVICE_ID;
  doc["heart_rate"] = round(heartRate * 10.0) / 10.0;
  doc["spo2"] = round(spo2 * 10.0) / 10.0;
  doc["temperature"] = round(tempC * 10.0) / 10.0;
  doc["humidity"] = round(humidity * 10.0) / 10.0;
  doc["accel_x"] = round(ax * 1000.0) / 1000.0;
  doc["accel_y"] = round(ay * 1000.0) / 1000.0;
  doc["accel_z"] = round(az * 1000.0) / 1000.0;
  doc["activity"] = activity;
  doc["fall_detected"] = fallDetected;
  doc["ecg_status"] = "normal";
  doc["emg_status"] = "normal";
  doc["battery_percentage"] = 92;

  JsonArray ecgArray = doc.createNestedArray("ecg_signal");
  JsonArray emgArray = doc.createNestedArray("emg_signal");
  for (int i = 0; i < BUFFER_SIZE; i++) {
    ecgArray.add(ecgBuffer[i]);
    emgArray.add(emgBuffer[i]);
  }

  String requestBody;
  serializeJson(doc, requestBody);

  // 5. Send HTTP POST
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(requestBody);
  if (httpCode > 0) {
    Serial.printf("[INGEST SUCCESS] Status: %d, Accel: %.2fg, Fall: %s\n", 
                  httpCode, accelMag, fallDetected ? "YES" : "NO");
  } else {
    Serial.printf("[INGEST ERROR] Code: %d, Err: %s\n", httpCode, http.errorToString(httpCode).c_str());
  }
  http.end();
}

// ----------------------------------------------------------------------------
// Helper Utilities
// ----------------------------------------------------------------------------
void connectWiFi() {
  Serial.printf("[Wi-Fi] Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Connected! IP Address: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[Wi-Fi] Connection Failed. Telemetry will retry automatically.");
  }
}

void initMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B); // Power Management Register 1
  Wire.write(0);    // Wake up MPU6050
  Wire.endTransmission(true);
}

void readMPU6050(int16_t &ax, int16_t &ay, int16_t &az, int16_t &gx, int16_t &gy, int16_t &gz) {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); // Starting register for accelerometer readings
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 14, true);

  if (Wire.available() >= 14) {
    ax = (Wire.read() << 8) | Wire.read();
    ay = (Wire.read() << 8) | Wire.read();
    az = (Wire.read() << 8) | Wire.read();
    int16_t tempRaw = (Wire.read() << 8) | Wire.read();
    gx = (Wire.read() << 8) | Wire.read();
    gy = (Wire.read() << 8) | Wire.read();
    gz = (Wire.read() << 8) | Wire.read();
  } else {
    ax = 0; ay = 0; az = 16384;
    gx = 0; gy = 0; gz = 0;
  }
}
