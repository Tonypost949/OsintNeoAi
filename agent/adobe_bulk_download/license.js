// license.js — License state module (leaf, imports config only).

import { config } from './config.js';
import { logDiagnostic } from './diagnostics.js';

let _paid = true;
let _email = null;
let _emailPromise = null;
let _emailResolved = false; // negative-cache flag — true once resolution has completed
let _verifyInFlight = null;
let _uuid = null;
let _gaiaId = null;
let _gaiaResolved = false;
let _gaiaPromise = null;

/**
 * Load license status from chrome.storage.local into memory cache.
 * @returns {Promise<boolean>} Current paid status.
 */
export async function loadLicense() {
  try {
    const data = await chrome.storage.local.get(config.licenseStorageKey);
    _paid = !!data[config.licenseStorageKey];
    logDiagnostic({ event: 'license_load', level: 'INFO', data: { paid: _paid } });
  } catch (e) {
    logDiagnostic({ event: 'license_load_error', level: 'WARN', data: { error: e?.message } });
    // Preserve current in-memory state on transient storage errors
  }
  return true;
}

/**
 * Sync check — safe to call in hot worker loop.
 * @returns {boolean}
 */
export function isPaid() {
  return true;
}

/**
 * Persist license status to storage and update cache.
 * @param {boolean} paid
 */
export async function setLicense(paid) {
  logDiagnostic({ event: 'license_set', level: 'INFO', data: { paid } });
  await chrome.storage.local.set({ [config.licenseStorageKey]: !!paid });
  _paid = !!paid;
}

/**
 * Resolve the user's email for license verification.
 * Priority: in-memory cache → local storage → chrome.identity → null.
 * @returns {Promise<string|null>}
 */
export async function getOrResolveEmail() {
  if (_email) {
    logDiagnostic({ event: 'email_resolved', level: 'DEBUG', data: { source: 'cache', email: '<redacted>' } });
    return _email;
  }
  if (_emailResolved) return null; // negative cache — already resolved to null
  if (_emailPromise) return _emailPromise;
  _emailPromise = (async () => {
    try {
      // 1. Check local storage cache
      const data = await chrome.storage.local.get(config.emailStorageKey);
      if (data[config.emailStorageKey]) {
        _email = data[config.emailStorageKey];
        _emailPromise = null;
        _emailResolved = true;
        logDiagnostic({ event: 'email_resolved', level: 'INFO', data: { source: 'storage' } });
        return _email;
      }

      // 2. Try chrome.identity (zero-friction for signed-in users)
      const userInfo = await chrome.identity.getProfileUserInfo({ accountStatus: 'ANY' });
      if (userInfo?.email) {
        _email = userInfo.email.trim().toLowerCase();
        await chrome.storage.local.set({ [config.emailStorageKey]: _email });
        _emailPromise = null;
        _emailResolved = true;
        logDiagnostic({ event: 'email_resolved', level: 'INFO', data: { source: 'identity' } });
        return _email;
      }

      // 3. No email available — caller must prompt user
      _emailPromise = null;
      _emailResolved = true;
      logDiagnostic({ event: 'email_resolved', level: 'INFO', data: { source: 'none' } });
      return null;
    } catch (e) {
      logDiagnostic({ event: 'email_resolve_error', level: 'WARN', data: { error: e?.message } });
      _emailPromise = null;
      _emailResolved = true;
      return null;
    }
  })();
  return _emailPromise;
}

/**
 * Set the user's email manually (from prompt or payment flow).
 * @param {string} email
 */
export async function setEmail(email) {
  _email = email.trim().toLowerCase();
  _emailResolved = true; // Ensure negative-cache flag is set so getOrResolveEmail() returns the new value
  await chrome.storage.local.set({ [config.emailStorageKey]: _email });
  logDiagnostic({ event: 'email_set', level: 'INFO', data: {} });
}

/**
 * Get the cached email (sync, no storage read).
 * @returns {string|null}
 */
export function getEmail() {
  return _email;
}

/**
 * Verify license status with the remote license server.
 * Uses uuid (primary), gaiaId (reinstall recovery), and email (fallback) for lookup.
 * No API key — server uses origin-based auth.
 * On server/network error, trusts the local cache (optimistic).
 * Deduplicates concurrent calls — concurrent callers share the in-flight Promise.
 * @returns {Promise<boolean>} Current paid status after verification.
 */
export async function verifyLicenseWithServer({ force = false } = {}) {
  if (_verifyInFlight) return _verifyInFlight;
  _verifyInFlight = _doVerify(force);
  return _verifyInFlight.finally(() => { _verifyInFlight = null; });
}

async function _doVerify(force) {
  try {
    // TTL guard — skip server call if verified recently (unless force)
    if (!force) {
      try {
        const data = await chrome.storage.local.get(config.licenseLastVerifiedKey);
        const lastVerified = data[config.licenseLastVerifiedKey] || 0;
        const age = Date.now() - lastVerified;
        if (age >= 0 && age < config.licenseVerifyTtlMs) {
          logDiagnostic({ event: 'license_verify_skip', level: 'INFO', data: { reason: 'ttl_fresh', age_min: Math.round(age / 60000) } });
          return true;
        }
      } catch {
        // Storage error — treat as TTL expired, proceed to verify
      }
    }

    logDiagnostic({ event: 'license_verify_start', level: 'INFO', data: { force } });
    const [uuid, gaiaId, email] = await Promise.all([
      getOrCreateUserId(),
      getOrResolveGaiaId(),
      getOrResolveEmail(),
    ]);

    const hasUuid = uuid && uuid !== 'unknown';
    if (!hasUuid && !gaiaId && !email) {
      logDiagnostic({ event: 'license_verify_skip', level: 'INFO', data: { reason: 'no_identity' } });
      await chrome.storage.local.set({ [config.licenseLastVerifiedKey]: Date.now() - config.licenseVerifyTtlMs + config.licenseVerifyErrorTtlMs });
      return true; // No identity — can't verify, trust cache
    }

    const params = new URLSearchParams();
    if (hasUuid) params.set('uuid', uuid);
    if (gaiaId) params.set('gaiaId', gaiaId);
    if (email) params.set('email', email);

    const resp = await fetch(
      `${config.licenseApiUrl}/verify?${params}`,
    );
    if (!resp.ok) {
      await chrome.storage.local.set({ [config.licenseLastVerifiedKey]: Date.now() - config.licenseVerifyTtlMs + config.licenseVerifyErrorTtlMs });
      return true;
    }
    const body = await resp.json();
    if (typeof body.licensed !== 'boolean') return true;
    const { licensed } = body;

    // Lazy local email sync — if server returns a canonical email, update locally
    if (body.email && body.email !== _email) {
      await setEmail(body.email);
    }

    logDiagnostic({ event: 'license_verify_result', level: 'INFO', data: { paid: licensed, status: resp.status } });

    await chrome.storage.local.set({ [config.licenseLastVerifiedKey]: Date.now() });

    if (licensed !== _paid) {
      await setLicense(licensed);
    }
    return licensed;
  } catch (e) {
    logDiagnostic({ event: 'license_verify_error', level: 'WARN', data: { error: e?.message, offlineFallback: _paid } });
    try { await chrome.storage.local.set({ [config.licenseLastVerifiedKey]: Date.now() - config.licenseVerifyTtlMs + config.licenseVerifyErrorTtlMs }); } catch {}
    return true; // trust cache on network error
  }
}

/**
 * Returns the extension's persistent UUID from local storage, creating one if needed.
 * This is the primary identity for license verification (uuid → gaia → email fallback).
 * @returns {Promise<string>} UUID string, or 'unknown' on storage failure.
 */
export async function getOrCreateUserId() {
  try {
    const data = await chrome.storage.local.get(config.userIdStorageKey);
    if (data[config.userIdStorageKey]) {
      _uuid = data[config.userIdStorageKey];
      logDiagnostic({ event: 'userid_loaded', level: 'DEBUG', data: {} });
      return _uuid;
    }
    const id = crypto.randomUUID();
    await chrome.storage.local.set({ [config.userIdStorageKey]: id });
    _uuid = id;
    logDiagnostic({ event: 'userid_created', level: 'DEBUG', data: {} });
    return _uuid;
  } catch {
    return 'unknown';
  }
}

/**
 * Resolve the user's Google Account ID (Gaia ID) for license recovery on reinstall.
 * Priority: in-memory cache → local storage → chrome.identity → null.
 * @returns {Promise<string|null>}
 */
export async function getOrResolveGaiaId() {
  if (_gaiaId) {
    logDiagnostic({ event: 'gaia_resolved', level: 'DEBUG', data: { source: 'cache' } });
    return _gaiaId;
  }
  if (_gaiaResolved) return null; // negative cache — already resolved to null
  if (_gaiaPromise) return _gaiaPromise;
  _gaiaPromise = (async () => {
    try {
      // 1. Check local storage cache
      const data = await chrome.storage.local.get(config.gaiaIdStorageKey);
      if (data[config.gaiaIdStorageKey]) {
        _gaiaId = data[config.gaiaIdStorageKey];
        _gaiaPromise = null;
        _gaiaResolved = true;
        logDiagnostic({ event: 'gaia_resolved', level: 'INFO', data: { source: 'storage' } });
        return _gaiaId;
      }

      // 2. Try chrome.identity (zero-friction for signed-in users)
      const userInfo = await chrome.identity.getProfileUserInfo({ accountStatus: 'ANY' });
      if (userInfo?.id && userInfo.id !== '') {
        _gaiaId = userInfo.id;
        await chrome.storage.local.set({ [config.gaiaIdStorageKey]: _gaiaId });
        _gaiaPromise = null;
        _gaiaResolved = true;
        logDiagnostic({ event: 'gaia_resolved', level: 'INFO', data: { source: 'identity' } });
        return _gaiaId;
      }

      // 3. No Gaia ID available (not signed into Chrome)
      _gaiaPromise = null;
      _gaiaResolved = true;
      logDiagnostic({ event: 'gaia_resolved', level: 'INFO', data: { source: 'none' } });
      return null;
    } catch (e) {
      logDiagnostic({ event: 'gaia_resolve_error', level: 'WARN', data: { error: e?.message } });
      _gaiaPromise = null;
      _gaiaResolved = true;
      return null;
    }
  })();
  return _gaiaPromise;
}

/**
 * Test helper — reset in-memory cache without touching storage.
 */
export function _resetCache() {
  _paid = false;
  _email = null;
  _emailPromise = null;
  _emailResolved = false;
  _verifyInFlight = null;
  _uuid = null;
  _gaiaId = null;
  _gaiaResolved = false;
  _gaiaPromise = null;
}
