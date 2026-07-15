// downloads.js — Download pipeline, PSDC conversion, and file saving (ES module).
// Ported from adobe-bulk-download-v1.5.3.js lines 153, 802-1485.

import { fetchWithRetry, sleep, _classifyError } from './api.js';
import { events } from './events.js';
import { config } from './config.js';
import { state, saveProgress, loadProgress, waitForResume } from './state.js';
import { listFolder } from './scanner.js';
import { initializeETA, restoreState as restoreETA } from './eta.js';
import { getToken } from './token.js';
import { logDiagnostic } from './diagnostics.js';
import { isPaid } from './license.js';
import { trackEvent } from './analytics.js';

// --- Helpers ---

/** Validate and sanitize region string for URL interpolation. */
function _validateRegion(region) {
  const r = (region || '').toLowerCase();
  if (!/^[a-z0-9]{2,10}$/.test(r)) {
    throw new Error(`Invalid storage region: "${region}"`);
  }
  return r;
}

/** Strip characters illegal in Windows file names. (v1.5.3 line 153) */
function _sanitizeFileName(name) {
  let sanitized = name.replace(/[<>:"|?*\/]/g, '_').replace(/\\/g, '-');
  sanitized = sanitized.replace(/[\x00-\x1f]|\p{Cf}/gu, '');
  if (!sanitized) return 'unnamed_file';
  // Block Windows reserved device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
  const RESERVED = /^(CON|PRN|AUX|NUL|COM\d|LPT\d)(\.|$)/i;
  if (RESERVED.test(sanitized)) sanitized = '_' + sanitized;
  // Cap individual segments at 200 chars to leave room for directory prefix
  // within maxPathLength (250). saveFile() performs the final path-level check.
  if (sanitized.length > 200) sanitized = sanitized.slice(0, 200);
  return sanitized;
}

/** One-time AIC format notice flag, reset per downloadAll run. */

/** H5: Track active blob URLs for cleanup on SW termination. */
const _activeBlobUrls = new Set();

/** Phase 4D-3+7A: Conversion job store for SW restart recovery. */
const _conversionJobStore = new Map();   // Map<assetId, { jobId, tempPath, pollCount, startedAt }>
let _conversionJobStoreReady = null;     // Promise gate — initialized once per SW lifecycle
let _conversionClearEpoch = 0;           // Monotonic counter — invalidates in-flight reads after clear

/** Phase 7A: Per-repositoryId cache of temp directory asset IDs. */
const _tempDirCache = new Map(); // Map<repositoryId:region, tempDirAssetId>

/** Task 9: Dirty-flag persistence of free file count to chrome.storage.local. */
let _freeCountWriteInFlight = false;
let _freeCountDirty = false;
async function _persistFreeCount() {
  _freeCountDirty = true;
  if (_freeCountWriteInFlight) return;
  _freeCountWriteInFlight = true;
  try {
    while (_freeCountDirty) {
      _freeCountDirty = false;
      await chrome.storage.local.set({ [config.freeFilesUsedKey]: state._freeFilesUsed });
    }
  } catch (e) {
    _freeCountDirty = true;
    console.warn('[ABD] Free count persist failed:', e?.message);
    logDiagnostic({ event: 'free_count_persist_failed', level: 'WARN', data: { error: e?.message } });
  }
  _freeCountWriteInFlight = false;
}

// --- saveFile (NEW for extension — replaces File System Access API) ---

/**
 * Build sanitized download path from file metadata.
 * Shared by saveFile (blob path) and saveFileByUrl (direct URL path).
 * @param {object} file - File metadata (needs .path)
 * @param {string} saveName - Filename to save as
 * @returns {string} Sanitized relative path for chrome.downloads
 */
function _buildDownloadPath(file, saveName) {
  const sanitized = _sanitizeFileName(saveName || file.name || file.assetId || 'unnamed_file');

  // Prepend user-specified subfolder if configured
  const subfolder = config.downloadSubfolder
    ? _sanitizeFileName(config.downloadSubfolder)
    : '';

  // Build relative path: strip leading /cloud-content/, sanitize each segment
  const segments = file.path
    .replace(/^\/cloud-content\/?/, '')
    .split('/')
    .slice(0, -1) // drop the filename segment
    .map((s) => _sanitizeFileName(s))
    .map((s) => s.replace(/^\.+/, ''))
    .filter((s) => s);

  const prefix = subfolder
    ? (segments.length > 0 ? subfolder + '/' + segments.join('/') : subfolder)
    : (segments.length > 0 ? segments.join('/') : '');

  let filename = prefix
    ? prefix + '/' + sanitized
    : sanitized;

  if (filename.length > config.maxPathLength) {
    const originalLength = filename.length;
    const dotIdx = sanitized.lastIndexOf('.');
    const ext = dotIdx > 0 ? sanitized.slice(dotIdx) : '';
    const dirPrefix = prefix ? prefix + '/' : '';
    const maxNameLen = config.maxPathLength - dirPrefix.length - ext.length;
    const truncatedName = sanitized.slice(0, Math.max(10, maxNameLen)) + ext; // 10 = minimum chars for recognizable filename
    filename = dirPrefix + truncatedName;
    // Post-condition: if directory prefix alone pushes over the limit, hard-truncate
    if (filename.length > config.maxPathLength) {
      filename = filename.slice(0, config.maxPathLength);
    }
    events.emit('path_truncated', {
      originalLength,
      truncatedLength: filename.length,
      truncatedName,
      resolvedFilename: filename,
      path: file.path,
    });
  }

  logDiagnostic({ event: 'path_built', level: 'DEBUG', data: { input: file.path, output: filename, subfolder: config.downloadSubfolder || '' } });
  return filename;
}

/**
 * Save a blob to the user's downloads folder via chrome.downloads API.
 * Preserves directory structure from the file's cloud path.
 *
 * @param {Blob} blob - File content
 * @param {object} file - File metadata (needs .path)
 * @param {string} saveName - Filename to save as
 * @returns {Promise<number>} Download ID
 */
export async function saveFile(blob, file, saveName) {
  const filename = _buildDownloadPath(file, saveName);

  // Note: In MV3 service workers, URL.createObjectURL is not available.
  // Callers should use saveFileByUrl() instead for direct URL downloads.
  let url;
  let isBlobUrl = false;
  try {
    url = URL.createObjectURL(blob);
    isBlobUrl = true;
    _activeBlobUrls.add(url);
  } catch {
    // URL.createObjectURL unavailable in MV3 service worker — no blob download support
    logDiagnostic({ event: 'create_object_url_failed', level: 'WARN', data: { reason: 'SW context — use saveFileByUrl instead' } });
    const err2 = new Error('Blob download not available in service worker context — use saveFileByUrl for direct URL downloads');
    err2.nonRetryable = true;
    err2.details = { error_category: 'blob_unavailable' };
    throw err2;
  }

  return new Promise((resolve, reject) => {
    let settled = false;
    chrome.downloads.download(
      { url, filename, conflictAction: 'uniquify' },
      (downloadId) => {
        const revokeBlob = () => {
          if (isBlobUrl) { URL.revokeObjectURL(url); _activeBlobUrls.delete(url); }
        };
        if (chrome.runtime.lastError) {
          revokeBlob();
          if (!settled) { settled = true; reject(new Error(chrome.runtime.lastError.message)); }
          return;
        }

        let safetyTimer = null;

        const onChange = (delta) => {
          if (delta.id !== downloadId) return;
          if (settled) return;
          if (state.stopped) {
            if (safetyTimer) { clearTimeout(safetyTimer); safetyTimer = null; }
            chrome.downloads.onChanged.removeListener(onChange);
            revokeBlob();
            settled = true;
            reject(new Error('stopped'));
            return;
          }
          if (delta.state?.current === 'complete') {
            if (safetyTimer) { clearTimeout(safetyTimer); safetyTimer = null; }
            chrome.downloads.onChanged.removeListener(onChange);
            revokeBlob();
            settled = true;
            resolve(downloadId);
          } else if (delta.state?.current === 'interrupted') {
            if (safetyTimer) { clearTimeout(safetyTimer); safetyTimer = null; }
            chrome.downloads.onChanged.removeListener(onChange);
            revokeBlob();
            settled = true;
            const reason = delta.error?.current || 'unknown';
            const classified = _classifyInterruptReason(reason);
            const err = new Error(classified.message);
            err.nonRetryable = !classified.retryable;
            err.details = { error_category: classified.category, interrupt_reason: reason };
            reject(err);
          }
        };

        chrome.downloads.onChanged.addListener(onChange);

        // Safety timeout: revoke blob URL if chrome.downloads.onChanged never fires.
        // Uses setTimeout — safe because SW keepalive alarm is active during downloads
        // (Consumer 6 in background.js). In practice, onChanged fires well before 60s.
        safetyTimer = setTimeout(() => {
          safetyTimer = null;
          if (settled) return;
          chrome.downloads.onChanged.removeListener(onChange);
          revokeBlob();
          settled = true;
          reject(new Error('blob_url_timeout: download state change not received'));
        }, config.blobUrlTimeoutMs);
      },
    );
  });
}

/**
 * Query chrome.downloads.search for a download's byte counters and state.
 * NOTE: Chromium aliases fileSize to totalBytes (the server-declared length) — on a
 * truncated download both equal the declared size, NOT bytes on disk. bytesReceived
 * is the only field that reflects actual bytes written. All three are returned so
 * diagnostics payloads keep the full picture for forensics.
 * @param {number} downloadId
 * @returns {Promise<{ bytesReceived: number, totalBytes: number, fileSize: number, state: string|null, error: string|null, exists: boolean }>}
 */
async function _getDownloadStats(downloadId) {
  try {
    const results = await chrome.downloads.search({ id: downloadId });
    const item = results?.[0];
    if (item) {
      return {
        bytesReceived: item.bytesReceived || 0,
        totalBytes: item.totalBytes || 0,
        fileSize: item.fileSize || 0,
        state: item.state || null,
        error: item.error || null,
        exists: true,
      };
    }
  } catch (e) { logDiagnostic({ event: 'download_size_check_failed', level: 'WARN', data: { error: e?.message } }); }
  return { bytesReceived: 0, totalBytes: 0, fileSize: 0, state: null, error: null, exists: false };
}

/**
 * Clean up a truncated-but-"complete" download: removeFile (deletes the bytes on
 * disk — requires state complete) then erase (drops the history entry; invalidates
 * the id, so it must come second). removeFile failure is logged, not fatal —
 * uniquify means a retry then lands as "name (1).psd" instead of colliding.
 * @param {number} downloadId
 * @param {string} path - Cloud path for diagnostics
 */
async function _removeAndEraseDownload(downloadId, path) {
  try {
    await chrome.downloads.removeFile(downloadId);
  } catch (e) {
    logDiagnostic({ event: 'truncated_remove_failed', level: 'WARN', data: { downloadId, path, error: e?.message } });
  }
  try {
    await chrome.downloads.erase({ id: downloadId });
  } catch (e) {
    logDiagnostic({ event: 'truncated_erase_failed', level: 'WARN', data: { downloadId, path, error: e?.message } });
  }
}

// --- P2: In-flight download persistence + on-wake reconciliation ---

/** P2: In-flight downloadId map for SW-restart reconciliation. Map<downloadId, { path, expectedBytes, enforceSize, startedAt }> */
const _activeDownloadStore = new Map();

/** P2: Track an in-flight download — in-memory map + fire-and-forget write-through to session storage. */
function _saveActiveDownload(downloadId, entry) {
  _activeDownloadStore.set(downloadId, entry);
  const obj = Object.fromEntries(_activeDownloadStore);
  chrome.storage.session.set({ [config.activeDownloadsKey]: obj }).catch((e) => { logDiagnostic({ event: 'active_download_save_failed', level: 'WARN', data: { error: e?.message } }); });
}

/** P2: Remove a settled download from map + write-through. Idempotent — safe on every settle path. */
function _deleteActiveDownload(downloadId) {
  if (!_activeDownloadStore.delete(downloadId)) return;
  if (_activeDownloadStore.size === 0) {
    chrome.storage.session.remove(config.activeDownloadsKey).catch((e) => { logDiagnostic({ event: 'active_download_delete_failed', level: 'WARN', data: { error: e?.message } }); });
  } else {
    const obj = Object.fromEntries(_activeDownloadStore);
    chrome.storage.session.set({ [config.activeDownloadsKey]: obj }).catch((e) => { logDiagnostic({ event: 'active_download_delete_failed', level: 'WARN', data: { error: e?.message } }); });
  }
}

/** P2: Build a failed-files entry for a download classified during reconciliation (mirrors the processFile shape). */
function _reconcileFailureEntry(entry, error, errorCategory, actualBytes) {
  const path = entry.path || null;
  return {
    path,
    name: path ? path.split('/').pop() : null,
    error,
    errorCategory,
    interruptReason: null,
    size: entry.expectedBytes ?? null,
    retryCount: 0,
    category: null,
    timestamp: new Date().toISOString(),
    httpStatus: null,
    url: null,
    responseBody: '',
    responseHeaders: null,
    durationMs: null,
    stage: 'sw_wake_reconciliation',
    tierLog: [],
    retryHistory: [],
    expectedBytes: entry.expectedBytes ?? null,
    actualBytes: actualBytes ?? null,
  };
}

/**
 * P2: On-wake reconciliation sweep — called from background.js startup alongside the
 * existing SW recovery path. Downloads tracked in abd_active_downloads outlived a SW
 * death; chrome.downloads kept running without an onChanged listener or poller, so the
 * size validation in saveFileByUrl never ran. Re-run it retroactively:
 * - complete + bytesReceived >= expected (or no expected) → download_reconciled (INFO)
 * - complete + short + enforceSize → removeFile/erase + download_truncated + failed-files entry
 * - complete + short + shadow → size_mismatch_shadow (file kept, matching the live path)
 * - in_progress → orphan: cancel (auto-deletes partial; the file is still un-marked
 *   downloaded, so auto-resume re-downloads it cleanly instead of racing the orphan)
 * - interrupted / missing → failed-files entry with reason
 * The storage key is cleared up-front so a concurrently starting download's
 * write-through cannot resurrect swept ids.
 */
export async function reconcileActiveDownloads() {
  let entries;
  try {
    const data = await chrome.storage.session.get(config.activeDownloadsKey);
    entries = data?.[config.activeDownloadsKey];
  } catch (e) {
    logDiagnostic({ event: 'active_download_sweep_failed', level: 'WARN', data: { error: e?.message } });
    return;
  }
  if (!entries || typeof entries !== 'object' || Object.keys(entries).length === 0) return;
  await chrome.storage.session.remove(config.activeDownloadsKey).catch(() => {});

  const newFailures = [];
  for (const [idStr, rawEntry] of Object.entries(entries)) {
    const entry = rawEntry || {};
    const downloadId = Number(idStr);
    const stats = await _getDownloadStats(downloadId);
    const expected = entry.expectedBytes > 0 ? entry.expectedBytes : 0;

    if (stats.exists && stats.state === 'complete') {
      const actual = stats.bytesReceived;
      if (expected > 0 && actual < expected) {
        const payload = {
          path: entry.path, expected, actual,
          totalBytes: stats.totalBytes, url_host: null, tier: 'reconciliation',
        };
        if (entry.enforceSize) {
          await _removeAndEraseDownload(downloadId, entry.path);
          events.emit('download_truncated', payload);
          newFailures.push(_reconcileFailureEntry(entry, `Truncated download (found on service worker restart): got ${actual} of ${expected} bytes`, 'truncated_download', actual));
        } else {
          events.emit('size_mismatch_shadow', payload);
        }
      } else {
        events.emit('download_reconciled', { path: entry.path, downloadId, bytesReceived: actual, expected: expected || null, outcome: 'ok' });
      }
    } else if (stats.exists && stats.state === 'in_progress') {
      await Promise.resolve(chrome.downloads.cancel(downloadId)).catch(() => { /* already gone */ });
      events.emit('download_reconciled', { path: entry.path, downloadId, bytesReceived: stats.bytesReceived, expected: expected || null, outcome: 'orphan_cancelled' });
    } else {
      const reason = stats.exists ? (stats.error || 'interrupted') : 'missing from downloads history';
      newFailures.push(_reconcileFailureEntry(entry, `Download interrupted by service worker restart (${reason})`, stats.exists ? 'download_error' : 'download_missing', stats.bytesReceived || null));
    }
  }

  if (newFailures.length > 0) {
    // Merge into the persisted failed-files list (read-modify-write: in-memory state
    // is empty on a fresh SW, so pushing state.failedFilesList alone would clobber
    // prior-session entries). The recovery path's restore then re-reads the merged list.
    let persisted = [];
    try {
      const failedData = await chrome.storage.session.get(config.failedFilesKey);
      const raw = failedData?.[config.failedFilesKey];
      if (Array.isArray(raw)) persisted = raw;
    } catch { logDiagnostic({ event: 'failed_list_restore_failed', level: 'WARN' }); }
    const merged = persisted.concat(newFailures).slice(-500);
    state.failedFilesList = merged;
    await chrome.storage.session.set({ [config.failedFilesKey]: merged }).catch(() => {});
  }
}

/**
 * Download a file by passing a URL directly to chrome.downloads.download() with auth headers.
 * Chrome streams to disk — no blob in SW memory, no size limit.
 *
 * Completion is signalled by onChanged (primary) or the stall-detector poller (backstop).
 * The poller also provides progress-based stall detection (onChanged never carries
 * bytesReceived), a 2 h zombie cap, and SW keepalive for free — every chrome.* call
 * resets the 30 s idle timer.
 *
 * Post-complete size validation: Chrome reports "complete" even on a short read
 * (SERVER_CONTENT_LENGTH_MISMATCH without strong validators is treated as finished),
 * so when expectedBytes is known the actual bytesReceived is compared after completion.
 *
 * @param {string} downloadUrl - Direct URL to the file on Adobe CDN
 * @param {object} file - File metadata (needs .path)
 * @param {string} saveName - Filename to save as
 * @param {string} token - Bearer token for Authorization header
 * @param {object} [options]
 * @param {boolean} [options.omitAuth] - Skip domain validation + auth headers (presigned URLs)
 * @param {number} [options.expectedBytes] - Authoritative size; a "complete" download smaller than this is truncated
 * @param {boolean} [options.enforceSize=false] - true: delete truncated file + reject retryable; false: shadow mode (log size_mismatch_shadow, resolve as success)
 * @param {string} [options.tier] - Tier label for size-validation diagnostics payloads
 * @returns {Promise<{ downloadId: number, fileSize: number }>} fileSize = bytesReceived (actual bytes on disk)
 */
export async function saveFileByUrl(downloadUrl, file, saveName, token, options = {}) {
  if (!options.omitAuth) {
  if (!token) {
    const err = new Error('No authentication token available');
    err.nonRetryable = true;
    err.details = { error_category: 'auth_expired' };
    throw err;
  }
  // Validate URL domain to prevent token leakage to non-Adobe hosts
  try {
    const host = new URL(downloadUrl).hostname;
    if (!host.endsWith('.adobe.io') && !host.endsWith('.adobe.com')) {
      throw new Error(`Refusing to send token to non-Adobe domain: ${host}`);
    }
  } catch (urlErr) {
    if (urlErr.message.startsWith('Refusing')) throw urlErr;
    throw new Error(`Invalid download URL: ${downloadUrl}`);
  }
  }
  const { expectedBytes, enforceSize = false } = options;
  const filename = _buildDownloadPath(file, saveName);
  const urlHost = new URL(downloadUrl).hostname;

  logDiagnostic({ event: 'download_request', level: 'DEBUG', data: { filename, url: urlHost } });
  return new Promise((resolve, reject) => {
    let settled = false;
    chrome.downloads.download(
      {
        url: downloadUrl,
        filename,
        conflictAction: 'uniquify',
        ...(options.omitAuth ? {} : { headers: [
          { name: 'Authorization', value: `Bearer ${token}` },
          { name: 'X-Api-Key', value: config.apiKey },
        ] }),
      },
      (downloadId) => {
        if (chrome.runtime.lastError) {
          logDiagnostic({ event: 'download_api_error', level: 'WARN', data: { error: chrome.runtime.lastError.message, filename } });
          if (!settled) { settled = true; reject(new Error(chrome.runtime.lastError.message)); }
          return;
        }

        let pollTimer = null;
        const startedAt = Date.now();
        let lastBytesReceived = 0;
        let lastProgressAt = startedAt;

        // P2: persist the in-flight downloadId so an on-wake sweep can reconcile it
        // if the SW dies mid-download. Removed in cleanup() — every settle path
        // (complete, interrupted, stalled, zombie-cap, stopped, truncated) runs it.
        _saveActiveDownload(downloadId, {
          path: file.path,
          expectedBytes: expectedBytes ?? null,
          enforceSize,
          startedAt,
        });

        const cleanup = () => {
          if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
          chrome.downloads.onChanged.removeListener(onChange);
          _deleteActiveDownload(downloadId);
        };

        // Shared complete handler — reached from onChanged (primary) or the poller (backstop).
        const handleComplete = () => {
          if (settled) return;
          settled = true;
          cleanup();
          _getDownloadStats(downloadId).then((stats) => {
            const actual = stats.bytesReceived;
            // Fail only when smaller — never when equal or larger.
            if (expectedBytes > 0 && actual < expectedBytes) {
              const payload = {
                path: file.path, expected: expectedBytes, actual,
                totalBytes: stats.totalBytes, url_host: urlHost, tier: options.tier || null,
              };
              if (enforceSize) {
                _removeAndEraseDownload(downloadId, file.path).then(() => {
                  events.emit('download_truncated', payload);
                  const err = new Error(`Truncated download: got ${actual} of ${expectedBytes} bytes`);
                  err.details = { error_category: 'truncated_download', expected: expectedBytes, actual, url: downloadUrl };
                  reject(err);
                });
                return;
              }
              // Shadow mode (raw files, D4): log the mismatch, keep the file.
              events.emit('size_mismatch_shadow', payload);
            }
            resolve({ downloadId, fileSize: actual });
          });
        };

        const handleInterrupted = (reason) => {
          if (settled) return;
          settled = true;
          cleanup();
          const classified = _classifyInterruptReason(reason);
          const err = new Error(classified.message);
          err.nonRetryable = !classified.retryable;
          err.details = {
            error_category: classified.category,
            interrupt_reason: reason,
            url: downloadUrl,
          };
          reject(err);
        };

        // Cancel a stalled/zombie download and reject retryably. cancel() auto-deletes
        // the partial file (Chromium Cancel() → DeleteDownloadFile()) and is a silent
        // no-op on completed/missing downloads — no removeFile needed on this path.
        const cancelStalled = (event, stalledMs, bytesReceived) => {
          if (settled) return;
          settled = true;
          cleanup();
          Promise.resolve(chrome.downloads.cancel(downloadId)).catch(() => {});
          events.emit(event, { path: file.path, bytesReceived, stalledMs });
          const err = new Error(event === 'download_zombie_cap'
            ? `Download cancelled: exceeded ${Math.round(config.downloadAbsoluteCapMs / 60000)} min absolute cap`
            : `Download stalled: no progress for ${Math.round(stalledMs / 1000)}s`);
          err.details = { error_category: 'download_stalled', bytes_received: bytesReceived, url: downloadUrl };
          reject(err);
        };

        const onChange = (delta) => {
          if (delta.id !== downloadId) return;
          if (settled) return;
          if (state.stopped) {
            settled = true;
            cleanup();
            reject(new Error('stopped'));
            return;
          }
          if (delta.state?.current === 'complete') {
            handleComplete();
          } else if (delta.state?.current === 'interrupted') {
            handleInterrupted(delta.error?.current || 'unknown');
          }
        };

        chrome.downloads.onChanged.addListener(onChange);

        // Stall-detector poller: progress (bytesReceived growth), not elapsed time,
        // is the liveness criterion — a slow-but-alive download is never cancelled
        // before the absolute cap.
        pollTimer = setInterval(() => {
          if (settled) { cleanup(); return; }
          if (state.stopped) {
            settled = true;
            cleanup();
            reject(new Error('stopped'));
            return;
          }
          _getDownloadStats(downloadId).then((stats) => {
            if (settled) return;
            // Poll-observed terminal states settle via the same handlers (onChanged stays primary).
            if (stats.state === 'complete') { handleComplete(); return; }
            if (stats.state === 'interrupted') { handleInterrupted(stats.error || 'unknown'); return; }
            if (stats.bytesReceived > lastBytesReceived) {
              lastBytesReceived = stats.bytesReceived;
              lastProgressAt = Date.now();
            }
            const now = Date.now();
            if (now - startedAt >= config.downloadAbsoluteCapMs) {
              cancelStalled('download_zombie_cap', now - startedAt, stats.bytesReceived);
              return;
            }
            if (now - lastProgressAt >= config.downloadStallTimeoutMs) {
              // Re-check state once before cancelling — guards the race where the
              // download finished between the byte snapshot and the stall verdict.
              _getDownloadStats(downloadId).then((recheck) => {
                if (settled) return;
                if (recheck.state === 'complete') { handleComplete(); return; }
                if (recheck.state === 'interrupted') { handleInterrupted(recheck.error || 'unknown'); return; }
                cancelStalled('download_stalled', Date.now() - lastProgressAt, recheck.bytesReceived);
              });
            }
          });
        }, config.downloadPollIntervalMs);
      },
    );
  });
}

/** H5: Revoke and clean up all tracked blob URLs (e.g. on SW terminal status). */
export function cleanupBlobUrls() {
  for (const blobUrl of _activeBlobUrls) {
    try { URL.revokeObjectURL(blobUrl); } catch { logDiagnostic({ event: 'blob_revoke_failed', level: 'DEBUG' }); }
  }
  _activeBlobUrls.clear();
}

/** Fetch and parse the composite manifest for a Firefly-generated asset. */
async function _fetchManifest(file) {
  const region = _validateRegion(file.region || state.storageRegion);
  const url = `https://platform-cs-edge-${region}.adobe.io/composite/manifest/id/${file.assetId}`;
  const resp = await fetchWithRetry(url);
  if (!resp.ok) {
    const err = new Error(`Manifest fetch failed: HTTP ${resp.status}`);
    err.details = { error_category: 'manifest_failed', http_status: resp.status };
    throw err;
  }
  const manifest = await resp.json();
  for (const child of manifest.children || []) {
    for (const comp of child.components || []) {
      if (comp.rel === 'primary') {
        if (!comp.version) {
          const err = new Error('Manifest primary component missing version/revision');
          err.details = { error_category: 'manifest_failed' };
          throw err;
        }
        return { componentId: comp.id, revision: comp.version, type: comp.type };
      }
    }
  }
  const err = new Error('No primary component found in manifest');
  err.details = { error_category: 'manifest_failed' };
  throw err;
}

/** Fetch a presigned download URL for a Firefly audio component. */
async function _fetchPresignedUrl(file, componentId, revision) {
  const region = _validateRegion(file.region || state.storageRegion);
  const resource = JSON.stringify({
    component_id: componentId,
    revision: revision,
    reltype: 'http://ns.adobe.com/adobecloud/rel/component',
  });
  const url = `https://platform-cs-edge-${region}.adobe.io/composite/block/download/id/${file.assetId};version=0?resource=${encodeURIComponent(resource)}`;
  const resp = await fetchWithRetry(url, {
    headers: {
      directive: 'link-2023',
      'link-options': 'absolute-base,long-form-rel',
    },
  });
  if (!resp.ok) {
    const err = new Error(`Presigned URL fetch failed: HTTP ${resp.status}`);
    err.details = { error_category: 'presigned_url_failed', http_status: resp.status };
    throw err;
  }
  return resp.json();
}

/**
 * P1.9: Fetch the :block_download descriptor for an asset and return its presigned
 * blobstore URL. Request shape from the Adobe-Clawback source (Task 0c): plain GET,
 * no query params, no body — the Accept header is what makes the endpoint return a
 * JSON descriptor (top-level `{"href": <presigned URL>}`) instead of bytes. The href
 * is downloaded with NO auth headers (presigned), so only https is enforced — no
 * hostname allowlist, consistent with the Firefly presigned path (no token sent).
 *
 * Raw fetch, single attempt (not fetchWithRetry): this tier is best-effort — any
 * failure here must fall through to the next tier immediately, and fetchWithRetry's
 * 401/403 handling would flip state.status to 'error' as a side effect.
 *
 * @param {string} assetId - Asset ID (converted temp asset)
 * @param {string} region - Validated storage region
 * @param {string} token - Bearer token for the descriptor request
 * @returns {Promise<string>} Presigned https href
 */
async function _getBlockDownloadUrl(assetId, region, token) {
  const url = `https://platform-cs-edge-${region}.adobe.io/content/storage/id/${assetId}/:block_download`;
  const resp = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'x-api-key': config.apiKey,
      'Accept': 'application/vnd.adobecloud.download+json',
    },
  });
  if (!resp.ok) {
    const err = new Error(`block_download descriptor failed: HTTP ${resp.status}`);
    err.details = { error_category: 'blockdownload_failed', http_status: resp.status };
    throw err;
  }
  const body = await resp.json();
  const href = body?.href;
  if (!href || typeof href !== 'string') {
    const err = new Error('block_download descriptor missing href');
    err.details = { error_category: 'blockdownload_failed' };
    throw err;
  }
  if (new URL(href).protocol !== 'https:') {
    const err = new Error('block_download presigned href is not https');
    err.details = { error_category: 'blockdownload_failed' };
    throw err;
  }
  return href;
}

/**
 * Raw fallback shared by all ffgen categories.
 * Tries primary CDN then fallback CDN, resolves with true on success or false if
 * directUrlDownload is disabled.
 */
async function _ffgenRawFallback(file, t0, tierLog, errorMessage) {
  events.emit('ffgen_raw_fallback_start', {
    path: file.path, name: file.name, error: errorMessage,
  });
  if (!config.directUrlDownload) return false;

  const rawToken = getToken();
  const rawRegion = _validateRegion(file.region || state.storageRegion);
  const rawPrimaryUrl = `https://platform-cs-edge-${rawRegion}.adobe.io/content/storage/id/${file.assetId}`;
  tierLog.push({ tier: 'raw_fallback', method: 'direct_url_primary', result: 'pending' });
  try {
    // Raw original: file.size (repo:size) is exact — shadow mode (D4)
    const result = await saveFileByUrl(rawPrimaryUrl, file, file.name, rawToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_primary' });
    tierLog[tierLog.length - 1].result = 'ok';
    events.emit('ffgen_raw_fallback_success', { path: file.path, name: file.name, size: result.fileSize });
    file.downloaded = true;
    file.downloadedSize = result.fileSize;
    file.downloadTime = Date.now() - t0;
    state.downloadedFiles++;
    state.downloadedBytes += result.fileSize;
    state.sessionMetrics.consecutiveFailures = 0;
    events.emit('file_success', {
      path: file.path, size: file.size, downloaded_size: result.fileSize,
      duration_ms: Date.now() - t0, category: file.category, save_name: file.name,
      expected_size: file.size, download_method: 'ffgen_raw_fallback', tierLog,
    });
    return true;
  } catch (rawPrimaryErr) {
    tierLog[tierLog.length - 1].result = rawPrimaryErr.details?.error_category || 'error';
    if (state.stopped) throw rawPrimaryErr;
    if (rawPrimaryErr.details?.error_category === 'auth_expired') throw rawPrimaryErr;
    const fallbackUrl = `https://cc-api-storage.adobe.io/id/${file.assetId}`;
    tierLog.push({ tier: 'raw_fallback', method: 'direct_url_fallback', result: 'pending' });
    const freshToken = getToken();
    const result = await saveFileByUrl(fallbackUrl, file, file.name, freshToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_fallback' });
    tierLog[tierLog.length - 1].result = 'ok';
    events.emit('ffgen_raw_fallback_success', { path: file.path, name: file.name, size: result.fileSize });
    file.downloaded = true;
    file.downloadedSize = result.fileSize;
    file.downloadTime = Date.now() - t0;
    state.downloadedFiles++;
    state.downloadedBytes += result.fileSize;
    state.sessionMetrics.consecutiveFailures = 0;
    events.emit('file_success', {
      path: file.path, size: file.size, downloaded_size: result.fileSize,
      duration_ms: Date.now() - t0, category: file.category, save_name: file.name,
      expected_size: file.size, download_method: 'ffgen_raw_fallback_cdn', tierLog,
    });
    return true;
  }
}

/**
 * Classify Chrome download interrupt reasons into error categories.
 * Maps chrome.downloads InterruptReason strings to { category, retryable, message }.
 * @param {string} reason - Chrome's InterruptReason (e.g. 'SERVER_UNAUTHORIZED')
 * @returns {{ category: string, retryable: boolean, message: string }}
 */
function _classifyInterruptReason(reason) {
  if (!reason) return { category: 'unknown', retryable: true, message: 'Unknown download error' };
  const r = String(reason).toUpperCase();
  if (r === 'SERVER_UNAUTHORIZED') {
    return { category: 'auth_expired', retryable: false, message: `Auth failed: ${reason}` };
  }
  // Adobe CDN: 403 = origin/referrer rejection from service worker origin, not auth
  if (r === 'SERVER_FORBIDDEN') {
    return { category: 'server_forbidden', retryable: false, message: `Server forbidden: ${reason}` };
  }
  if (r.startsWith('NETWORK_')) {
    return { category: 'network_error', retryable: true, message: `Network error: ${reason}` };
  }
  if (r === 'FILE_TOO_LARGE' || r === 'FILE_ACCESS_DENIED' || r === 'FILE_NO_SPACE' || r === 'FILE_NAME_TOO_LONG') {
    return { category: 'file_system_error', retryable: false, message: `File system error: ${reason}` };
  }
  if (r === 'SERVER_FAILED' || r === 'SERVER_BAD_CONTENT') {
    return { category: 'server_error', retryable: true, message: `Server error: ${reason}` };
  }
  if (r === 'USER_CANCELED' || r === 'USER_SHUTDOWN') {
    return { category: 'user_stopped', retryable: false, message: 'Download cancelled' };
  }
  return { category: 'download_error', retryable: true, message: `Download interrupted: ${reason}` };
}

/**
 * D8: Detect "converted asset gone" errors from a download tier (HTTP 404 maps to
 * chrome.downloads SERVER_BAD_CONTENT). Used to invalidate the per-file conversion
 * cache in processFile so the next retry reconverts instead of re-downloading a
 * missing temp asset.
 * @param {Error|null|undefined} err
 * @returns {boolean}
 */
function _isConvertedAssetGone(err) {
  return err?.details?.interrupt_reason === 'SERVER_BAD_CONTENT' || err?.details?.http_status === 404;
}

// --- Phase 4D-3+7A: Conversion job store helpers ---

/** Phase 4D-3+7A: Lazy-init — reads abd_conversion_jobs from session storage into _conversionJobStore. */
async function _ensureConversionJobStoreReady() {
  if (_conversionJobStoreReady) return _conversionJobStoreReady;
  const epoch = _conversionClearEpoch;
  _conversionJobStoreReady = (async () => {
    try {
      const data = await chrome.storage.session.get(config.conversionJobsKey);
      if (_conversionClearEpoch !== epoch) return; // cleared while reading — discard stale data
      const stored = data?.[config.conversionJobsKey];
      if (stored && typeof stored === 'object') {
        for (const [k, v] of Object.entries(stored)) {
          if (v?.jobId && !/^[a-zA-Z0-9_\-]{1,128}$/.test(v.jobId)) continue;
          _conversionJobStore.set(k, v);
        }
      }
    } catch { logDiagnostic({ event: 'conversion_store_restore_failed', level: 'WARN' }); }
  })();
  return _conversionJobStoreReady;
}

/** Phase 4D-3: Update in-memory map + fire-and-forget write-through to session storage. */
function _saveConversionJob(assetId, jobState) {
  _conversionJobStore.set(assetId, jobState);
  const obj = Object.fromEntries(_conversionJobStore);
  chrome.storage.session.set({ [config.conversionJobsKey]: obj }).catch((e) => { logDiagnostic({ event: 'conversion_job_save_failed', level: 'WARN', data: { error: e?.message } }); });
}

/** Phase 4D-3: Remove job from map + write-through. */
function _deleteConversionJob(assetId) {
  _conversionJobStore.delete(assetId);
  if (_conversionJobStore.size === 0) {
    chrome.storage.session.remove(config.conversionJobsKey).catch((e) => { logDiagnostic({ event: 'conversion_job_delete_failed', level: 'WARN', data: { error: e?.message } }); });
  } else {
    const obj = Object.fromEntries(_conversionJobStore);
    chrome.storage.session.set({ [config.conversionJobsKey]: obj }).catch((e) => { logDiagnostic({ event: 'conversion_job_delete_failed', level: 'WARN', data: { error: e?.message } }); });
  }
}

/** Phase 4D-3+7A: Clear all conversion jobs — called by background.js Consumer 6 on terminal status. */
export function clearConversionJobs() {
  _conversionJobStore.clear();
  _conversionClearEpoch++;
  _conversionJobStoreReady = null;
  _tempDirCache.clear();
  chrome.storage.session.remove(config.conversionJobsKey).catch((e) => { logDiagnostic({ event: 'conversion_job_clear_failed', level: 'WARN', data: { error: e?.message } }); });
}

/** @deprecated Use clearConversionJobs instead. */
export const clearPsdcJobs = clearConversionJobs;

/**
 * Phase 7A: Create (or confirm) the /temp directory in a Creative Cloud repository.
 * Uses raw fetch (not fetchWithRetry): 409 Conflict is a success case (dir exists),
 * but fetchWithRetry rejects non-2xx responses.
 * @param {string} region - Validated storage region
 * @returns {Promise<string|null>} tempDirAssetId if returned by server, else null
 */
async function _createTempDir(region) {
  const repositoryId = state.repositoryId;
  if (!repositoryId) {
    logDiagnostic({ event: 'temp_dir_skip_no_repo', level: 'WARN' });
    return null;
  }
  const safeRegion = _validateRegion(region);
  const cacheKey = `${repositoryId}:${safeRegion}`;
  if (_tempDirCache.has(cacheKey)) {
    return _tempDirCache.get(cacheKey);
  }
  const url = `https://platform-cs-edge-${safeRegion}.adobe.io/content/storage/path/${encodeURIComponent(repositoryId)}/:create?path=temp&intermediates=true&respondWith=${encodeURIComponent('http://ns.adobe.com/adobecloud/rel/metadata/repository')}`;

  const token = getToken();
  if (!token) {
    const err = new Error('No token for temp dir creation');
    err.nonRetryable = true;
    err.details = { error_category: 'auth_expired' };
    throw err;
  }

  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'x-api-key': config.apiKey,
      'Content-Type': 'application/vnd.adobecloud.directory+json',
      'Content-Length': '0',
    },
  });

  if (resp.status === 401 || resp.status === 403) {
    const err = new Error(`AUTH_EXPIRED during temp dir creation (${resp.status})`);
    err.nonRetryable = true;
    err.details = { error_category: 'auth_expired', http_status: resp.status };
    throw err;
  }

  // 204 = created, 409 = already exists — both are success
  if (resp.status !== 204 && resp.status !== 409) {
    logDiagnostic({ event: 'temp_dir_unexpected_status', level: 'WARN', data: { status: resp.status } });
  }

  let tempDirAssetId = resp.headers.get('asset-id') || resp.headers.get('x-resource-id') || null;

  // On 409 (already exists), Adobe omits asset-id header but embeds it in a Link header:
  //   <https://...storage/id/urn:aaid:sc:VA7:xxxxx>; rel="http://ns.adobe.com/adobecloud/rel/id"
  if (!tempDirAssetId) {
    const linkHeader = resp.headers.get('link') || '';
    const idMatch = linkHeader.match(/\/content\/storage\/id\/(urn:aaid:sc:[^\s>?]+)/);
    if (idMatch) tempDirAssetId = decodeURIComponent(idMatch[1]);
  }

  if (tempDirAssetId) {
    _tempDirCache.set(cacheKey, tempDirAssetId);
  }
  logDiagnostic({ event: 'temp_dir_created', level: 'DEBUG', data: { repositoryId: repositoryId.slice(-12), status: resp.status, cached: !!tempDirAssetId } });

  return tempDirAssetId;
}

/**
 * Phase 7A: Submit a PSDC-to-PSD conversion job to Adobe's Photoshop API.
 * Extracted from downloadPSDC for reuse pattern — AIC will have a parallel function in 7B.
 * @param {object} file - File metadata (needs .assetId, .path)
 * @param {string} tempPath - Temp directory path for output
 * @returns {Promise<string>} jobId
 */
async function _submitPsdcConversion(file, tempPath) {
  let createResp;
  try {
    const body = JSON.stringify({
      image: { source: { creativeCloudFileId: file.assetId } },
      outputs: [{ destination: { creativeCloudPath: tempPath }, mediaType: 'image/vnd.adobe.photoshop' }],
    });
    createResp = await fetchWithRetry(`${config.photoshopApi}/create-composite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    });
  } catch (e) {
    if (e != null && typeof e === 'object') {
      e.stage = 'create_composite';
      if (!e.details) e.details = { error_category: 'conversion_failed' };
    }
    throw e;
  }

  // Extract job ID from Location header or response body
  let jobId;
  const loc = createResp.headers.get('Location');
  let bodyText = null;
  if (loc) {
    jobId = loc.split('/').pop();
  } else {
    bodyText = await createResp.text();
    let parsed;
    try { parsed = JSON.parse(bodyText); } catch { logDiagnostic({ event: 'psdc_job_parse_failed', level: 'WARN' }); parsed = null; }
    jobId = parsed?.jobId || parsed?._links?.self?.href?.split('/').pop();
  }
  if (jobId && !/^[a-zA-Z0-9_\-]{1,128}$/.test(jobId)) {
    logDiagnostic({ event: 'psdc_job_id_invalid', level: 'WARN', data: { jobId: String(jobId).slice(0, 50) } });
    jobId = null;
  }
  if (!jobId) {
    events.emit('conversion_job_id_missing', {
      path: file.path,
      response_status: createResp.status,
      response_body: (bodyText || '(no body)').slice(0, 500),
      location_header: loc,
    });
    const err = new Error('No job ID from create-composite');
    err.stage = 'create_composite';
    err.details = { error_category: 'conversion_failed' };
    throw err;
  }

  return jobId;
}

/**
 * Phase 7B: Submit an AIC-to-AI conversion job to Adobe's Sensei ML platform.
 * Parallel to _submitPsdcConversion but uses different API endpoint and payload format.
 * @param {object} file - File metadata (needs .assetId, .name, .modified, .path)
 * @param {string} tempDirAssetId - Asset ID of the /temp directory for output
 * @returns {Promise<string>} requestId
 */
async function _submitAicConversion(file, tempDirAssetId) {
  const sourceFileAssetId = file.assetId;
  const sourceId = (file.assetId || '').split(':').pop();
  const rawTs = new Date(file.modified).getTime();
  const timestamp = Number.isFinite(rawTs) ? rawTs : Date.now();
  const filename = (file.name || 'unnamed').replace(/\.[^.]+$/, '.ai').replace(/~/g, '_');

  let predictResp;
  try {
    const payload = JSON.stringify({
      'sensei:invocation_mode': 'asynchronous',
      'sensei:invocation_batch': false,
      'sensei:in_response': false,
      'sensei:engines': [{
        'sensei:execution_info': {
          'sensei:engine': config.senseiEngineId,
        },
        'sensei:inputs': {
          contentIn: {
            'dc:format': 'document/vnd.adobe.illustrator+dcxucf',
            'repo:id': sourceFileAssetId,
            'sensei:repoType': 'RAPI',
          },
        },
        'sensei:outputs': {
          contentOut: {
            'sensei:repoType': 'RAPI',
            'repo:id': tempDirAssetId,
            'dc:format': 'application/vnd.adobe.illustrator',
            'repo:resource': {
              reltype: 'http://ns.adobe.com/adobecloud/rel/create',
              path: `${sourceId}-${timestamp}/${filename}`,
            },
            'sensei:additionalProperties': {
              op_type: 'post',
              'x-composite-name': `${sourceId}-${timestamp}/${filename}`,
              'x-parent-urn': tempDirAssetId,
            },
          },
        },
        'sensei:params': {
          format: 'application/vnd.adobe.illustrator',
          inFormat: 'document/vnd.adobe.illustrator+dcx',
        },
      }],
    });

    const formData = new FormData();
    formData.append('contentAnalyzerRequests', payload);

    predictResp = await fetchWithRetry(config.senseiApi, {
      method: 'POST',
      body: formData,
    });
  } catch (e) {
    if (e != null && typeof e === 'object') {
      e.stage = 'sensei_predict';
      if (!e.details) e.details = { error_category: 'conversion_failed' };
    }
    logDiagnostic({ event: 'aic_predict_failed', level: 'WARN',
      data: { error: e?.message, http_status: e?.details?.http_status, engineId: config.senseiEngineId } });
    throw e;
  }

  // Extract request_id from response body or Location header
  let requestId;
  const loc = predictResp.headers.get('Location');
  let bodyText = null;
  if (loc) {
    requestId = loc.split('/').pop();
  }
  if (!requestId) {
    bodyText = await predictResp.text();
    let parsed;
    try { parsed = JSON.parse(bodyText); } catch { parsed = null; }
    requestId = parsed?.request_id;
  }
  if (requestId && !/^[a-zA-Z0-9_\-]{1,128}$/.test(requestId)) {
    logDiagnostic({ event: 'aic_job_id_invalid', level: 'WARN', data: { requestId: String(requestId).slice(0, 50) } });
    requestId = null;
  }
  if (!requestId) {
    events.emit('conversion_job_id_missing', {
      path: file.path,
      response_status: predictResp.status,
      response_body: (bodyText || '(no body)').slice(0, 500),
      location_header: loc,
    });
    const err = new Error('No request_id from Sensei predict');
    err.stage = 'sensei_predict';
    err.details = { error_category: 'conversion_failed' };
    throw err;
  }

  return requestId;
}

/**
 * Validate AI magic bytes ("%PDF") by fetching first 4 bytes via HTTP Range header.
 * Converted .ai files are PDF-based; this lightweight check confirms validity before full download.
 * @param {string} url - CDN URL to validate
 * @param {string} filePath - Original file path for event emission
 */
async function _validateAiMagicBytes(url, filePath) {
  const controller = new AbortController();
  let resp;
  try {
    resp = await fetch(url, {
      headers: {
        Accept: '*/*',
        Range: 'bytes=0-3',
        Authorization: `Bearer ${getToken()}`,
        'x-api-key': config.apiKey,
      },
      signal: controller.signal,
    });
  } catch (networkErr) {
    const err = new Error('AI validation network error');
    err.stage = 'validate_ai';
    throw err;
  }
  if (!resp.ok && resp.status !== 206) {
    const err = new Error(`AI validation HTTP ${resp.status}`);
    err.stage = 'validate_ai';
    throw err;
  }
  if (resp.status === 200) {
    const reader = resp.body.getReader();
    const { value } = await reader.read();
    controller.abort();
    if (!value || value.length < 4) {
      events.emit('ai_validation_failed', { path: filePath, header: '', size: value?.length || 0 });
      const err = new Error('AI validation failed: file too small');
      err.stage = 'validate_ai';
      err.details = { error_category: 'invalid_ai' };
      throw err;
    }
    const magic = String.fromCharCode(...value.slice(0, 4));
    if (magic !== '%PDF') {
      events.emit('ai_validation_failed', { path: filePath, header: magic, size: value.length });
      const err = new Error(`AI validation failed: header "${magic}"`);
      err.stage = 'validate_ai';
      err.details = { error_category: 'invalid_ai' };
      throw err;
    }
    events.emit('ai_validation_success', { path: filePath, size: value.length });
    return;
  }
  const buf = await resp.arrayBuffer();
  const bytes = new Uint8Array(buf);
  if (bytes.length < 4) {
    events.emit('ai_validation_failed', { path: filePath, header: '', size: bytes.length });
    const err = new Error('AI validation failed: file too small for magic bytes');
    err.stage = 'validate_ai';
    err.details = { error_category: 'invalid_ai' };
    throw err;
  }
  const magic = String.fromCharCode(...bytes.slice(0, 4));
  if (magic !== '%PDF') {
    events.emit('ai_validation_failed', { path: filePath, header: magic, size: buf.byteLength });
    const err = new Error(`AI validation failed: header "${magic}" (expected "%PDF")`);
    err.stage = 'validate_ai';
    err.details = { error_category: 'invalid_ai' };
    throw err;
  }
  events.emit('ai_validation_success', { path: filePath, size: buf.byteLength });
}

// --- downloadRegularFile (v1.5.3 lines 802-826) ---

export async function downloadRegularFile(file) {
  const region = _validateRegion(file.region || state.storageRegion);
  const url = `https://platform-cs-edge-${region}.adobe.io/content/storage/id/${file.assetId}`;
  try {
    const resp = await fetchWithRetry(url, { headers: { Accept: '*/*' } });
    return resp.blob();
  } catch (e) {
    if (e.message?.includes('AUTH_EXPIRED') || e.message?.includes('stopped') || e.message?.includes('Rate limited') || e.details?.error_category === 'auth_expired' || e.details?.error_category === 'rate_limit') {
      if (e != null && typeof e === 'object' && !e.stage) e.stage = 'primary_download';
      throw e;
    }
    const fallbackUrl = `https://cc-api-storage.adobe.io/id/${file.assetId}`;
    events.emit('fallback_attempt', {
      path: file.path,
      primary_url: url,
      fallback_url: fallbackUrl,
      primary_error: e.message,
      primary_error_category: e.details?.error_category || null,
    });
    const fbResp = await fetchWithRetry(fallbackUrl, {
      headers: { Accept: '*/*' },
    });
    events.emit('fallback_success', {
      path: file.path,
      fallback_url: fallbackUrl,
    });
    return fbResp.blob();
  }
}

// --- downloadPSDC (v1.5.3 lines 828-1092) ---

export async function downloadPSDC(file) {
  events.emit('psdc_conversion_start', {
    path: file.path,
    name: file.name,
    assetId: file.assetId,
  });
  const psdName = file.name.replace(/\.psdc$/i, '.psd').replace(/~/g, '_');
  const rawTs = new Date(file.modified).getTime();
  const ts = Number.isFinite(rawTs) ? rawTs : Date.now();
  const shortId = (file.assetId || '').split(':').pop();
  const tempPath = `temp/${shortId}-${ts}/${psdName}`;

  let outputPath;

  // --- Phase 4D-3: Recovery probe ---
  await _ensureConversionJobStoreReady();
  const priorJob = _conversionJobStore.get(file.assetId);

  // Phase 4D-3: Validate recovered job before attempting probes
  if (priorJob && priorJob.type && priorJob.type !== 'psdc') {
    _deleteConversionJob(file.assetId);
    events.emit('psdc_job_recovery_failed', { path: file.path, reason: 'type_mismatch' });
  } else if (priorJob && (!priorJob.jobId || typeof priorJob.jobId !== 'string')) {
    _deleteConversionJob(file.assetId);
    events.emit('psdc_job_recovery_failed', { path: file.path, reason: 'invalid recovered job data' });
  } else if (priorJob) {
    // Probe 1: Poll recovered jobId
    // Uses raw fetch (not fetchWithRetry) intentionally — recovery probe
    // should not consume retry budget or emit auth_expired status changes.
    const currentToken = getToken();
    try {
      if (!currentToken) throw new Error('No valid token for recovery probe');
      const statusResp = await fetch(`${config.photoshopApi}/status/${priorJob.jobId}`, {
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'x-api-key': config.apiKey,
        },
      });
      if (statusResp.ok) {
        const sd = await statusResp.json();
        if (sd.status === 'succeeded') {
          const out = sd.output || (sd.outputs && sd.outputs[0]);
          if (out) outputPath = out.creativeCloudPath || out.path || null;
          _deleteConversionJob(file.assetId);
          if (outputPath) {
            events.emit('psdc_job_recovered', { jobId: priorJob.jobId, status: 'succeeded', path: file.path });
          } else {
            events.emit('psdc_job_recovered', { jobId: priorJob.jobId, status: 'succeeded_no_output', path: file.path });
            // outputPath is undefined — will fall to Probe 2 for tempPath listing
          }
        } else if (sd.status === 'running' || sd.status === 'pending') {
          // Abbreviated poll loop capped at conversionJobRecoveryPollMs
          const recoveryDeadline = Date.now() + config.conversionJobRecoveryPollMs;
          let recoveredStatus = sd.status;
          while (recoveredStatus !== 'succeeded' && recoveredStatus !== 'failed' && Date.now() < recoveryDeadline) {
            await sleep(config.psdcPollDelay);
            if (state.stopped) { _deleteConversionJob(file.assetId); throw new Error('Download stopped by user'); }
            const loopToken = getToken();
            if (!loopToken) { _deleteConversionJob(file.assetId); break; }
            const pr = await fetch(`${config.photoshopApi}/status/${priorJob.jobId}`, {
              headers: {
                'Authorization': `Bearer ${loopToken}`,
                'x-api-key': config.apiKey,
              },
            });
            if (!pr.ok) break;
            const pd = await pr.json();
            recoveredStatus = pd.status;
            if (recoveredStatus === 'succeeded') {
              const out2 = pd.output || (pd.outputs && pd.outputs[0]);
              if (out2) outputPath = out2.creativeCloudPath || out2.path || null;
              _deleteConversionJob(file.assetId);
              events.emit('psdc_job_recovered', { jobId: priorJob.jobId, status: 'succeeded', path: file.path });
            }
          }
          // If still not succeeded after deadline/break, clean up job before Probe 2
          if (recoveredStatus !== 'succeeded') {
            _deleteConversionJob(file.assetId);
          }
        }
        // If status is 'failed' or unrecognized, fall to Probe 2
      }
      // If !statusResp.ok (404 etc), fall to Probe 2
    } catch (probeErr) {
      if (probeErr.message?.includes('stopped')) throw probeErr;
      // Network/parse error — fall to Probe 2
    }

    // Probe 2: tempPath directory listing (only if Probe 1 didn't succeed)
    if (!outputPath) {
      // Validate tempPath before attempting Probe 2
      if (typeof priorJob.tempPath !== 'string' || !priorJob.tempPath.startsWith('temp/') || priorJob.tempPath.length <= 5 ||
          priorJob.tempPath.split('/').some(seg => seg === '..' || seg === '.')) {
        _deleteConversionJob(file.assetId);
        events.emit('psdc_job_recovery_failed', { path: file.path, jobId: priorJob.jobId, reason: 'invalid tempPath' });
      } else {
      try {
        const tempDir = '/' + priorJob.tempPath.split('/').slice(0, -1).join('/');
        const region = _validateRegion(file.region || state.storageRegion);
        const tempContents = await listFolder(tempDir, region);
        const convertedFile = tempContents.find((c) => c.name === psdName);
        if (convertedFile) {
          events.emit('psdc_job_recovered_via_temppath', { path: file.path, tempDir });
          _deleteConversionJob(file.assetId);
          return {
            convertedAssetId: convertedFile.assetId,
            convertedSize: convertedFile.size || null,
            dlPath: priorJob.tempPath.replace(/^\//, ''),
            region: _validateRegion(file.region || state.storageRegion),
          };
        }
      } catch (probe2Err) {
        if (probe2Err.message?.includes('stopped')) throw probe2Err;
        const cat = probe2Err.details?.error_category;
        if (cat === 'auth_expired' || cat === 'rate_limit') throw probe2Err;
        // Probe 2 failed — fall through to normal path
      }
      _deleteConversionJob(file.assetId);
      events.emit('psdc_job_recovery_failed', { path: file.path, jobId: priorJob.jobId });
      } // end validTempPath else
    }
  }
  // --- End Phase 4D-3: Recovery probe ---

  // Phase 7A: Create temp directory (shared infra for PSDC and AIC conversions)
  // Non-fatal for PSDC: existing pipeline works without it. Required for AIC (7B).
  if (!outputPath) {
    try {
      const region = _validateRegion(file.region || state.storageRegion);
      await _createTempDir(region);
    } catch (tempDirErr) {
      if (tempDirErr.details?.error_category === 'auth_expired') throw tempDirErr;
      if (tempDirErr.message?.includes('stopped')) throw tempDirErr;
      logDiagnostic({ event: 'temp_dir_failed_nonfatal', level: 'WARN', data: { error: tempDirErr.message, path: file.path } });
    }
  }

  // Retry loop for conversion (Step 1 + Step 2)
  let lastConversionError;
  if (!outputPath) for (let convAttempt = 0; convAttempt <= config.maxConversionRetries; convAttempt++) {
    try {
      // Step 1: Submit conversion job (extracted in Phase 7A)
      const jobId = await _submitPsdcConversion(file, tempPath);

      // Phase 4D-3: Persist in-flight job for SW restart recovery
      _saveConversionJob(file.assetId, { jobId, tempPath, pollCount: 0, startedAt: Date.now(), type: 'psdc' });

      // Step 2: Poll for completion
      const conversionStartTime = Date.now();
      try {
        let status = 'running',
          polls = 0;
        while (status !== 'succeeded' && status !== 'failed' && polls < config.maxPsdcPolls) {
          await sleep(polls < 5 ? config.psdcPollInitialDelay : config.psdcPollDelay);
          // Stop guard after poll sleep
          if (state.stopped) { _deleteConversionJob(file.assetId); throw new Error('Download stopped by user'); }
          polls++;
          // Phase 4D-3: Update persisted poll count
          _saveConversionJob(file.assetId, { jobId, tempPath, pollCount: polls, startedAt: _conversionJobStore.get(file.assetId)?.startedAt || Date.now(), type: 'psdc' });
          const sr = await fetchWithRetry(`${config.photoshopApi}/status/${jobId}`);
          const sd = await sr.json();
          status = sd.status;
          events.emit('psdc_poll_iteration', {
            path: file.path,
            jobId,
            poll_count: polls,
            status,
            elapsed_ms: Date.now() - conversionStartTime,
          });
          if (status === 'succeeded') {
            const out = sd.output || (sd.outputs && sd.outputs[0]);
            if (out) outputPath = out.creativeCloudPath || out.path || null;
          }
          if (status === 'failed') throw new Error(`PSD conversion failed: ${JSON.stringify(sd.errors || sd)}`);
        }
        if (status !== 'succeeded') {
          events.emit('psdc_conversion_timeout', {
            path: file.path,
            jobId,
            polls,
            elapsed_ms: Date.now() - conversionStartTime,
          });
          throw new Error('PSD conversion timed out');
        }
      } catch (e) {
        if (e != null && typeof e === 'object') {
          if (!e.stage) e.stage = 'poll_status';
          if (!e.details) e.details = { error_category: 'conversion_failed' };
        }
        throw e;
      }

      // Success - emit event and exit retry loop
      lastConversionError = undefined;  // Clear stale error from prior failed attempts
      _deleteConversionJob(file.assetId);
      events.emit('psdc_conversion_succeeded', {
        name: file.name,
        path: file.path,
        jobId,
        outputPath,
        attempt: convAttempt + 1,
      });
      break;

    } catch (convErr) {
      lastConversionError = convErr;
      if (convAttempt < config.maxConversionRetries) {
        events.emit('psdc_conversion_retry', {
          path: file.path,
          attempt: convAttempt + 1,
          max_attempts: config.maxConversionRetries + 1,
          error: convErr.message,
          stage: convErr.stage,
        });
        if (state.stopped) { _deleteConversionJob(file.assetId); throw convErr; }
        await sleep(config.conversionRetryDelay);
        // Stop guard after conversion retry sleep
        if (state.stopped) { _deleteConversionJob(file.assetId); throw convErr; }
      } else {
        // Final attempt exhausted — clean up persisted job
        _deleteConversionJob(file.assetId);
      }
    }
  }

  // If conversion failed after all retries, throw the last error
  if (!outputPath) {
    if (lastConversionError) throw lastConversionError;
    // Conversion succeeded but API didn't return output path
    // Fall through to Step 3: temp directory listing will find it
  }

  // Step 3: Download the converted PSD (with smart retry for file propagation)
  try {
    const region = _validateRegion(file.region || state.storageRegion);
    const dlPath = (outputPath || tempPath).replace(/^\//, '');

    // Try ID-based download first (no size limit) with smart retry
    const tempDir = `/${dlPath.split('/').slice(0, -1).join('/')}`;
    let convertedFile = null;
    const maxPropagationAttempts = file.size >= config.largePropagationThreshold
      ? config.largePropagationAttempts : config.maxPropagationAttempts;

    // Smart retry loop for file propagation
    for (let attempt = 0; attempt < maxPropagationAttempts; attempt++) {
      try {
        const tempContents = await listFolder(tempDir, region);
        convertedFile = tempContents.find((c) => c.name === psdName);

        if (convertedFile) {
          if (attempt > 0) {
            events.emit('psdc_propagation_ready', {
              asset_id: file.assetId,
              wait_attempt: attempt + 1,
              total_wait_ms: attempt * config.propagationDelay,
            });
          }
          break;
        }

        if (attempt < maxPropagationAttempts - 1) {
          await sleep(config.propagationDelay);
          // Stop guard after propagation sleep
          if (state.stopped) throw new Error('Download stopped by user');
        }
      } catch (listErr) {
        if (listErr.message?.includes('stopped')) throw listErr;
        if (attempt === 0) {
          events.emit('psdc_download_method_list_failed', {
            path: file.path,
            error: listErr.message,
          });
          convertedFile = null;
        }
        break;
      }
    }

    if (!convertedFile) {
      events.emit('psdc_propagation_exhausted', {
        asset_id: file.assetId,
        attempts: maxPropagationAttempts,
        total_wait_ms: (maxPropagationAttempts - 1) * config.propagationDelay,
      });
    }

    // convertedSize: repo:size from the directory entry — the authoritative byte count
    // for the converted PSD, used as expectedBytes for post-download size validation.
    return { convertedAssetId: convertedFile?.assetId || null, convertedSize: convertedFile?.size || null, dlPath, region };
  } catch (e) {
    if (e != null && typeof e === 'object' && !e.stage) e.stage = 'download_psd';
    throw e;
  }
}

// --- convertAIC (Phase 7B) ---

export async function convertAIC(file) {
  events.emit('aic_conversion_start', {
    path: file.path,
    name: file.name,
    assetId: file.assetId,
  });
  const aiName = (file.name || 'unnamed').replace(/\.[^.]+$/, '.ai');
  const sourceId = (file.assetId || '').split(':').pop();
  const rawTs = new Date(file.modified).getTime();
  const ts = Number.isFinite(rawTs) ? rawTs : Date.now();

  let convertedAssetId = null;

  // Phase 7B: Temp dir is FATAL for AIC (Sensei payload requires tempDirAssetId)
  const region = _validateRegion(file.region || state.storageRegion);
  let tempDirAssetId;
  try {
    tempDirAssetId = await _createTempDir(region);
  } catch (tempDirErr) {
    if (tempDirErr.details?.error_category === 'auth_expired') throw tempDirErr;
    if (tempDirErr.message?.includes('stopped')) throw tempDirErr;
    const err = new Error('Temp dir creation failed (required for AIC conversion)');
    err.stage = 'temp_dir';
    err.details = { error_category: 'conversion_failed' };
    throw err;
  }
  if (!tempDirAssetId) {
    const err = new Error('No temp dir asset ID available (required for AIC conversion)');
    err.stage = 'temp_dir';
    err.details = { error_category: 'conversion_failed' };
    throw err;
  }

  // --- Recovery probe ---
  await _ensureConversionJobStoreReady();
  const priorJob = _conversionJobStore.get(file.assetId);

  if (priorJob && priorJob.type !== 'aic') {
    // Wrong type — don't attempt recovery
    _deleteConversionJob(file.assetId);
    logDiagnostic({ event: 'aic_job_recovery_skipped', level: 'DEBUG', data: { path: file.path, reason: 'type_mismatch', type: priorJob.type } });
  } else if (priorJob && (!priorJob.jobId || typeof priorJob.jobId !== 'string')) {
    _deleteConversionJob(file.assetId);
    logDiagnostic({ event: 'aic_job_recovery_failed', level: 'WARN', data: { path: file.path, reason: 'invalid_job_id' } });
  } else if (priorJob) {
    // Probe: Poll recovered requestId via Sensei status endpoint
    const currentToken = getToken();
    try {
      if (!currentToken) throw new Error('No valid token for recovery probe');
      const statusResp = await fetch(`${config.senseiStatusApi}/${priorJob.jobId}`, {
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'x-api-key': config.apiKey,
        },
      });
      if (statusResp.ok) {
        const sd = statusResp.status !== 202 ? await statusResp.json() : null;
        const invocation = sd?.statuses?.[0]?.invocations?.[0];
        const invStatus = invocation?.status;
        if (invStatus === '200') {
          convertedAssetId = invocation?.['sensei:outputs']?.contentOut?.['repo:id'] || null;
          _deleteConversionJob(file.assetId);
          events.emit('aic_conversion_succeeded', { name: file.name, path: file.path, jobId: priorJob.jobId, recovered: true });
        } else {
          // Abbreviated poll loop capped at conversionJobRecoveryPollMs
          const recoveryDeadline = Date.now() + config.conversionJobRecoveryPollMs;
          let recovered = false;
          let malformedCount = 0;
          while (!recovered && Date.now() < recoveryDeadline) {
            await sleep(config.aicPollDelay);
            if (state.stopped) { _deleteConversionJob(file.assetId); throw new Error('Download stopped by user'); }
            const loopToken = getToken();
            if (!loopToken) { _deleteConversionJob(file.assetId); break; }
            const pr = await fetch(`${config.senseiStatusApi}/${priorJob.jobId}`, {
              headers: {
                'Authorization': `Bearer ${loopToken}`,
                'x-api-key': config.apiKey,
              },
            });
            if (!pr.ok) break;
            if (pr.status === 202) continue; // still pending, empty body
            const pd = await pr.json();
            if (!pd?.statuses || !Array.isArray(pd.statuses) || pd.statuses.length === 0) {
              malformedCount++;
              logDiagnostic({ event: 'aic_poll_malformed_response', level: 'WARN',
                data: { jobId: priorJob.jobId, context: 'recovery_probe', malformedCount, keys: Object.keys(pd || {}).join(',') } });
              if (malformedCount >= 3) break;
              continue;
            }
            const inv = pd?.statuses?.[0]?.invocations?.[0];
            if (inv?.status === '200') {
              convertedAssetId = inv?.['sensei:outputs']?.contentOut?.['repo:id'] || null;
              _deleteConversionJob(file.assetId);
              events.emit('aic_conversion_succeeded', { name: file.name, path: file.path, jobId: priorJob.jobId, recovered: true });
              recovered = true;
            }
          }
          if (!recovered) {
            _deleteConversionJob(file.assetId);
            logDiagnostic({ event: 'aic_job_recovery_failed', level: 'WARN', data: { path: file.path, reason: 'recovery_poll_timeout', jobId: priorJob.jobId } });
          }
        }
      }
    } catch (probeErr) {
      if (probeErr.message?.includes('stopped')) throw probeErr;
      _deleteConversionJob(file.assetId);
      logDiagnostic({ event: 'aic_job_recovery_failed', level: 'WARN', data: { path: file.path, reason: probeErr.message, jobId: priorJob.jobId } });
    }
  }
  // --- End recovery probe ---

  // Pre-check: see if a prior conversion already produced the AI file in temp
  if (!convertedAssetId) {
    const dlPath = `temp/${sourceId}-${ts}/${aiName}`;
    const tempDir = `/${dlPath.split('/').slice(0, -1).join('/')}`;
    try {
      const tempContents = await listFolder(tempDir, region);
      const existing = tempContents.find((c) => c.name === aiName);
      if (existing && existing.assetId) {
        convertedAssetId = existing.assetId;
        logDiagnostic({ event: 'aic_existing_conversion_found', level: 'INFO',
          data: { path: file.path, assetId: existing.assetId, dlPath } });
        events.emit('aic_conversion_succeeded', { name: file.name, path: file.path, recovered: true, preExisting: true });
      }
    } catch {
      // Temp dir doesn't exist or listing failed — proceed to Sensei conversion
    }
  }

  // Retry loop for conversion
  let lastConversionError;
  if (!convertedAssetId) for (let convAttempt = 0; convAttempt <= config.maxConversionRetries; convAttempt++) {
    try {
      // Step 1: Submit conversion job
      const jobId = await _submitAicConversion(file, tempDirAssetId);

      // Persist in-flight job for SW restart recovery
      _saveConversionJob(file.assetId, { jobId, tempPath: `temp/${sourceId}-${ts}/${aiName}`, pollCount: 0, startedAt: Date.now(), type: 'aic' });

      // Step 2: Poll for completion
      const conversionStartTime = Date.now();
      try {
        let polls = 0;
        let completed = false;
        while (!completed && polls < config.maxAicPolls) {
          await sleep(polls < 3 ? config.aicPollInitialDelay : config.aicPollDelay);
          if (state.stopped) { _deleteConversionJob(file.assetId); throw new Error('Download stopped by user'); }
          polls++;
          _saveConversionJob(file.assetId, { jobId, tempPath: `temp/${sourceId}-${ts}/${aiName}`, pollCount: polls, startedAt: _conversionJobStore.get(file.assetId)?.startedAt || Date.now(), type: 'aic' });
          const sr = await fetchWithRetry(`${config.senseiStatusApi}/${jobId}`);
          if (sr.status === 202) continue; // still pending, empty body
          const sd = await sr.json();
          if (!sd?.statuses || !Array.isArray(sd.statuses) || sd.statuses.length === 0) {
            logDiagnostic({ event: 'aic_poll_malformed_response', level: 'WARN',
              data: { jobId, poll_count: polls, keys: Object.keys(sd || {}).join(',') } });
            if (polls >= 3) throw new Error('AIC conversion polling: malformed status response');
            continue;
          }
          const invocation = sd?.statuses?.[0]?.invocations?.[0];
          const invStatus = invocation?.status;
          events.emit('aic_conversion_polling', {
            path: file.path,
            jobId,
            poll_count: polls,
            status: invStatus,
            elapsed_ms: Date.now() - conversionStartTime,
          });
          if (invStatus === '200') {
            convertedAssetId = invocation?.['sensei:outputs']?.contentOut?.['repo:id'] || null;
            completed = true;
          } else if (invStatus && invStatus !== '202' && invStatus !== '102') {
            // Explicit failure status
            throw new Error(`AIC conversion failed: status ${invStatus}`);
          }
          // else: still pending (202/102/null) — continue polling
        }
        if (!completed) {
          events.emit('aic_conversion_timeout', {
            path: file.path,
            jobId,
            polls,
            elapsed_ms: Date.now() - conversionStartTime,
          });
          throw new Error('AIC conversion timed out');
        }
      } catch (e) {
        if (e != null && typeof e === 'object') {
          if (!e.stage) e.stage = 'poll_status';
          if (!e.details) e.details = { error_category: 'conversion_failed' };
        }
        throw e;
      }

      // Success — emit event and exit retry loop
      lastConversionError = undefined;
      _deleteConversionJob(file.assetId);
      events.emit('aic_conversion_succeeded', {
        name: file.name,
        path: file.path,
        jobId,
        convertedAssetId,
        attempt: convAttempt + 1,
      });
      break;

    } catch (convErr) {
      lastConversionError = convErr;
      if (convAttempt < config.maxConversionRetries) {
        events.emit('aic_conversion_retry', {
          path: file.path,
          attempt: convAttempt + 1,
          max_attempts: config.maxConversionRetries + 1,
          error: convErr.message,
          stage: convErr.stage,
        });
        if (state.stopped) { _deleteConversionJob(file.assetId); throw convErr; }
        await sleep(config.conversionRetryDelay);
        if (state.stopped) { _deleteConversionJob(file.assetId); throw convErr; }
      } else {
        _deleteConversionJob(file.assetId);
      }
    }
  }

  // If conversion failed after all retries, throw the last error
  if (!convertedAssetId && lastConversionError) throw lastConversionError;

  // Step 3: Propagation retry — find converted file in temp directory
  try {
    const dlPath = `temp/${sourceId}-${ts}/${aiName}`;
    const tempDir = `/${dlPath.split('/').slice(0, -1).join('/')}`;
    let convertedFile = null;
    const maxPropagationAttempts = file.size >= config.largePropagationThreshold
      ? config.largePropagationAttempts : config.maxPropagationAttempts;

    for (let attempt = 0; attempt < maxPropagationAttempts; attempt++) {
      try {
        const tempContents = await listFolder(tempDir, region);
        convertedFile = tempContents.find((c) => c.name === aiName);
        if (convertedFile) {
          if (attempt > 0) {
            events.emit('aic_propagation_ready', {
              asset_id: file.assetId,
              wait_attempt: attempt + 1,
              total_wait_ms: attempt * config.propagationDelay,
            });
          }
          // Prefer the asset ID from the directory listing if we got one
          if (convertedFile.assetId) convertedAssetId = convertedFile.assetId;
          break;
        }
        if (attempt < maxPropagationAttempts - 1) {
          await sleep(config.propagationDelay);
          if (state.stopped) throw new Error('Download stopped by user');
        }
      } catch (listErr) {
        if (listErr.message?.includes('stopped')) throw listErr;
        if (attempt === 0) {
          convertedFile = null;
        }
        break;
      }
    }

    if (!convertedFile) {
      events.emit('aic_propagation_exhausted', {
        asset_id: file.assetId,
        attempts: maxPropagationAttempts,
        total_wait_ms: (maxPropagationAttempts - 1) * config.propagationDelay,
      });
    }

    return { convertedAssetId: convertedAssetId || null, dlPath, region };
  } catch (e) {
    if (e != null && typeof e === 'object' && !e.stage) e.stage = 'download_ai';
    throw e;
  }
}

// --- downloadAIC (v1.5.3 lines 1094-1130) ---

export async function downloadAIC(file) {
  const region = _validateRegion(file.region || state.storageRegion);
  const url = `https://platform-cs-edge-${region}.adobe.io/content/storage/id/${file.assetId}`;
  let resp;
  try {
    resp = await fetchWithRetry(url, { headers: { Accept: '*/*' } });
    const blob = await resp.blob();
    if (blob.size > 0) {
      events.emit('aic_download_method', {
        path: file.path,
        name: file.name,
        method: 'primary',
        size: blob.size,
      });
      return blob;
    }
  } catch (e) {
    if (e != null && typeof e === 'object' && !e.stage) e.stage = 'primary_download';
    throw e;
  }
  // Composite doc fallback (empty primary response)
  try {
    events.emit('aic_download_method', {
      path: file.path,
      name: file.name,
      method: 'composite_fallback',
      primary_error: 'empty response',
    });
    const mResp = await fetchWithRetry(`https://cc-api-storage.adobe.io/id/${file.assetId}`, {
      headers: { Accept: '*/*' },
    });
    return mResp.blob();
  } catch (e) {
    if (e != null && typeof e === 'object' && !e.stage) e.stage = 'composite_fallback';
    throw e;
  }
}

// --- processFile (v1.5.3 lines 1169-1336) ---

export async function processFile(file) {
  file.retry_history = file.retry_history || [];
  if (file.retryCount == null) file.retryCount = 0;
  if (file.truncationRetries == null) file.truncationRetries = 0;
  logDiagnostic({ event: 'file_start', level: 'DEBUG', data: { path: file.path, category: file.category } });

  // D8: conversion result cached across retry iterations so a failed download tier
  // doesn't trigger a full reconversion. Invalidated only when a download tier
  // reports the converted asset gone (HTTP 404 / SERVER_BAD_CONTENT).
  let cachedConversion = null;

  // Iterative retry loop to avoid stack overflow
  while (file.retryCount < config.maxRetries && !state.stopped) {
    const t0 = Date.now();
    const attemptNum = file.retry_history.length + 1;
    const tierLog = [];

    try {
      let blob,
        saveName = file.name;
      switch (file.category) {
        case 'psdc': {
          let psdcResult = null;
          try {
            // D8: reuse the cached conversion on retry — reconversion only happens
            // after the cache was invalidated (converted asset gone).
            psdcResult = cachedConversion || await downloadPSDC(file);
            cachedConversion = psdcResult;
            saveName = file.name.replace(/\.psdc$/i, '.psd');
          } catch (psdcErr) {
            if (state.stopped) throw psdcErr;
            // Conversion failed — fall back to raw PSDC file download
            events.emit('psdc_raw_fallback_start', {
              path: file.path,
              name: file.name,
              stage: psdcErr.stage || null,
              error: psdcErr.message,
              response_body: psdcErr.details?.response_body || null,
              http_status: psdcErr.details?.http_status || null,
            });
            if (config.directUrlDownload) {
              const rawToken = getToken();
              const rawRegion = _validateRegion(file.region || state.storageRegion);
              const rawPrimaryUrl = `https://platform-cs-edge-${rawRegion}.adobe.io/content/storage/id/${file.assetId}`;
              tierLog.push({ tier: 'raw_fallback', method: 'direct_url_primary', result: 'pending' });
              try {
                // Raw original: file.size (repo:size) is exact — shadow mode (D4)
                const result = await saveFileByUrl(rawPrimaryUrl, file, file.name, rawToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_primary' });
                tierLog[tierLog.length - 1].result = 'ok';
                events.emit('psdc_raw_fallback_success', { path: file.path, name: file.name, size: result.fileSize, conversion_error: psdcErr.message });
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path, size: file.size, downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0, category: file.category, save_name: file.name,
                  expected_size: file.size, download_method: 'direct_url_raw_fallback', tierLog,
                });
                return;
              } catch (rawErr) {
                tierLog[tierLog.length - 1].result = rawErr.details?.error_category || 'error';
                if (state.stopped) throw rawErr;
                if (rawErr.details?.error_category === 'auth_expired') throw rawErr;
                // Tier 2: Fallback CDN for raw file
                const rawFallbackUrl = `https://cc-api-storage.adobe.io/id/${file.assetId}`;
                tierLog.push({ tier: 'raw_fallback_2', method: 'direct_url_fallback', result: 'pending' });
                try {
                  const freshToken = getToken();
                  if (!freshToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const result = await saveFileByUrl(rawFallbackUrl, file, file.name, freshToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_fallback' });
                  tierLog[tierLog.length - 1].result = 'ok';
                  events.emit('psdc_raw_fallback_success', { path: file.path, name: file.name, size: result.fileSize, conversion_error: psdcErr.message });
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: file.name,
                    expected_size: file.size, download_method: 'direct_url_raw_fallback', tierLog,
                  });
                  return;
                } catch (rawFallbackErr) {
                  tierLog[tierLog.length - 1].result = rawFallbackErr.details?.error_category || 'error';
                  if (state.stopped) throw rawFallbackErr;
                  if (rawFallbackErr.details?.error_category === 'auth_expired') throw rawFallbackErr;
                }
              }
            }
            // Legacy blob fallback (directUrlDownload disabled or both direct URLs failed)
            if (typeof URL.createObjectURL !== 'function') {
              const noFallbackErr = new Error('All direct URL download tiers failed; blob fallback unavailable in service worker');
              noFallbackErr.nonRetryable = true;
              noFallbackErr.details = { error_category: 'download_failed' };
              noFallbackErr.stage = 'psdc_raw_fallback';
              throw noFallbackErr;
            }
            tierLog.push({ tier: 3, method: 'blob', result: 'pending' });
            blob = await downloadRegularFile(file);
            tierLog[tierLog.length - 1].result = 'ok';
            saveName = file.name;
            events.emit('psdc_raw_fallback_success', { path: file.path, name: file.name, size: blob.size, conversion_error: psdcErr.message });
            break;
          }
          // PSDC conversion succeeded — download converted PSD via direct URL
          if (psdcResult) {
            const { convertedAssetId, convertedSize, region: psdRegion, dlPath } = psdcResult;
            const currentToken = getToken();

            if (convertedAssetId) {
              // ID-based download (preferred)
              const primaryUrl = `https://platform-cs-edge-${psdRegion}.adobe.io/content/storage/id/${convertedAssetId}`;
              const fallbackUrl = `https://cc-api-storage.adobe.io/id/${convertedAssetId}`;

              // Converted files enforce size (D4): repo:size from the listFolder entry is
              // the authoritative converted byte count. Missing/zero size → enforcement
              // skipped (no header-harvest fallback — zero pre-download requests, D3).
              const expectedBytes = convertedSize > 0 ? convertedSize : undefined;
              if (!expectedBytes) {
                events.emit('expected_size_unavailable', { path: file.path, asset_id: convertedAssetId });
              }

              // Tier 1: Primary CDN (with one in-tier retry after a short backoff — P1.11)
              tierLog.push({ tier: 1, method: 'direct_url_primary', result: 'pending' });
              try {
                let result;
                try {
                  result = await saveFileByUrl(primaryUrl, file, saveName, currentToken, { expectedBytes, enforceSize: !!expectedBytes, tier: 'primary' });
                  tierLog[tierLog.length - 1].result = 'ok';
                } catch (primaryErr) {
                  tierLog[tierLog.length - 1].result = primaryErr.details?.error_category || 'error';
                  if (state.stopped) throw primaryErr;
                  if (primaryErr.details?.error_category === 'auth_expired') throw primaryErr;
                  await sleep(config.primaryRetryDelayMs);
                  if (state.stopped) throw primaryErr;
                  tierLog.push({ tier: 1, method: 'direct_url_primary_retry', result: 'pending' });
                  const retryToken = getToken();
                  if (!retryToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  result = await saveFileByUrl(primaryUrl, file, saveName, retryToken, { expectedBytes, enforceSize: !!expectedBytes, tier: 'primary_retry' });
                  tierLog[tierLog.length - 1].result = 'ok';
                }
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path, size: file.size, downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                  expected_size: expectedBytes ?? null, download_method: 'direct_url', tierLog,
                });
                return;
              } catch (directErr) {
                tierLog[tierLog.length - 1].result = directErr.details?.error_category || 'error';
                if (state.stopped) throw directErr;
                if (directErr.details?.error_category === 'auth_expired') throw directErr;

                events.emit('fallback_attempt', {
                  path: file.path, primary_url: primaryUrl,
                  fallback_url: fallbackUrl, primary_error: directErr.message,
                  primary_error_category: directErr.details?.error_category || null,
                });

                // Tier 2: :block_download presigned descriptor (P1.9, D2). Best-effort —
                // ANY failure (descriptor error incl. 400/404, missing/non-https href,
                // presigned download failure) falls through to the cc-api-storage tier;
                // this tier must never make the outcome worse. Only a user stop aborts.
                let blockErr = null;
                tierLog.push({ tier: 2, method: 'block_download', result: 'pending' });
                try {
                  const bdToken = getToken();
                  if (!bdToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const presignedHref = await _getBlockDownloadUrl(convertedAssetId, psdRegion, bdToken);
                  events.emit('blockdownload_attempt', {
                    path: file.path, presigned_host: new URL(presignedHref).hostname,
                  });
                  const result = await saveFileByUrl(presignedHref, file, saveName, null, { omitAuth: true, expectedBytes, enforceSize: !!expectedBytes, tier: 'block_download' });
                  tierLog[tierLog.length - 1].result = 'ok';
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                    expected_size: expectedBytes ?? null, download_method: 'block_download', tierLog,
                  });
                  return;
                } catch (bdErr) {
                  tierLog[tierLog.length - 1].result = bdErr.details?.error_category || 'error';
                  if (state.stopped) throw bdErr;
                  blockErr = bdErr;
                  events.emit('blockdownload_unavailable', {
                    path: file.path,
                    http_status: bdErr.details?.http_status || null,
                    reason: bdErr.message,
                  });
                }

                // Tier 3: Fallback CDN
                tierLog.push({ tier: 3, method: 'direct_url_fallback', result: 'pending' });
                try {
                  const freshToken = getToken();
                  if (!freshToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const result = await saveFileByUrl(fallbackUrl, file, saveName, freshToken, { expectedBytes, enforceSize: !!expectedBytes, tier: 'fallback' });
                  tierLog[tierLog.length - 1].result = 'ok';
                  events.emit('fallback_success', { path: file.path, fallback_url: fallbackUrl });
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                    expected_size: expectedBytes ?? null, download_method: 'direct_url_fallback', tierLog,
                  });
                  return;
                } catch (fallbackErr) {
                  tierLog[tierLog.length - 1].result = fallbackErr.details?.error_category || 'error';
                  if (state.stopped) throw fallbackErr;
                  if (fallbackErr.details?.error_category === 'auth_expired') throw fallbackErr;
                  // D8: reconvert on the next retry only if a tier reported the converted asset gone
                  // (a 404 from the block_download descriptor counts — same temp asset)
                  if (_isConvertedAssetGone(directErr) || _isConvertedAssetGone(blockErr) || _isConvertedAssetGone(fallbackErr)) {
                    cachedConversion = null;
                  }
                  throw fallbackErr; // No more tiers for converted PSDC
                }
              }
            } else {
              // Path-based download (propagation exhausted — no converted file ID found)
              // No directory entry → no authoritative converted size; enforcement skipped (D4).
              events.emit('expected_size_unavailable', { path: file.path, asset_id: null });
              const encodedPath = dlPath.split('/').map(s => encodeURIComponent(s)).join('/');
              const pathPrimaryUrl = `https://platform-cs.adobe.io/content/storage/path/${state.repositoryId}/${encodedPath}`;
              const pathFallbackUrl = `https://platform-cs-edge-${psdRegion}.adobe.io/content/storage/path/${state.repositoryId}/${encodedPath}`;

              tierLog.push({ tier: 1, method: 'direct_url_path_primary', result: 'pending' });
              try {
                const pathToken = getToken();
                if (!pathToken) {
                  const authErr = new Error('No authentication token available');
                  authErr.nonRetryable = true;
                  authErr.details = { error_category: 'auth_expired' };
                  throw authErr;
                }
                const result = await saveFileByUrl(pathPrimaryUrl, file, saveName, pathToken);
                tierLog[tierLog.length - 1].result = 'ok';
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path, size: file.size, downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                  expected_size: null, download_method: 'direct_url_path', tierLog,
                });
                return;
              } catch (pathErr) {
                tierLog[tierLog.length - 1].result = pathErr.details?.error_category || 'error';
                if (state.stopped) throw pathErr;
                if (pathErr.details?.error_category === 'auth_expired') throw pathErr;

                tierLog.push({ tier: 2, method: 'direct_url_path_fallback', result: 'pending' });
                try {
                  const freshToken = getToken();
                  if (!freshToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const result = await saveFileByUrl(pathFallbackUrl, file, saveName, freshToken);
                  tierLog[tierLog.length - 1].result = 'ok';
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                    expected_size: null, download_method: 'direct_url_path_fallback', tierLog,
                  });
                  return;
                } catch (pathFallbackErr) {
                  tierLog[tierLog.length - 1].result = pathFallbackErr.details?.error_category || 'error';
                  if (state.stopped) throw pathFallbackErr;
                  if (pathFallbackErr.details?.error_category === 'auth_expired') throw pathFallbackErr;
                  // D8: the path-based route downloads the converted temp file too —
                  // a 404 here also means the asset is gone, so force reconversion
                  if (_isConvertedAssetGone(pathErr) || _isConvertedAssetGone(pathFallbackErr)) {
                    cachedConversion = null;
                  }
                  throw pathFallbackErr; // No more tiers
                }
              }
            }
          }
          break;
        }
        case 'aic': {
          let aicResult = null;
          try {
            aicResult = await convertAIC(file);
            saveName = (file.name || 'unnamed').replace(/\.[^.]+$/, '.ai');
          } catch (aicErr) {
            if (state.stopped) throw aicErr;
            // Conversion failed — fall back to raw AIC download
            events.emit('aic_raw_fallback_start', {
              path: file.path,
              name: file.name,
              stage: aicErr.stage || null,
              error: aicErr.message,
              http_status: aicErr.details?.http_status || null,
            });

            if (config.directUrlDownload) {
              const rawToken = getToken();
              if (!rawToken) {
                const authErr = new Error('No authentication token available');
                authErr.nonRetryable = true;
                authErr.details = { error_category: 'auth_expired' };
                throw authErr;
              }
              const rawRegion = _validateRegion(file.region || state.storageRegion);
              const rawPrimaryUrl = `https://platform-cs-edge-${rawRegion}.adobe.io/content/storage/id/${file.assetId}`;
              tierLog.push({ tier: 'raw_fallback', method: 'direct_url_primary', result: 'pending' });
              try {
                // Raw original: file.size (repo:size) is exact — shadow mode (D4)
                const result = await saveFileByUrl(rawPrimaryUrl, file, file.name, rawToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_primary' });
                tierLog[tierLog.length - 1].result = 'ok';
                events.emit('aic_raw_fallback_success', { path: file.path, name: file.name, size: result.fileSize, conversion_error: aicErr.message });
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path, size: file.size, downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0, category: file.category, save_name: file.name,
                  expected_size: file.size, download_method: 'direct_url_raw_fallback', tierLog,
                });
                return;
              } catch (rawErr) {
                tierLog[tierLog.length - 1].result = rawErr.details?.error_category || 'error';
                if (state.stopped) throw rawErr;
                if (rawErr.details?.error_category === 'auth_expired') throw rawErr;
                // Tier 2: Fallback CDN for raw file
                const rawFallbackUrl = `https://cc-api-storage.adobe.io/id/${file.assetId}`;
                tierLog.push({ tier: 'raw_fallback_2', method: 'direct_url_fallback', result: 'pending' });
                try {
                  const freshToken = getToken();
                  if (!freshToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const result = await saveFileByUrl(rawFallbackUrl, file, file.name, freshToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_fallback' });
                  tierLog[tierLog.length - 1].result = 'ok';
                  events.emit('aic_raw_fallback_success', { path: file.path, name: file.name, size: result.fileSize, conversion_error: aicErr.message });
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: file.name,
                    expected_size: file.size, download_method: 'direct_url_raw_fallback', tierLog,
                  });
                  return;
                } catch (rawFallbackErr) {
                  tierLog[tierLog.length - 1].result = rawFallbackErr.details?.error_category || 'error';
                  if (state.stopped) throw rawFallbackErr;
                  if (rawFallbackErr.details?.error_category === 'auth_expired') throw rawFallbackErr;
                }
              }
            }
            // Legacy blob fallback
            if (typeof URL.createObjectURL !== 'function') {
              const noFallbackErr = new Error('All direct URL download tiers failed; blob fallback unavailable in service worker');
              noFallbackErr.nonRetryable = true;
              noFallbackErr.details = { error_category: 'download_failed' };
              noFallbackErr.stage = 'aic_raw_fallback';
              throw noFallbackErr;
            }
            tierLog.push({ tier: 3, method: 'blob', result: 'pending' });
            blob = await downloadAIC(file);
            tierLog[tierLog.length - 1].result = 'ok';
            saveName = file.name;
            events.emit('aic_raw_fallback_success', { path: file.path, name: file.name, size: blob.size, conversion_error: aicErr.message });
            break;
          }

          // Conversion succeeded — download converted .ai via direct URL
          if (aicResult) {
            const { convertedAssetId, region: aiRegion, dlPath } = aicResult;
            const currentToken = getToken();

            if (convertedAssetId) {
              // ID-based download (preferred)
              const primaryUrl = `https://platform-cs-edge-${aiRegion}.adobe.io/content/storage/id/${convertedAssetId}`;
              const fallbackUrl = `https://cc-api-storage.adobe.io/id/${convertedAssetId}`;

              // Validate AI magic bytes before full download
              try {
                await _validateAiMagicBytes(primaryUrl, file.path);
              } catch (validationErr) {
                if (validationErr.details?.error_category === 'invalid_ai') throw validationErr;
                try {
                  await _validateAiMagicBytes(fallbackUrl, file.path);
                } catch (fallbackValidationErr) {
                  if (fallbackValidationErr.details?.error_category === 'invalid_ai') throw fallbackValidationErr;
                  logDiagnostic({ event: 'ai_validation_skipped', level: 'WARN', data: { path: file.path, reason: 'Range request failed on both CDNs' } });
                }
              }

              // Tier 1: Primary CDN
              tierLog.push({ tier: 1, method: 'direct_url_primary', result: 'pending' });
              try {
                const result = await saveFileByUrl(primaryUrl, file, saveName, currentToken);
                tierLog[tierLog.length - 1].result = 'ok';
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path, size: file.size, downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                  expected_size: file.size, download_method: 'direct_url_converted', tierLog,
                });
                return;
              } catch (directErr) {
                tierLog[tierLog.length - 1].result = directErr.details?.error_category || 'error';
                if (state.stopped) throw directErr;
                if (directErr.details?.error_category === 'auth_expired') throw directErr;

                // Tier 2: Fallback CDN
                tierLog.push({ tier: 2, method: 'direct_url_fallback', result: 'pending' });
                try {
                  events.emit('fallback_attempt', {
                    path: file.path, primary_url: primaryUrl,
                    fallback_url: fallbackUrl, primary_error: directErr.message,
                    primary_error_category: directErr.details?.error_category || null,
                  });
                  const freshToken = getToken();
                  if (!freshToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const result = await saveFileByUrl(fallbackUrl, file, saveName, freshToken);
                  tierLog[tierLog.length - 1].result = 'ok';
                  events.emit('fallback_success', { path: file.path, fallback_url: fallbackUrl });
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                    expected_size: file.size, download_method: 'direct_url_converted_fallback', tierLog,
                  });
                  return;
                } catch (fallbackErr) {
                  tierLog[tierLog.length - 1].result = fallbackErr.details?.error_category || 'error';
                  if (state.stopped) throw fallbackErr;
                  if (fallbackErr.details?.error_category === 'auth_expired') throw fallbackErr;
                  throw fallbackErr; // No more tiers for converted AIC
                }
              }
            } else {
              // Path-based download (propagation exhausted — no converted file ID found)
              const encodedPath = dlPath.split('/').map(s => encodeURIComponent(s)).join('/');
              const pathPrimaryUrl = `https://platform-cs.adobe.io/content/storage/path/${state.repositoryId}/${encodedPath}`;
              const pathFallbackUrl = `https://platform-cs-edge-${aiRegion}.adobe.io/content/storage/path/${state.repositoryId}/${encodedPath}`;

              tierLog.push({ tier: 1, method: 'direct_url_path_primary', result: 'pending' });
              try {
                const pathToken = getToken();
                if (!pathToken) {
                  const authErr = new Error('No authentication token available');
                  authErr.nonRetryable = true;
                  authErr.details = { error_category: 'auth_expired' };
                  throw authErr;
                }
                const result = await saveFileByUrl(pathPrimaryUrl, file, saveName, pathToken);
                tierLog[tierLog.length - 1].result = 'ok';
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path, size: file.size, downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                  expected_size: file.size, download_method: 'direct_url_path', tierLog,
                });
                return;
              } catch (pathErr) {
                tierLog[tierLog.length - 1].result = pathErr.details?.error_category || 'error';
                if (state.stopped) throw pathErr;
                if (pathErr.details?.error_category === 'auth_expired') throw pathErr;

                tierLog.push({ tier: 2, method: 'direct_url_path_fallback', result: 'pending' });
                try {
                  const freshToken = getToken();
                  if (!freshToken) {
                    const authErr = new Error('No authentication token available');
                    authErr.nonRetryable = true;
                    authErr.details = { error_category: 'auth_expired' };
                    throw authErr;
                  }
                  const result = await saveFileByUrl(pathFallbackUrl, file, saveName, freshToken);
                  tierLog[tierLog.length - 1].result = 'ok';
                  file.downloaded = true;
                  file.downloadedSize = result.fileSize;
                  file.downloadTime = Date.now() - t0;
                  state.downloadedFiles++;
                  state.downloadedBytes += result.fileSize;
                  state.sessionMetrics.consecutiveFailures = 0;
                  events.emit('file_success', {
                    path: file.path, size: file.size, downloaded_size: result.fileSize,
                    duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
                    expected_size: file.size, download_method: 'direct_url_path_fallback', tierLog,
                  });
                  return;
                } catch (pathFallbackErr) {
                  tierLog[tierLog.length - 1].result = pathFallbackErr.details?.error_category || 'error';
                  if (state.stopped) throw pathFallbackErr;
                  if (pathFallbackErr.details?.error_category === 'auth_expired') throw pathFallbackErr;
                  throw pathFallbackErr; // No more tiers
                }
              }
            }
          }
          break;
        }
        case 'ffgenimg':
        case 'ffgenvid': {
          let manifest;
          try {
            events.emit('ffgen_manifest_fetch', { path: file.path, name: file.name, category: file.category });
            manifest = await _fetchManifest(file);
          } catch (manifestErr) {
            if (state.stopped) throw manifestErr;
            const didFallback = await _ffgenRawFallback(file, t0, tierLog, manifestErr.message);
            if (didFallback) return;
            break;
          }

          const typeMap = { 'image/png': '.png', 'image/jpeg': '.jpg', 'video/mp4': '.mp4' };
          const ext = typeMap[manifest.type] || '.bin';
          saveName = file.name.replace(/\.[^.]+$/, ext);
          const region = _validateRegion(file.region || state.storageRegion);
          const componentUrl = `https://platform-cs-edge-${region}.adobe.io/composite/component/id/${file.assetId}?component_id=${manifest.componentId}&revision=${manifest.revision}`;

          events.emit('ffgen_component_download', { path: file.path, type: manifest.type, ext });
          tierLog.push({ tier: 1, method: 'composite_component', result: 'pending' });
          const token = getToken();
          const result = await saveFileByUrl(componentUrl, file, saveName, token);
          tierLog[tierLog.length - 1].result = 'ok';

          file.downloaded = true;
          file.downloadedSize = result.fileSize;
          file.downloadTime = Date.now() - t0;
          state.downloadedFiles++;
          state.downloadedBytes += result.fileSize;
          state.sessionMetrics.consecutiveFailures = 0;
          events.emit('file_success', {
            path: file.path, size: file.size, downloaded_size: result.fileSize,
            duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
            expected_size: file.size, download_method: 'composite_component', tierLog,
          });
          return;
        }
        case 'ffgenaud': {
          let manifest;
          try {
            events.emit('ffgen_manifest_fetch', { path: file.path, name: file.name, category: file.category });
            manifest = await _fetchManifest(file);
          } catch (manifestErr) {
            if (state.stopped) throw manifestErr;
            const didFallback = await _ffgenRawFallback(file, t0, tierLog, manifestErr.message);
            if (didFallback) return;
            break;
          }

          let presigned;
          try {
            events.emit('ffgenaud_presigned_fetch', { path: file.path, name: file.name });
            presigned = await _fetchPresignedUrl(file, manifest.componentId, manifest.revision);
          } catch (presignedErr) {
            if (state.stopped) throw presignedErr;
            events.emit('ffgenaud_presigned_failed', {
              path: file.path, name: file.name, error: presignedErr.message,
            });
            const didFallback = await _ffgenRawFallback(file, t0, tierLog, presignedErr.message);
            if (didFallback) return;
            break;
          }

          const typeMap = { 'audio/wav': '.wav', 'audio/mpeg': '.mp3' };
          const ext = typeMap[presigned.type] || '.bin';
          saveName = file.name.replace(/\.[^.]+$/, ext);

          tierLog.push({ tier: 1, method: 'presigned_url', result: 'pending' });
          const result = await saveFileByUrl(presigned.href, file, saveName, null, { omitAuth: true });
          tierLog[tierLog.length - 1].result = 'ok';

          file.downloaded = true;
          file.downloadedSize = result.fileSize;
          file.downloadTime = Date.now() - t0;
          state.downloadedFiles++;
          state.downloadedBytes += result.fileSize;
          state.sessionMetrics.consecutiveFailures = 0;
          events.emit('file_success', {
            path: file.path, size: file.size, downloaded_size: result.fileSize,
            duration_ms: Date.now() - t0, category: file.category, save_name: saveName,
            expected_size: file.size, download_method: 'presigned_url', tierLog,
          });
          return;
        }
        default: {
          if (config.directUrlDownload) {
            const currentToken = getToken();
            const region = _validateRegion(file.region || state.storageRegion);
            const primaryUrl = `https://platform-cs-edge-${region}.adobe.io/content/storage/id/${file.assetId}`;
            const fallbackCdnUrl = `https://cc-api-storage.adobe.io/id/${file.assetId}`;

            // Tier 1: Direct URL download from primary CDN
            // Raw original: file.size (repo:size) is exact — shadow mode (D4)
            tierLog.push({ tier: 1, method: 'direct_url_primary', result: 'pending' });
            try {
              const result = await saveFileByUrl(primaryUrl, file, saveName, currentToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_primary' });
              tierLog[tierLog.length - 1].result = 'ok';
              file.downloaded = true;
              file.downloadedSize = result.fileSize;
              file.downloadTime = Date.now() - t0;
              state.downloadedFiles++;
              state.downloadedBytes += result.fileSize;
              state.sessionMetrics.consecutiveFailures = 0;
              events.emit('file_success', {
                path: file.path,
                size: file.size,
                downloaded_size: result.fileSize,
                duration_ms: Date.now() - t0,
                category: file.category,
                save_name: saveName,
                expected_size: file.size,
                download_method: 'direct_url',
                tierLog,
              });
              return; // Success — exit retry loop
            } catch (directErr) {
              tierLog[tierLog.length - 1].result = directErr.details?.error_category || 'error';
              if (state.stopped) throw directErr;
              if (directErr.details?.error_category === 'auth_expired') throw directErr;

              // Tier 2: Direct URL from fallback CDN
              tierLog.push({ tier: 2, method: 'direct_url_fallback', result: 'pending' });
              try {
                events.emit('fallback_attempt', {
                  path: file.path,
                  primary_url: primaryUrl,
                  fallback_url: fallbackCdnUrl,
                  primary_error: directErr.message,
                  primary_error_category: directErr.details?.error_category || null,
                });
                const freshToken = getToken();
                if (!freshToken) {
                  const authErr = new Error('No authentication token available');
                  authErr.nonRetryable = true;
                  authErr.details = { error_category: 'auth_expired' };
                  throw authErr;
                }
                const result = await saveFileByUrl(fallbackCdnUrl, file, saveName, freshToken, { expectedBytes: file.size, enforceSize: false, tier: 'raw_fallback' });
                tierLog[tierLog.length - 1].result = 'ok';
                events.emit('fallback_success', { path: file.path, fallback_url: fallbackCdnUrl });
                file.downloaded = true;
                file.downloadedSize = result.fileSize;
                file.downloadTime = Date.now() - t0;
                state.downloadedFiles++;
                state.downloadedBytes += result.fileSize;
                state.sessionMetrics.consecutiveFailures = 0;
                events.emit('file_success', {
                  path: file.path,
                  size: file.size,
                  downloaded_size: result.fileSize,
                  duration_ms: Date.now() - t0,
                  category: file.category,
                  save_name: saveName,
                  expected_size: file.size,
                  download_method: 'direct_url_fallback',
                  tierLog,
                });
                return; // Success — exit retry loop
              } catch (fallbackErr) {
                tierLog[tierLog.length - 1].result = fallbackErr.details?.error_category || 'error';
                if (state.stopped) throw fallbackErr;
                if (fallbackErr.details?.error_category === 'auth_expired') throw fallbackErr;

                // Tier 3: Legacy blob path
                events.emit('direct_url_fallback_to_blob', {
                  path: file.path,
                  primary_error: directErr.message,
                  fallback_error: fallbackErr.message,
                });
              }
            }
          }
          // Legacy blob fallback (also used when directUrlDownload is disabled)
          tierLog.push({ tier: 3, method: 'blob', result: 'pending' });
          blob = await downloadRegularFile(file);
          tierLog[tierLog.length - 1].result = 'ok';
          break;
        }
      }
      if (!blob || blob.size === 0) {
        const err = new Error('Downloaded file is empty (0 bytes)');
        err.details = { error_category: 'empty_response' };
        throw err;
      }
      if (file.size > 0 && blob.size < file.size * 0.5) {
        events.emit('size_warning', {
          path: file.path,
          name: file.name,
          actual_size: blob.size,
          expected_size: file.size,
          category: file.category,
          save_name: saveName,
        });
      }
      try {
        await saveFile(blob, file, saveName);
      } catch (saveErr) {
        events.emit('file_save_error', {
          path: file.path,
          save_name: saveName,
          error: saveErr.message,
          error_name: saveErr.name,
          blob_size: blob.size,
        });
        throw saveErr;
      }
      file.downloaded = true;
      file.downloadedSize = blob.size;
      file.downloadTime = Date.now() - t0;
      state.downloadedFiles++;
      state.downloadedBytes += blob.size;
      state.sessionMetrics.consecutiveFailures = 0;
      events.emit('file_success', {
        path: file.path,
        size: file.size,
        downloaded_size: blob.size,
        duration_ms: Date.now() - t0,
        category: file.category,
        save_name: saveName,
        expected_size: file.size,
        tierLog,
      });
      return; // Success - exit retry loop

    } catch (e) {
      const duration_ms = Date.now() - t0;
      const details = e.details || {};
      const attemptEntry = {
        timestamp: new Date().toISOString(),
        attempt: attemptNum,
        http_status: details.http_status || null,
        error_category: details.error_category || _classifyError(e, null),
        url: details.url || null,
        stage: e.stage || null,
        duration_ms,
        error_message: e.message,
        response_body: details.response_body || null,
        response_headers: details.response_headers || null,
      };
      file.retry_history.push(attemptEntry);

      // Truncation retries are capped separately from maxRetries: at the cap, mark
      // non-retryable so the file fails honestly instead of looping conversions.
      if (attemptEntry.error_category === 'truncated_download') {
        file.truncationRetries++;
        if (file.truncationRetries > config.truncationMaxRetries) {
          e.nonRetryable = true;
        }
      }

      file.retryCount++;
      if (e.nonRetryable || file.retryCount >= config.maxRetries) {
        file.failed = true;
        file.error = e.message;
        state.failedFiles++;
        state.sessionMetrics.consecutiveFailures++;
        if (state.sessionMetrics.consecutiveFailures > state.sessionMetrics.maxConsecutiveFailures) {
          state.sessionMetrics.maxConsecutiveFailures = state.sessionMetrics.consecutiveFailures;
        }
        state.errors.push({ file: file.path, error: e.message, retries: file.retryCount, retry_history: file.retry_history });
        events.emit('file_fail', {
          path: file.path,
          name: file.name,
          size: file.size,
          duration_ms,
          error: e.message,
          retry_count: file.retryCount,
          retry_history: file.retry_history,
          http_status: attemptEntry.http_status,
          error_category: attemptEntry.error_category,
          url: attemptEntry.url,
          stage: attemptEntry.stage,
          category: file.category,
          response_body: attemptEntry.response_body,
          tierLog,
          expected_bytes: details.expected ?? null,
          actual_bytes: details.actual ?? null,
        });
        // Populate failed files list for sidepanel visibility
        state.failedFilesList.push({
          path: file.path,
          name: file.name,
          error: e.message,
          errorCategory: attemptEntry.error_category,
          interruptReason: e.details?.interrupt_reason || null,
          size: file.size,
          retryCount: file.retryCount,
          category: file.category,
          timestamp: new Date().toISOString(),
          httpStatus: attemptEntry.http_status,
          url: (() => { try { return attemptEntry.url ? new URL(attemptEntry.url).hostname : null; } catch { return attemptEntry.url || null; } })(),
          responseBody: (attemptEntry.response_body || '').slice(0, 200),
          responseHeaders: attemptEntry.response_headers || null,
          durationMs: duration_ms,
          stage: attemptEntry.stage,
          tierLog,
          retryHistory: file.retry_history,
          // Truncated downloads carry expected vs actual byte counts (Task 9 — TSV export)
          expectedBytes: details.expected ?? null,
          actualBytes: details.actual ?? null,
        });
        // Fire-and-forget persist to session storage for sidepanel recovery (capped at 500)
        const persistList = state.failedFilesList.length > 500
          ? state.failedFilesList.slice(-500)
          : state.failedFilesList;
        chrome.storage.session.set({ [config.failedFilesKey]: persistList }).catch(() => {});
        return; // Failed - exit retry loop
      } else {
        events.emit('file_retry', {
          path: file.path,
          name: file.name,
          attempt: attemptNum,
          error: e.message,
          error_category: attemptEntry.error_category,
          http_status: attemptEntry.http_status,
          url: attemptEntry.url,
          duration_ms: attemptEntry.duration_ms,
          stage: attemptEntry.stage,
          response_body: attemptEntry.response_body,
          response_headers: attemptEntry.response_headers,
          category: file.category,
        });
        const delay = config.retryBaseDelay * Math.pow(2, file.retryCount - 1);
        events.emit('file_retry_queued', {
          name: file.name,
          retryCount: file.retryCount,
          maxRetries: config.maxRetries,
          delay_seconds: delay / 1000,
        });
        await sleep(delay);
        // Stop guard after retry delay sleep
        if (state.stopped) return;
        // Continue loop to retry
      }
    }
  }
}

function _getDisplayName(file) {
  switch (file.category) {
    case 'psdc': {
      const dotIdx = file.name.lastIndexOf('.');
      return dotIdx > 0 ? file.name.slice(0, dotIdx) + '.psd' : file.name + '.psd';
    }
    case 'aic': {
      const dotIdx = file.name.lastIndexOf('.');
      return dotIdx > 0 ? file.name.slice(0, dotIdx) + '.ai' : file.name + '.ai';
    }
    case 'ffgenimg':
    case 'ffgenvid':
    case 'ffgenaud': {
      const dotIdx = file.name.lastIndexOf('.');
      return dotIdx > 0 ? file.name.slice(0, dotIdx) : file.name;
    }
    default: return file.name;
  }
}

// --- _runWorkers (v1.5.3 lines 1338-1384) ---

async function _runWorkers(fileList) {
  const workerCount = config.concurrentDownloads;
  events.emit('workers_init', { count: workerCount });
  let idx = 0;
  const worker = async (workerId) => {
    while (!state.stopped) {
      if (state.paused) {
        await waitForResume();
        if (state.stopped) break;
      }
      const myIdx = idx++;
      if (myIdx >= fileList.length) break;
      const file = fileList[myIdx];
      // Pre-flight freemium gate — stops new files once limit is reached.
      if (false && config.freeFileLimit > 0 && state._freeFilesUsed >= config.freeFileLimit) {
        if (!state._freeLimitEmitted) {
          state._freeLimitEmitted = true;
          state.paused = true;
          state.status = 'paused';
          trackEvent('abd_paywall_hit', { downloaded: state._freeFilesUsed, limit: config.freeFileLimit });
          events.emit('free_limit_reached', { downloaded: state._freeFilesUsed, limit: config.freeFileLimit });
          events.emit('status_change', { status: 'paused' });
        } else {
          state.paused = true;
          state.status = 'paused';
        }
        await waitForResume();
        if (state.stopped) break;
        if (false) continue;
        state._freeLimitEmitted = false;
      }
      // Pre-claim the free slot before processFile to prevent TOCTOU with concurrent workers
      const claimedFreeSlot = false && config.freeFileLimit > 0;
      if (claimedFreeSlot) {
        state._freeFilesUsed++;
        _persistFreeCount();
      }
      state.currentFile = file;
      state.currentFolder = file.path.split('/').slice(0, -1).join('/');
      const displayName = _getDisplayName(file);
      events.emit('worker_status', { workerId, state: 'downloading', fileName: displayName });
      // Reset SW idle timer before each file — fetch() does not reset it, only chrome.* calls do.
      chrome.runtime.getPlatformInfo(() => {});
      await processFile(file);
      events.emit('worker_status', { workerId, state: 'done', fileName: displayName });
      await saveProgress();
      // If the pre-claimed free slot didn't result in a successful download, release it
      if (claimedFreeSlot && !file.downloaded) {
        state._freeFilesUsed--;
        _persistFreeCount();
      }
      // Post-processFile freemium gate — safety net for concurrent boundary
      if (false && config.freeFileLimit > 0
          && state._freeFilesUsed >= config.freeFileLimit) {
        if (!state._freeLimitEmitted) {
          state._freeLimitEmitted = true;
          state.paused = true;
          state.status = 'paused';
          events.emit('free_limit_reached', {
            downloaded: state._freeFilesUsed,
            limit: config.freeFileLimit,
          });
          events.emit('status_change', { status: 'paused' });
        } else {
          state.paused = true;
          state.status = 'paused';
        }
        await waitForResume();
        if (state.stopped) break;
        // After resume, re-check: if still unpaid, loop back to pause
        if (false) continue;
        // Paid — clear flag, proceed normally
        state._freeLimitEmitted = false;
      }
      // Heartbeat logging every 25 files
      const processed = state.downloadedFiles + state.failedFiles;
      if (processed > 0 && processed % 25 === 0) {
        events.emit('download_heartbeat', {
          downloaded_files: state.downloadedFiles,
          failed_files: state.failedFiles,
          total_files: state.totalFiles,
          downloaded_bytes: state.downloadedBytes,
          adaptive_delay: state.adaptiveDelay,
          elapsed_ms: Date.now() - state.startTime,
        });
      }
      // Decay adaptive delay toward baseline when no recent throttling
      if (Date.now() - state.lastThrottleTime > 30000) {
        const oldDelay = state.adaptiveDelay;
        state.adaptiveDelay = Math.max(
          config.requestDelay,
          state.adaptiveDelay * 0.75,
        );
        if (oldDelay !== state.adaptiveDelay) {
          events.emit('adaptive_delay_decrease', {
            old_delay: oldDelay,
            new_delay: state.adaptiveDelay,
            time_since_last_throttle: Date.now() - state.lastThrottleTime,
          });
        }
      }
      // Upward-biased jitter: never faster than baseline
      const jitter = state.adaptiveDelay * (1.0 + Math.random() * 0.5);
      await sleep(jitter);
      // Stop guard after inter-file sleep
      if (state.stopped) break;
    }
    events.emit('worker_status', { workerId, state: 'idle' });
  };
  await Promise.all(Array.from({ length: workerCount }, (_, i) => worker(i)));
}

// --- _askResumeChoice (NEW) ---

const VALID_RESUME_CHOICES = new Set(['resume', 'fresh']);

async function _askResumeChoice(skippedCount, totalFiles) {
  let timeoutId;
  try {
    const response = await Promise.race([
      chrome.runtime.sendMessage({
        type: 'ABD_RESUME_PROMPT',
        skippedCount,
        totalFiles,
      }),
      new Promise((resolve) => {
        timeoutId = setTimeout(() => {
          timeoutId = null;
          events.emit('resume_prompt_timeout', { timeoutMs: config.resumePromptTimeoutMs });
          resolve({ choice: 'fresh' });
        }, config.resumePromptTimeoutMs);
      }),
    ]);
    if (timeoutId != null) clearTimeout(timeoutId);
    if (!VALID_RESUME_CHOICES.has(response?.choice)) {
      logDiagnostic({ event: 'resume_choice_invalid', level: 'WARN', data: { received: response?.choice } });
    }
    return VALID_RESUME_CHOICES.has(response?.choice) ? response.choice : 'fresh';
  } catch {
    if (timeoutId != null) clearTimeout(timeoutId);
    // Sidepanel not open — persist prompt and wait for it to open
    return _askResumeChoicePersisted(skippedCount, totalFiles);
  }
}

async function _askResumeChoicePersisted(skippedCount, totalFiles) {
  // Clear any stale answer from a previous session to prevent silent consumption
  await chrome.storage.session.remove(config.resumeAnswerKey).catch(() => {});
  try {
    await chrome.storage.session.set({
      [config.resumePromptKey]: { skippedCount, totalFiles, timestamp: Date.now() },
    });
    events.emit('resume_prompt_persisted', { skippedCount, totalFiles });

    const deadline = Date.now() + config.resumePromptExtendedTimeoutMs;
    while (Date.now() < deadline) {
      if (state.stopped) break;
      await sleep(config.resumePromptPollIntervalMs);
      if (state.stopped) break;
      try {
        const data = await chrome.storage.session.get(config.resumeAnswerKey);
        const answer = data?.[config.resumeAnswerKey];
        if (answer?.choice) {
          await chrome.storage.session.remove([config.resumePromptKey, config.resumeAnswerKey]);
          return VALID_RESUME_CHOICES.has(answer.choice) ? answer.choice : 'fresh';
        }
      } catch {
        logDiagnostic({ event: 'resume_poll_storage_failed', level: 'WARN' });
        // Session storage read failed — continue polling
      }
    }
  } catch {
    // Session storage write failed — fall through
  }
  // Timeout or error — final answer check before giving up (race window: user
  // may have clicked a button between the last poll and deadline expiry)
  try {
    const finalData = await chrome.storage.session.get(config.resumeAnswerKey);
    const finalAnswer = finalData?.[config.resumeAnswerKey];
    if (finalAnswer?.choice) {
      chrome.storage.session.remove([config.resumePromptKey, config.resumeAnswerKey]).catch(() => {});
      return VALID_RESUME_CHOICES.has(finalAnswer.choice) ? finalAnswer.choice : 'fresh';
    }
  } catch { /* ignore */ }
  chrome.storage.session.remove([config.resumePromptKey, config.resumeAnswerKey]).catch(() => {});
  events.emit('resume_prompt_timeout', { timeoutMs: config.resumePromptExtendedTimeoutMs });
  return 'fresh';
}

// --- _emitDownloadSummary ---

function _emitDownloadSummary() {
  if (state.failedFiles <= 0) return;
  const errorGroups = {};
  for (const f of state.failedFilesList) {
    const cat = f.errorCategory || 'unknown';
    if (!errorGroups[cat]) errorGroups[cat] = { count: 0, files: [] };
    errorGroups[cat].count++;
    if (errorGroups[cat].files.length < 10) errorGroups[cat].files.push(f.name);
  }
  events.emit('download_summary', {
    totalFiles: state.totalFiles,
    downloadedFiles: state.downloadedFiles,
    failedFiles: state.failedFiles,
    errorGroups,
    sessionMetrics: state.sessionMetrics,
  });
}

// --- downloadAll (v1.5.3 lines 1385-1463) ---

export async function downloadAll({ fromRecovery = false } = {}) {

  try { await chrome.downloads.setUiOptions({ enabled: false }); } catch { logDiagnostic({ event: 'set_ui_options_failed', level: 'WARN' }); }
  // SW keepalive heartbeat — resets 30s idle timer every 20s during download
  logDiagnostic({ event: 'keepalive_started', level: 'DEBUG' });
  const _keepaliveInterval = setInterval(() => chrome.runtime.getPlatformInfo(() => {}), 20_000);
  try {
    // C4: Status may already be set synchronously by handler — idempotent
    if (state.status !== 'downloading') {
      state.status = 'downloading';
      events.emit('status_change', { status: 'downloading' });
    }
    // Note: counters are zeroed here and re-accumulated from the resume set below.
    // Recovery (fromRecovery=true) depends on this reset-then-recount pattern.
    state.downloadedFiles = 0;
    state.failedFiles = 0;
    state.downloadedBytes = 0;
    state.paused = false;
    state.stopped = false;
    state.stoppedPhase = null;
    state._freeLimitEmitted = false;
    state.errors = [];
    state.failedFilesList = [];
    chrome.storage.session.remove(config.failedFilesKey).catch(() => {});

    // Task 9: Load persisted free file count for freemium gate persistence
    if (false) {
      try {
        const stored = await chrome.storage.local.get(config.freeFilesUsedKey);
        state._freeFilesUsed = stored[config.freeFilesUsedKey] || 0;
      } catch { state._freeFilesUsed = 0; }
    } else {
      state._freeFilesUsed = 0;
    }

    // Resume support
    const resume = await loadProgress();
    if (resume) {
      const done = new Set(resume.downloadedIds || []);
      const potentialSkip = state.files.filter((f) => done.has(f.assetId)).length;

      if (potentialSkip > 0) {
        if (fromRecovery) {
          // Skip dialog — auto-resume from where we left off
          let skipped = 0;
          state.files.forEach((f) => {
            if (done.has(f.assetId)) {
              f.downloaded = true;
              state.downloadedFiles++;
              state.downloadedBytes += f.size || 0;
              skipped++;
            }
          });
          events.emit('resume_accepted', {
            stale_session_id: resume.sessionId,
            potential_skip: potentialSkip,
            skipped,
            total_files: state.totalFiles,
          });
        } else {
          const choice = await _askResumeChoice(potentialSkip, state.totalFiles);

          if (choice === 'resume') {
            let skipped = 0;
            state.files.forEach((f) => {
              if (done.has(f.assetId)) {
                f.downloaded = true;
                state.downloadedFiles++;
                state.downloadedBytes += f.size || 0;
                skipped++;
              }
            });
            events.emit('resume_accepted', {
              stale_session_id: resume.sessionId,
              potential_skip: potentialSkip,
              skipped,
              total_files: state.totalFiles,
            });
          } else {
            // Clear progress keys from chrome.storage.local
            try {
              const all = await chrome.storage.local.get(null);
              const keys = Object.keys(all).filter((k) => k.startsWith(config.storageKeyPrefix));
              if (keys.length) await chrome.storage.local.remove(keys);
            } catch {
              // Ignore cleanup errors
            }
            events.emit('resume_declined', {
              stale_session_id: resume.sessionId,
              potential_skip: potentialSkip,
              total_files: state.totalFiles,
            });
          }
        }
      }
    }

    // Stop guard: user may have clicked Stop while resume prompt was pending
    if (state.stopped) {
      state.status = 'stopped';
      events.emit('status_change', { status: 'stopped', stoppedPhase: state.stoppedPhase });
      return;
    }

    const pending = state.files.filter((f) => !f.downloaded && !f.failed);
    if (pending.length === 0) {
      logDiagnostic({ event: 'download_nothing_pending', level: 'INFO' });
    }
    events.emit('download_start', {
      pending: pending.length,
      concurrency: config.concurrentDownloads,
      fromRecovery,
    });

    state.startTime = Date.now();
    state.sessionMetrics.startTime = Date.now();
    state.adaptiveDelay = config.requestDelay;
    initializeETA(state.files, config.concurrentDownloads);
    if (resume?.eta) restoreETA(resume.eta);
    await _runWorkers(pending);

    // Reset orphaned files to pristine state so they retry on next run
    if (state.stopped) {
      const orphaned = state.files.filter((f) => !f.downloaded && !f.failed && f.retry_history?.length > 0);
      if (orphaned.length > 0) {
        orphaned.forEach((f) => { f.retryCount = 0; f.retry_history = []; f.error = null; });
        events.emit('stop_orphan_reconciliation', {
          orphaned_count: orphaned.length,
          paths: orphaned.slice(0, 10).map((f) => f.path),
        });
      }
    }

    state.sessionMetrics.endTime = Date.now();
    if (state.sessionMetrics.startTime) {
      const elapsed = (state.sessionMetrics.endTime - state.sessionMetrics.startTime) / 1000;
      if (elapsed > 0) {
        state.sessionMetrics.bytesPerSecond = Math.round(state.downloadedBytes / elapsed);
        state.sessionMetrics.filesPerMinute = Math.round((state.downloadedFiles / elapsed) * 60 * 10) / 10;
      }
    }
    // Task 9: Final persist of free file count before marking complete
    if (false && state._freeFilesUsed > 0) {
      _freeCountWriteInFlight = false; // force flush
      await _persistFreeCount();
    }
    // Clear recovery counter on successful completion
    chrome.storage.session.remove(config.recoveryCountKey).catch(() => {});
    state.status = state.stopped ? 'stopped' : 'complete';
    events.emit('status_change', { status: state.status, stoppedPhase: state.stoppedPhase });
    state.currentFile = null;
    const elapsed = ((Date.now() - state.startTime) / 1000).toFixed(0);
    if (pending.length > 0) {
      if (!state.stopped) {
        events.emit('download_complete_banner', {});
      }
      events.emit('download_complete', {
        downloadedFiles: state.downloadedFiles,
        failedFiles: state.failedFiles,
        downloadedBytes: state.downloadedBytes,
        elapsed: Number(elapsed),
        stopped: state.stopped,
      });
      _emitDownloadSummary();
    }
  } finally {
    logDiagnostic({ event: 'keepalive_stopped', level: 'DEBUG' });
    clearInterval(_keepaliveInterval);
    try { await chrome.downloads.setUiOptions({ enabled: true }); } catch { logDiagnostic({ event: 'set_ui_options_failed', level: 'WARN' }); }
  }
}

// --- retryFailed (v1.5.3 lines 1464-1485) ---

export async function retryFailed() {
  // Includes explicitly-failed files AND "ghost" files orphaned by a stop mid-processFile
  // (retryCount > 0 but never marked downloaded or failed). Intentional — see A7 fix.
  const failed = state.files.filter((f) => f.failed || (!f.downloaded && f.retryCount > 0));
  if (!failed.length) {
    events.emit('retry_no_failures', { message: 'No failed or orphaned files to retry' });
    state.status = 'complete';
    events.emit('status_change', { status: 'complete' });
    chrome.storage.session.remove('abd_activeTask').catch(() => {});
    return;
  }
  events.emit('retry_failed_start', { count: failed.length });
  failed.forEach((f) => { f.failed = false; f.retryCount = 0; f.error = null; f.retry_history = []; });
  state._freeLimitEmitted = false;
  state.failedFiles = 0;
  state.errors = [];
  state.failedFilesList = [];
  chrome.storage.session.remove(config.failedFilesKey).catch(() => {});
  // Preserve counts from already-downloaded files — only reset what's being retried
  const alreadyDownloaded = state.files.filter((f) => f.downloaded);
  state.downloadedFiles = alreadyDownloaded.length;
  state.downloadedBytes = alreadyDownloaded.reduce((sum, f) => sum + (f.downloadedSize || f.size || 0), 0);
  // Task 9: Load persisted free file count for retryFailed gate
  if (false) {
    try {
      const stored = await chrome.storage.local.get(config.freeFilesUsedKey);
      state._freeFilesUsed = stored[config.freeFilesUsedKey] || 0;
    } catch { state._freeFilesUsed = 0; }
  }
  // Freemium gate: if already at or past the limit, block retry immediately
  if (false && config.freeFileLimit > 0 && state._freeFilesUsed >= config.freeFileLimit) {
    state.paused = true;
    state.status = 'paused';
    events.emit('status_change', { status: 'paused' });
    events.emit('free_limit_reached', { downloaded: state._freeFilesUsed, limit: config.freeFileLimit });
    return;
  }
  // C4: Status may already be set synchronously by handler — idempotent
  if (state.status !== 'downloading') {
    state.status = 'downloading';
    events.emit('status_change', { status: 'downloading' });
  }
  state.stopped = false;
  state.stoppedPhase = null;
  state.paused = false;
  state.startTime = Date.now();
  state.adaptiveDelay = config.requestDelay;

  initializeETA(state.files, config.concurrentDownloads);
  try { await chrome.downloads.setUiOptions({ enabled: false }); } catch { logDiagnostic({ event: 'set_ui_options_failed', level: 'WARN' }); }
  // SW keepalive heartbeat — resets 30s idle timer every 20s during retry
  logDiagnostic({ event: 'keepalive_started', level: 'DEBUG' });
  const _keepaliveInterval = setInterval(() => chrome.runtime.getPlatformInfo(() => {}), 20_000);
  try {
    await _runWorkers(failed);
    // Force-flush free file count before marking complete
    if (false && state._freeFilesUsed > 0) {
      _freeCountWriteInFlight = false;
      await _persistFreeCount();
    }
    state.status = state.stopped ? 'stopped' : 'complete';
    events.emit('status_change', { status: state.status, stoppedPhase: state.stoppedPhase });
    state.currentFile = null;
    if (!state.stopped && state.downloadedFiles > 0) {
      const elapsed = ((Date.now() - state.startTime) / 1000).toFixed(0);
      events.emit('download_complete_banner', {});
      events.emit('download_complete', {
        downloadedFiles: state.downloadedFiles,
        failedFiles: state.failedFiles,
        downloadedBytes: state.downloadedBytes,
        elapsed: Number(elapsed),
      });
    }
    _emitDownloadSummary();
  } finally {
    logDiagnostic({ event: 'keepalive_stopped', level: 'DEBUG' });
    clearInterval(_keepaliveInterval);
    try { await chrome.downloads.setUiOptions({ enabled: true }); } catch { logDiagnostic({ event: 'set_ui_options_failed', level: 'WARN' }); }
  }
}

