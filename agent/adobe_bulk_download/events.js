// events.js — Event bus and UI formatter (ES module).
// Ported from adobe-bulk-download-v1.5.3.js lines 146-312.

/**
 * Format byte count as human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
  if (typeof bytes !== 'number' || !isFinite(bytes) || bytes <= 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1);
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Map internal error categories to human-readable strings for UI display.
 * @param {string} category
 * @returns {string}
 */
export function friendlyCategory(category) {
  const map = {
    auth_expired: 'Authentication expired',
    server_forbidden: 'Server forbidden (403)',
    rate_limit: 'Rate limited by server',
    responsetoolarge: 'File too large for server',
    response_too_large: 'File too large for server',
    file_too_large_for_data_url: 'File too large to process',
    network_error: 'Network error',
    network_timeout: 'Network timeout',
    server_error: 'Server error',
    file_system_error: 'File system error',
    empty_response: 'Empty response from server',
    user_stopped: 'Stopped by user',
    download_error: 'Download error',
    truncated_download: 'Download incomplete (truncated)',
    download_stalled: 'Download stalled',
    download_missing: 'Download lost (browser restart)',
    invalid_ai: 'Invalid AI file',
    manifest_failed: 'Could not retrieve file info',
    component_download_failed: 'Could not download converted file',
    presigned_url_failed: 'Could not get download link',
    unknown: 'Unknown error',
  };
  return map[category] || category || 'Unknown error';
}

/**
 * Unified event bus. Consumers register callbacks that receive every emitted entry.
 */
export const events = {
  _consumers: [],

  register(consumer) {
    if (!this._consumers.includes(consumer)) this._consumers.push(consumer);
  },

  unregister(consumer) {
    this._consumers = this._consumers.filter((c) => c !== consumer);
  },

  emit(eventName, data = {}) {
    const entry = { event: eventName, ...data, timestamp: new Date().toISOString() };
    for (const consumer of this._consumers) {
      try {
        consumer(entry);
      } catch (e) {
        console.error('[ABD events] Consumer error:', e);
      }
    }
    return entry;
  },
};

/**
 * Map event entries to human-readable {message, type} for the activity log.
 * Returns null for events that should not appear in the UI.
 *
 * @param {object} entry - Event entry from events.emit()
 * @param {object|null} config - Config object (needs max429Retries for rate_limit)
 * @returns {{message: string, type: string}|null}
 */
export function formatEventForUI(entry, config) {
  const e = entry;
  switch (e.event) {
    // Session
    case 'session_initialized':
    case 'scan_folder':
    case 'scan_pagination':
      return null;
    case 'scan_fallback_triggered':
      return { message: `Falling back to root scan (${e.reason === 'cloud_content_404' ? '/cloud-content not found' : '/cloud-content is empty'})`, type: 'warning' };
    case 'scan_region_cycle':
      return { message: `Scanning additional storage region${e.tryingRegion ? ': ' + e.tryingRegion : ''}`, type: 'info' };
    case 'scan_region_cycle_start':
      return { message: `Scanning ${e.regionsToTry} additional storage region${e.regionsToTry !== 1 ? 's' : ''}${e.filesAlreadyFound ? ` (${e.filesAlreadyFound} files found so far)` : ''}...`, type: 'info' };
    case 'scan_error':
      return { message: `Error scanning ${e.path}: ${e.error}`, type: 'error' };
    case 'scan_start':
      return null;
    case 'scan_complete':
      return { message: `Scan complete: ${e.totalFiles} files in ${e.totalFolders} folders`, type: 'info' };
    case 'scan_summary_line':
      return { message: e.message, type: 'info' };
    // Download orchestration
    case 'initializing':
      return null;
    case 'download_start':
      return { message: `Downloading ${e.pending} files (${e.concurrency} concurrent)\u2026`, type: 'info' };
    case 'retry_failed_start':
      return { message: `Retrying ${e.count} failed files\u2026`, type: 'info' };
    case 'resume_accepted':
      return { message: `Resumed \u2014 skipping ${e.skipped} already-downloaded files`, type: 'info' };
    case 'resume_declined':
      return { message: 'Starting fresh \u2014 cleared previous session data', type: 'info' };
    case 'download_complete':
      return { message: `Downloaded: ${e.downloadedFiles} | Failed: ${e.failedFiles} | ${formatBytes(e.downloadedBytes)} in ${e.elapsed}s`, type: 'info' };
    case 'download_complete_banner':
      return null;
    // File outcomes
    case 'file_success':
      return null;
    case 'file_fail':
      return { message: `\u2717 ${e.name}: ${e.error}`, type: 'error' };
    case 'file_retry_queued':
      return null;
    // HTTP-level
    case 'http_retry':
      return null;
    case 'non_retryable_error':
      return null;
    case 'rate_limit': {
      const maxRetries = config?.max429Retries ?? '?';
      return { message: `Rate limited (${e.throttle_count}/${maxRetries}). Waiting ${e.wait_seconds}s\u2026`, type: 'warning' };
    }
    // PSDC conversion
    case 'psdc_conversion_start':
      return null;
    case 'psdc_conversion_succeeded':
      return null;
    case 'psdc_conversion_retry':
      return null;
    case 'psdc_raw_fallback_start':
      return { message: `  PSD conversion failed, downloading raw PSDC: ${e.name}`, type: 'warning' };
    case 'psdc_raw_fallback_success':
      return null;
    case 'psdc_psd_fallback_attempt':
    case 'psdc_psd_fallback_success':
    case 'psdc_propagation_ready':
    case 'psdc_propagation_exhausted':
    case 'psdc_download_method':
      return null;
    case 'psdc_job_recovered':
    case 'psdc_job_recovered_via_temppath':
    case 'psdc_job_recovery_failed':
    case 'psdc_download_method_list_failed':
      return null;
    // AIC
    // AIC conversion
    case 'aic_conversion_start':
    case 'aic_conversion_succeeded':
    case 'aic_conversion_retry':
    case 'aic_conversion_polling':
    case 'aic_raw_fallback_success':
    case 'ai_validation_failed':
    case 'ai_validation_success':
    case 'aic_propagation_ready':
    case 'aic_propagation_exhausted':
    case 'aic_download_method':
    // Defensive: these events flow through logDiagnostic() only today,
    // but are listed here to suppress if ever routed through events.emit().
    case 'aic_job_id_invalid':
    case 'aic_poll_malformed_response':
    case 'aic_job_recovery_skipped':
    case 'aic_job_recovery_failed':
    case 'aic_predict_failed':
      return null;
    case 'aic_conversion_timeout':
      return { message: `  AIC conversion timed out: ${e.path}`, type: 'error' };
    case 'aic_raw_fallback_start':
      return { message: `  AI conversion failed, downloading raw AIC: ${e.name}`, type: 'warning' };
    // Firefly (ffgenimg/ffgenvid/ffgenaud)
    case 'ffgen_manifest_fetch':
    case 'ffgen_component_download':
    case 'ffgen_raw_fallback_success':
    case 'ffgenaud_presigned_fetch':
      return null;
    case 'ffgen_raw_fallback_start':
      return { message: `  Extraction failed, downloading raw file: ${e.name}`, type: 'warning' };
    case 'ffgenaud_presigned_failed':
      return { message: `  Could not get audio download link: ${e.name}`, type: 'warning' };
    // Fallback
    case 'fallback_attempt':
      return null;
    case 'fallback_success':
      return null; // Diagnostic only — both fallback events suppressed from UI
    // Size
    case 'size_warning':
      return null;
    // User controls
    case 'user_pause':
      return { message: 'Paused', type: 'info' };
    case 'user_resume':
      return { message: 'Resumed \u2014 continuing download', type: 'info' };
    case 'user_stop':
      console.log('[ABD] Stopped by user');
      return null;
    case 'free_limit_reached':
      return { message: `Free limit reached (${e.downloaded}/${e.limit} files). Upgrade for unlimited downloads.`, type: 'info' };
    case 'license_activated':
      return { message: 'License activated \u2014 unlimited downloads enabled', type: 'success' };
    case 'scan_failed':
      return { message: 'Scan failed: ' + e.error, type: 'error' };
    case 'config_change':
      return null;
    case 'progress_save_failed':
      return null;
    case 'progress_load_failed':
      return null;
    case 'file_save_error':
      return { message: `Save failed: ${e.save_name} — ${e.error}`, type: 'error' };
    case 'download_heartbeat':
      return null;
    case 'adaptive_delay_decrease':
      return null;
    case 'adaptive_delay_increase':
      return null;
    case 'stop_orphan_reconciliation':
      return null;
    case 'conversion_job_id_missing':
      return null;
    case 'psdc_poll_iteration':
      return null;
    // Size validation / stall detection (diagnostic-only — file_fail/file_retry carry the UI message)
    case 'download_truncated':
    case 'size_mismatch_shadow':
    case 'download_stalled':
    case 'download_zombie_cap':
    case 'expected_size_unavailable':
      return null;
    // block_download tier + on-wake reconciliation (diagnostic-only)
    case 'blockdownload_attempt':
    case 'blockdownload_unavailable':
    case 'download_reconciled':
      return null;
    case 'retry_no_failures':
      return { message: e.message, type: 'info' };
    case 'psdc_conversion_timeout':
      return { message: `  PSDC conversion timed out: ${e.path}`, type: 'error' };
    case 'eta_update':
      return null;
    case 'eta_invariant_violation':
      return null;
    case 'status_change':
      return null;
    // Phase 4A — SW lifecycle
    case 'scan_depth_limit':
      return { message: `Scan depth limit reached (${e.depth}): ${e.path}`, type: 'warning' };
    case 'sw_recovery':
      return null;
    case 'token_accepted':
      return null; // Handled by sidepanel badge, not activity log
    case 'token_invalid':
      return { message: `Token invalid (HTTP ${e.status ?? '?'}) — please re-authenticate`, type: 'error' };
    case 'token_validation_failed':
      return { message: `Token rejected: ${e.reason}`, type: 'error' };
    case 'resume_prompt_timeout':
      return { message: 'Resume prompt timed out — starting fresh', type: 'warning' };
    case 'file_retry':
      return null;
    case 'auth_expired':
      return { message: `Auth expired (HTTP ${e.http_status ?? '?'}) — please refresh the page`, type: 'error' };
    case 'network_timeout':
    case 'path_truncated':
      return null;
    // Token expiry
    case 'token_expiry_warning': {
      const mins = Math.ceil((e.remainingMs || 0) / 60000);
      return { message: `Token expiring in ${mins} minute${mins !== 1 ? 's' : ''} — re-authenticate soon`, type: 'warning' };
    }
    case 'token_expired':
      return { message: 'Token expired — please refresh the page to re-authenticate', type: 'error' };
    case 'resume_prompt_persisted':
      return { message: 'Resume prompt saved — open the side panel to respond', type: 'info' };
    case 'download_summary': {
      const groups = Object.entries(e.errorGroups || {})
        .map(([cat, g]) => `${friendlyCategory(cat)}: ${g.count}`)
        .join(', ');
      return { message: `Failed files breakdown: ${groups}`, type: 'error' };
    }
    case 'unhandled_error':
      return { message: `Internal error: ${e.error || e.message || 'unknown'}`, type: 'error' };
    case 'direct_url_fallback_to_blob':
    case 'capabilities_detected':
    case 'tier_fallback':
      return null;
    case 'create_object_url_failed':
      return null;
    case 'blob_revoke_failed':
      return null;
    case 'temp_dir_created':
    case 'temp_dir_skip_no_repo':
    case 'temp_dir_unexpected_status':
    case 'temp_dir_failed_nonfatal':
    case 'conversion_store_restore_failed':
    case 'conversion_job_save_failed':
    case 'conversion_job_delete_failed':
    case 'conversion_job_clear_failed':
      return null;
    case 'set_ui_options_failed':
      return null;
    case 'token_restore_failed':
      return null;
    case 'failed_list_restore_failed':
      return null;
    case 'send_response_failed':
      return null;
    case 'worker_status':
    case 'workers_init':
      return null;
    default:
      return null;
  }
}
