// diagnostics.js — Persistent diagnostic ring buffer backed by IndexedDB.
// Stores diagnostic events with 200K cap and 7-day TTL. Survives browser restarts.

import { config } from './config.js';
import * as store from './diag-store.js';

const MAX_ENTRIES = config.diagMaxEntries || 200000;

/** Severity hierarchy — higher number = more severe. */
export const LEVELS = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };

/**
 * Event-to-severity mapping. Consumer 7 (background.js) uses this to tag
 * every event bus entry with a severity level before writing to the ring buffer.
 */
export const EVENT_LEVELS = {
  // ERROR
  file_fail: 'ERROR',
  file_save_error: 'ERROR',
  scan_error: 'ERROR',
  scan_failed: 'ERROR',
  auth_expired: 'ERROR',
  token_expired: 'ERROR',
  psdc_conversion_timeout: 'ERROR',
  aic_conversion_timeout: 'ERROR',
  unhandled_error: 'ERROR',
  sw_recovery_failed: 'ERROR',
  scan_persist_failed: 'ERROR',
  toplevel_scan_error: 'ERROR',
  toplevel_download_error: 'ERROR',
  toplevel_retry_error: 'ERROR',

  // WARN
  http_retry: 'WARN',
  file_retry: 'WARN',
  file_retry_queued: 'WARN',
  rate_limit: 'WARN',
  network_timeout: 'WARN',
  psdc_conversion_retry: 'WARN',
  psdc_raw_fallback_start: 'WARN',
  psdc_psd_fallback_attempt: 'WARN',
  psdc_download_method_list_failed: 'WARN',
  psdc_job_recovery_failed: 'WARN',
  aic_conversion_retry: 'WARN',
  aic_raw_fallback_start: 'WARN',
  aic_propagation_exhausted: 'WARN',
  aic_job_recovery_failed: 'WARN',
  aic_predict_failed: 'WARN',
  aic_job_id_invalid: 'WARN',
  aic_poll_malformed_response: 'WARN',
  fallback_attempt: 'WARN',
  tier_fallback: 'WARN',
  size_warning: 'WARN',
  path_truncated: 'WARN',
  scan_depth_limit: 'WARN',
  scan_fallback_triggered: 'WARN',
  scan_region_resolved: 'WARN',
  ffgen_raw_fallback_start: 'WARN',
  ffgen_manifest_failed: 'WARN',
  ffgenaud_presigned_failed: 'WARN',
  scan_region_cycle: 'INFO',
  token_invalid: 'WARN',
  token_validation_failed: 'WARN',
  token_expiry_warning: 'WARN',
  resume_prompt_timeout: 'WARN',
  free_count_persist_failed: 'WARN',
  scan_context_restore_failed: 'WARN',
  direct_url_fallback_to_blob: 'WARN',
  download_summary: 'WARN',
  download_truncated: 'WARN',
  size_mismatch_shadow: 'WARN',
  download_stalled: 'WARN',
  download_zombie_cap: 'WARN',
  expected_size_unavailable: 'WARN',
  blockdownload_unavailable: 'WARN',

  // INFO
  session_initialized: 'INFO',
  session_start: 'INFO',
  scan_start: 'INFO',
  scan_complete: 'INFO',
  scan_region_cycle_start: 'INFO',
  scan_folder: 'INFO',
  scan_summary_line: 'INFO',
  scan_pagination: 'INFO',
  index_response: 'INFO',
  download_start: 'INFO',
  download_complete: 'INFO',
  download_complete_banner: 'INFO',
  retry_failed_start: 'INFO',
  retry_no_failures: 'INFO',
  file_success: 'INFO',
  initializing: 'INFO',
  psdc_conversion_start: 'INFO',
  psdc_conversion_succeeded: 'INFO',
  psdc_job_recovered: 'INFO',
  psdc_job_recovered_via_temppath: 'INFO',
  aic_conversion_start: 'INFO',
  aic_conversion_succeeded: 'INFO',
  aic_conversion_polling: 'INFO',
  aic_raw_fallback_success: 'INFO',
  aic_propagation_ready: 'INFO',
  aic_download_method: 'INFO',
  aic_existing_conversion_found: 'INFO',
  ffgen_manifest_fetch: 'INFO',
  ffgen_component_download: 'INFO',
  ffgen_raw_fallback_success: 'INFO',
  ffgenaud_presigned_fetch: 'INFO',
  resume_accepted: 'INFO',
  resume_declined: 'INFO',
  user_pause: 'INFO',
  user_resume: 'INFO',
  user_stop: 'INFO',
  resume_prompt_persisted: 'INFO',
  sw_recovery: 'INFO',
  capabilities_detected: 'INFO',
  blockdownload_attempt: 'INFO',
  download_reconciled: 'INFO',

  // Worker strip (UI-only, never logged to activity)
  worker_status: 'DEBUG',
  workers_init: 'DEBUG',

  // AIC noise (per-file type_mismatch skips, verbose)
  aic_job_recovery_skipped: 'DEBUG',

  // Licensing — INFO
  license_load: 'INFO',
  license_set: 'INFO',
  license_verify_start: 'INFO',
  license_verify_result: 'INFO',
  license_verify_skip: 'INFO',
  email_resolved: 'INFO',
  email_set: 'INFO',
  msg_set_email: 'INFO',
  msg_check_license: 'INFO',
  msg_activate_license: 'INFO',
  stripe_checkout_open: 'INFO',
  license_poll_start: 'INFO',
  license_poll_success: 'INFO',
  license_restore_attempt: 'INFO',
  license_restore_success: 'INFO',
  license_check_on_load: 'INFO',

  // Licensing — WARN
  license_load_error: 'WARN',
  license_verify_error: 'WARN',
  email_resolve_error: 'WARN',
  msg_get_email_error: 'WARN',
  msg_get_userid_error: 'WARN',
  msg_check_license_error: 'WARN',
  uninstall_url_error: 'WARN',
  stripe_checkout_not_configured: 'WARN',
  license_poll_timeout: 'WARN',
  license_restore_not_found: 'WARN',

  // Licensing — ERROR
  msg_set_email_error: 'ERROR',
  msg_activate_license_error: 'ERROR',
  license_restore_error: 'ERROR',

  // Licensing — DEBUG
  userid_created: 'DEBUG',
  userid_loaded: 'DEBUG',
  msg_get_email: 'DEBUG',
  msg_get_userid: 'DEBUG',
  uninstall_url_updated: 'DEBUG',

  // Everything else defaults to DEBUG
};

/**
 * Recursively cap string values in an object/array to maxLen chars.
 * Prevents oversized entries from bloating the ring buffer.
 */
export function _capStrings(val, maxLen = 300, _depth = 0) {
  if (_depth > 10) return '[max depth]';
  if (val == null) return val;
  if (typeof val === 'string') {
    return val.length > maxLen ? val.slice(0, maxLen) + '...' : val;
  }
  if (Array.isArray(val)) {
    return val.map((item) => _capStrings(item, maxLen, _depth + 1));
  }
  if (typeof val === 'object') {
    const capped = {};
    for (const [k, v] of Object.entries(val)) {
      capped[k] = _capStrings(v, maxLen, _depth + 1);
    }
    return capped;
  }
  return val;
}

// --- Batched write state ---
let _pendingBatch = [];
let _flushTimer = null;
let _flushing = false;
let _droppedCount = 0;
let _flushCount = 0;
const TRIM_EVERY_N_FLUSHES = 10;
const BATCH_FLUSH_SIZE = 50;
const BATCH_FLUSH_DELAY_MS = 2000;
const BATCH_MAX_PENDING = 200;

export async function _flushBatch() {
  if (_flushTimer !== null) {
    clearTimeout(_flushTimer);
    _flushTimer = null;
  }
  if (_flushing || _pendingBatch.length === 0) return;
  _flushing = true;
  const batch = _pendingBatch;
  _pendingBatch = [];
  if (_droppedCount > 0) {
    batch.unshift({ ts: Date.now(), event: 'diagnostics_entries_dropped', level: 'WARN', data: { count: _droppedCount } });
    _droppedCount = 0;
  }
  try {
    await store.batchAdd(batch);
    _flushCount++;
    if (_flushCount % TRIM_EVERY_N_FLUSHES === 0) {
      await store.trimToMax(MAX_ENTRIES);
    }
  } catch (flushErr) {
    console.warn('[ABD diagnostics] flush failed:', flushErr?.message);
    _pendingBatch.unshift(...batch);
    if (_pendingBatch.length > BATCH_MAX_PENDING) {
      _droppedCount += _pendingBatch.length - BATCH_MAX_PENDING;
      _pendingBatch.length = BATCH_MAX_PENDING;
    }
  }
  finally {
    _flushing = false;
  }
  if (_pendingBatch.length > 0) {
    _flushTimer = setTimeout(_flushBatch, BATCH_FLUSH_DELAY_MS);
  }
}

/**
 * Append a diagnostic entry to the ring buffer in session storage.
 * Respects the diagnosticLevel gate — entries below threshold are silently dropped.
 * Writes are batched: flushed when batch reaches 50 entries or after 2000ms idle.
 * @param {{ event: string, level?: string, data?: any }} entry
 */
export function logDiagnostic(entry) {
  const entryLevel = (entry.level || 'DEBUG').toUpperCase();
  const threshold = (config.diagnosticLevel || 'INFO').toUpperCase();
  if ((LEVELS[entryLevel] ?? 0) < (LEVELS[threshold] ?? 1)) return;

  if (_pendingBatch.length >= BATCH_MAX_PENDING) {
    _droppedCount++;
    return;
  }
  _pendingBatch.push({ ts: Date.now(), ..._capStrings(entry), level: entryLevel });
  if (_pendingBatch.length >= BATCH_FLUSH_SIZE) {
    _flushBatch();
  } else if (_flushTimer === null) {
    _flushTimer = setTimeout(_flushBatch, BATCH_FLUSH_DELAY_MS);
  }
}

/**
 * Retrieve all diagnostic entries from the ring buffer.
 * @returns {Promise<Array>}
 */
export async function getDiagnostics() {
  try {
    return await store.getAll();
  } catch { return []; }
}

/**
 * Clear all diagnostic entries, including any pending unflushed batch.
 */
export async function clearDiagnostics() {
  _pendingBatch = [];
  _droppedCount = 0;
  _flushCount = 0;
  if (_flushTimer !== null) {
    clearTimeout(_flushTimer);
    _flushTimer = null;
  }
  try { await store.clear(); } catch {}
}

/**
 * Run TTL sweep: delete entries older than config.diagTtlMs.
 * Called on chrome.runtime.onStartup (browser start).
 * @returns {Promise<number>} entries deleted
 */
export async function sweepExpiredEntries() {
  try {
    const cutoff = Date.now() - (config.diagTtlMs || 7 * 24 * 60 * 60 * 1000);
    return await store.deleteOlderThan(cutoff);
  } catch { return 0; }
}

/**
 * Inject a session boundary marker into the log.
 * Called on chrome.runtime.onStartup so exports can filter by session.
 */
export function injectSessionMarker() {
  const sessionId = crypto.randomUUID();
  logDiagnostic({ event: 'session_start', level: 'INFO', data: { sessionId } });
}
