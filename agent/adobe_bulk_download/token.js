// token.js — Centralized token cache with chrome.storage.session persistence (ES module).
// Breaks circular import: background.js -> scanner.js -> api.js -> background.js (getToken).
// Persists to chrome.storage.session so token survives SW termination.

import { config } from './config.js';
import { events } from './events.js';
import { logDiagnostic } from './diagnostics.js';

const JWT_PATTERN = /^[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_\-+/=]{10,}$/;

let _cachedToken = null;
let _tokenExpiry = null;
let _warningEmitted = false;
let _expiredEmitted = false;

/** Return the cached access token, or null if unavailable/expired.
 *  Does NOT clear the token on expiry — checkTokenExpiry() is the sole cleanup
 *  authority so it can reliably emit the token_expired event. */
export function getToken() {
  if (!_cachedToken) return null;
  if (_tokenExpiry != null && Date.now() >= _tokenExpiry) {
    logDiagnostic({ event: 'token_get_expired', level: 'DEBUG' });
    return null;
  }
  return _cachedToken;
}

/** Cache an access token with optional expiry timestamp. Also persists to session storage.
 *  Returns true if accepted, false if rejected (format/length validation).
 */
export function setToken(token, expiry = null, { silent = false } = {}) {
  if (typeof token !== 'string' || token.length === 0) {
    if (!silent) events.emit('token_validation_failed', { reason: 'empty or non-string' });
    return false;
  }
  if (token.length > config.maxTokenLength) {
    if (!silent) events.emit('token_validation_failed', { reason: `exceeds max length (${config.maxTokenLength})` });
    return false;
  }
  if (!JWT_PATTERN.test(token)) {
    if (!silent) events.emit('token_validation_failed', { reason: 'not a valid JWT format' });
    return false;
  }
  // Normalize expiry to millisecond timestamp.
  // - ISO date string (e.g. "2026-03-20T06:51:24.416Z"): parse to ms
  // - Numeric seconds (< 1e12): convert to ms
  // - Numeric milliseconds (>= 1e12): pass through
  if (expiry != null && typeof expiry === 'string') {
    const parsed = new Date(expiry).getTime();
    expiry = Number.isNaN(parsed) ? null : parsed;
  } else if (expiry != null && typeof expiry === 'number' && expiry > 0 && expiry < 1e12) {
    expiry *= 1000;
  }
  if (_cachedToken === token && _tokenExpiry === expiry) return true;
  _cachedToken = token;
  _tokenExpiry = expiry ?? null;
  _warningEmitted = false;
  _expiredEmitted = false;
  _scheduleExpiryAlarm();
  chrome.storage.session.set({ abd_token: token, abd_tokenExpiry: expiry ?? null }).catch(() => {});
  return true;
}

/** Clear the cached token and session storage. */
export function clearToken() {
  logDiagnostic({ event: 'token_cleared', level: 'INFO' });
  _cachedToken = null;
  _tokenExpiry = null;
  _warningEmitted = false;
  _expiredEmitted = false;
  try { chrome.alarms.clear(config.expiryCheckAlarmName); } catch {}
  chrome.storage.session.remove(['abd_token', 'abd_tokenExpiry']).catch(() => {});
}

/** Restore token from chrome.storage.session on SW wake. Call once at startup. */
export async function restoreToken() {
  try {
    const data = await chrome.storage.session.get(['abd_token', 'abd_tokenExpiry']);
    if (data.abd_token) {
      if (data.abd_tokenExpiry == null || Date.now() < data.abd_tokenExpiry) {
        if (!setToken(data.abd_token, data.abd_tokenExpiry || null, { silent: true })) {
          logDiagnostic({ event: 'token_restore_invalid', level: 'WARN' });
          chrome.storage.session.remove(['abd_token', 'abd_tokenExpiry']).catch(() => {});
        }
      } else {
        logDiagnostic({ event: 'token_restore_expired', level: 'WARN' });
        chrome.storage.session.remove(['abd_token', 'abd_tokenExpiry']).catch(() => {});
      }
    }
  } catch { logDiagnostic({ event: 'token_restore_failed', level: 'WARN' }); }
}

function _scheduleExpiryAlarm() {
  if (_tokenExpiry == null) return;
  try {
    chrome.alarms.create(config.expiryCheckAlarmName, { periodInMinutes: 1 });
  } catch (e) {
    logDiagnostic({ event: 'expiry_alarm_failed', level: 'WARN', data: { error: e?.message } });
  }
  // Check immediately in case token is already near-expiry or expired —
  // the alarm won't fire for up to 60s, so this closes the gap.
  checkTokenExpiry();
}

/** Check token expiry and emit warning/expired events. Called by alarm handler. */
export function checkTokenExpiry() {
  if (!_cachedToken || _tokenExpiry == null) return;
  const now = Date.now();
  if (now >= _tokenExpiry && !_expiredEmitted) {
    _expiredEmitted = true;
    _cachedToken = null;
    _tokenExpiry = null;
    chrome.storage.session.remove(['abd_token', 'abd_tokenExpiry']).catch(() => {});
    try { chrome.alarms.clear(config.expiryCheckAlarmName); } catch {}
    events.emit('token_expired', {});
    return;
  }
  if (_tokenExpiry - now <= config.tokenExpiryWarningMs && !_warningEmitted) {
    _warningEmitted = true;
    events.emit('token_expiry_warning', { remainingMs: _tokenExpiry - now });
  }
}
