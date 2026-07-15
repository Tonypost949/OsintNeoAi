/**
 * GA4 funnel analytics via Worker proxy.
 * Fire-and-forget — never blocks or affects core functionality.
 */
import { config } from './config.js';
import { getOrCreateUserId } from './license.js';

const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const STORAGE_KEY_SESSION = 'abd_analytics_session';

let _cachedSession = null;

async function getOrRotateSession() {
  try {
    if (!_cachedSession) {
      const stored = await chrome.storage.local.get(STORAGE_KEY_SESSION);
      _cachedSession = stored[STORAGE_KEY_SESSION] || null;
    }
    const now = Date.now();
    if (_cachedSession && (now - _cachedSession.last_activity) < SESSION_TIMEOUT_MS) {
      _cachedSession.last_activity = now;
      chrome.storage.local.set({ [STORAGE_KEY_SESSION]: _cachedSession }).catch(() => {});
      return _cachedSession.session_id;
    }
    // New session
    _cachedSession = {
      session_id: String(now),
      last_activity: now,
    };
    chrome.storage.local.set({ [STORAGE_KEY_SESSION]: _cachedSession }).catch(() => {});
    return _cachedSession.session_id;
  } catch {
    return String(Math.floor(Date.now() / 1000));
  }
}

export function _resetSessionCache() {
  _cachedSession = null;
}

export async function trackEvent(name, params = {}) {
  try {
    if (!config.licenseApiUrl) return;

    // Check opt-out
    const optOut = await chrome.storage.local.get(config.analyticsOptOutKey);
    if (optOut[config.analyticsOptOutKey]) return;

    const clientId = await getOrCreateUserId();
    const sessionId = await getOrRotateSession();

    const body = {
      client_id: clientId,
      events: [{
        name,
        params: { session_id: sessionId, ...params },
      }],
    };

    fetch(`${config.licenseApiUrl}/analytics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).catch(() => {});  // Fire and forget
  } catch {
    // Never let analytics affect the extension
  }
}
