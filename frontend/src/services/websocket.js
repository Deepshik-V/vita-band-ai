/**
 * Real-time WebSocket Stream Client for VITA-BAND AI
 * Manages resilient bidirectional connection with automatic backoff reconnection,
 * status lifecycle notifications, and telemetry payload delivery.
 */
class TelemetryWebSocketClient {
  constructor() {
    this.ws = null;
    this.subscribers = new Set();
    this.statusSubscribers = new Set();
    this.isConnected = false;
    this.isManualDisconnect = false;
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 20;
    this.currentStatus = 'disconnected';
    this.url = '';
  }

  /**
   * Resolves target WebSocket URL based on environment or window location.
   */
  resolveUrl(customUrl = null) {
    if (customUrl) return customUrl;

    // 1. Explicit VITE_WS_URL takes highest priority
    const envWsUrl = import.meta?.env?.VITE_WS_URL;
    if (envWsUrl && typeof envWsUrl === 'string' && envWsUrl.trim() !== '') {
      return envWsUrl.trim().replace(/\/+$/, '');
    }

    // 2. Derive WebSocket URL from VITE_API_URL if configured
    const envApiUrl = import.meta?.env?.VITE_API_URL;
    if (envApiUrl && typeof envApiUrl === 'string' && envApiUrl.trim() !== '') {
      const cleanApi = envApiUrl.trim().replace(/\/+$/, '');
      if (cleanApi.startsWith('https://')) {
        return cleanApi.replace('https://', 'wss://') + '/ws/health-stream';
      }
      if (cleanApi.startsWith('http://')) {
        return cleanApi.replace('http://', 'ws://') + '/ws/health-stream';
      }
      return `wss://${cleanApi}/ws/health-stream`;
    }

    if (typeof window === 'undefined') return 'ws://127.0.0.1:8000/ws/health-stream';

    const loc = window.location;
    const protocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // In local development (port 3000 / 5173), direct connect to backend on port 8000
    if (loc.port === '3000' || loc.port === '5173') {
      const hostname = (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1')
        ? '127.0.0.1'
        : loc.hostname;
      return `${protocol}//${hostname}:8000/ws/health-stream`;
    }

    // In production or reverse proxy, use current host with wss: on https:
    return `${protocol}//${loc.host}/ws/health-stream`;
  }

  connect(url = null) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isManualDisconnect = false;
    this.url = this.resolveUrl(url);

    this._notifyStatus('connecting');

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this._notifyStatus('connected');
        console.log('[VITA_WS] Connected to telemetry stream:', this.url);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this._notifyData(data);
        } catch (err) {
          console.error('[VITA_WS] Message parse error:', err);
        }
      };

      this.ws.onclose = (event) => {
        this.isConnected = false;
        this.ws = null;

        if (this.isManualDisconnect) {
          this._notifyStatus('disconnected');
          console.log('[VITA_WS] Closed intentionally.');
        } else {
          this._notifyStatus('disconnected');
          console.warn(`[VITA_WS] Disconnected (code: ${event.code}), scheduling auto-reconnect...`);
          this._scheduleReconnect();
        }
      };

      this.ws.onerror = (err) => {
        console.error('[VITA_WS] WebSocket error:', err);
        // Closing the socket will trigger onclose and schedule reconnect
        if (this.ws && this.ws.readyState !== WebSocket.CLOSED) {
          this.ws.close();
        }
      };
    } catch (err) {
      console.error('[VITA_WS] Failed to instantiate WebSocket:', err);
      this.ws = null;
      this.isConnected = false;
      this._notifyStatus('disconnected');
      if (!this.isManualDisconnect) {
        this._scheduleReconnect();
      }
    }
  }

  _scheduleReconnect() {
    if (this.isManualDisconnect || this.reconnectTimer) return;

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`[VITA_WS] Max reconnect attempts (${this.maxReconnectAttempts}) reached.`);
      this._notifyStatus('failed');
      return;
    }

    this.reconnectAttempts += 1;
    // Exponential backoff: 1s, 1.5s, 2.25s, max 5s
    const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts - 1), 5000);

    this._notifyStatus('reconnecting', { attempt: this.reconnectAttempts, delay });
    console.log(`[VITA_WS] Reconnecting in ${Math.round(delay)}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (!this.isManualDisconnect) {
        this.connect(this.url);
      }
    }, delay);
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  subscribeStatus(callback) {
    this.statusSubscribers.add(callback);
    callback(this.currentStatus);
    return () => this.statusSubscribers.delete(callback);
  }

  _notifyData(data) {
    for (const sub of this.subscribers) {
      try {
        sub(data);
      } catch (e) {
        console.error('[VITA_WS] Subscriber error:', e);
      }
    }
  }

  _notifyStatus(status, metadata = {}) {
    this.currentStatus = status;
    for (const sub of this.statusSubscribers) {
      try {
        sub(status, metadata);
      } catch (e) {
        console.error('[VITA_WS] Status sub error:', e);
      }
    }
  }

  sendPing() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'ping', timestamp: new Date().toISOString() }));
      return true;
    }
    return false;
  }

  disconnect() {
    this.isManualDisconnect = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      try {
        this.ws.close(1000, 'User initiated disconnect');
      } catch (e) {
        // socket may already be closing
      }
      this.ws = null;
    }
    this.isConnected = false;
    this._notifyStatus('disconnected');
  }

  reconnectNow() {
    this.disconnect();
    this.connect();
  }
}

export const wsClient = new TelemetryWebSocketClient();

