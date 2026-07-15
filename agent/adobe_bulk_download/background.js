// background.js — Service worker (MV3, ES module).

import { events, formatEventForUI } from './events.js';
import { config } from './config.js';
import { state, saveProgress, loadProgress, resetState, waitForResume } from './state.js';
import { getToken, setToken, clearToken, restoreToken, checkTokenExpiry } from './token.js';
import { scanAll, listFolder, initialize, scanFolder } from './scanner.js';
import { fetchWithRetry, sleep } from './api.js';
import { downloadAll, retryFailed, saveFile, saveFileByUrl, downloadRegularFile, downloadPSDC, convertAIC, downloadAIC, processFile, cleanupBlobUrls, clearConversionJobs, reconcileActiveDownloads } from './downloads.js';
import { initializeETA, onFileSuccess, onFileFail, getDisplayData, serializeState as serializeETA, restoreState as restoreETA, resetETA, classifyFile } from './eta.js';
import { logDiagnostic, getDiagnostics, clearDiagnostics, _flushBatch, EVENT_LEVELS, LEVELS, sweepExpiredEntries, injectSessionMarker } from './diagnostics.js';
import {
  isPaid, loadLicense, setLicense,
  _resetCache as _resetLicenseCache,
  verifyLicenseWithServer,
  getOrCreateUserId,
  getOrResolveEmail, setEmail, getEmail,
  getOrResolveGaiaId,
} from './license.js';
import { trackEvent, _resetSessionCache } from './analytics.js';

// Global error handlers for SW-level visibility
self.addEventListener('unhandledrejection', (event) => {
  events.emit('unhandled_error', {
    error: event.reason?.message || String(event.reason),
    stack: event.reason?.stack || null,
  });
});
self.addEventListener('error', (event) => {
  events.emit('unhandled_error', {
    error: event.message || 'Unknown error',
    filename: event.filename || null,
    lineno: event.lineno || null,
  });
});

// Browser start: sweep expired diagnostic entries and inject session marker
chrome.runtime.onStartup.addListener(() => {
  sweepExpiredEntries()
    .then((deleted) => {
      if (deleted > 0) console.log(`[ABD] Swept ${deleted} expired diagnostic entries`);
      injectSessionMarker();
    })
    .catch(() => { injectSessionMarker(); });
});

// Status classification for alarm and badge management
const ACTIVE_STATUSES = new Set(['scanning', 'downloading', 'interrupted', 'paused']);
const TERMINAL_STATUSES = new Set(['idle', 'complete', 'stopped', 'error', 'scanned']);
const CONTROL_COMMANDS = new Set([
  'START_SCAN', 'START_DOWNLOAD', 'STOP_SCAN', 'STOP_DOWNLOAD',
  'PAUSE_DOWNLOAD', 'RESUME_DOWNLOAD', 'RETRY_FAILED', 'SET_CONFIG', 'FLUSH_DIAGNOSTICS',
  'CHECK_LICENSE', 'ACTIVATE_LICENSE', 'GET_EMAIL', 'SET_EMAIL', 'GET_USER_ID',
]);

// Expose module exports on self so Playwright serviceWorker.evaluate() can
// reach them (dynamic import() is disallowed in service workers).
// Not a public API — test and devtools use only.
// Guarded: only available for unpacked/dev extensions (update_url is undefined).
// SECURITY: CWS-published extensions always have update_url injected by Chrome.
// This guard ensures self.abd is only exposed for unpacked/developer-loaded extensions.
if (!chrome.runtime.getManifest().update_url) {
  self.abd = {
    events, formatEventForUI, config, state, saveProgress, loadProgress, resetState,
    getToken, setToken, clearToken, restoreToken, checkTokenExpiry, waitForResume,
    scanAll, listFolder, initialize, scanFolder, fetchWithRetry, sleep,
    downloadAll, retryFailed, saveFile, saveFileByUrl, downloadRegularFile, downloadPSDC, convertAIC, downloadAIC, processFile, cleanupBlobUrls, clearConversionJobs, reconcileActiveDownloads,
    initializeETA, onFileSuccess, onFileFail, getDisplayData, serializeETA, restoreETA, resetETA, classifyFile,
    logDiagnostic, getDiagnostics, clearDiagnostics, _flushBatch, EVENT_LEVELS, LEVELS, sweepExpiredEntries, injectSessionMarker,
    isPaid, loadLicense, setLicense, _resetLicenseCache, verifyLicenseWithServer, getOrCreateUserId,
    getOrResolveEmail, setEmail, getEmail, getOrResolveGaiaId,
    trackEvent, _resetSessionCache,
    _resetExternalVerifyTimer: () => { _lastExternalVerify = 0; },
    get _startupReady() { return _startupReady; },
    _setHadTokenBefore: (v) => { _hadTokenBefore = !!v; },
  };
}

// Track whether a token was ever accepted during this extension's lifetime
let _hadTokenBefore = false;

// Re-inject content script into already-open Adobe tabs on install/update
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason !== 'install' && details.reason !== 'update') return;
  chrome.tabs.query({ url: 'https://*.adobe.com/*', discarded: false }).then((tabs) => {
    for (const tab of tabs) {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js'],
      }).catch(() => {}); // Tab may be restricted or navigating
    }
  }).catch(() => {});
  logDiagnostic({ event: 'oninstalled_content_inject', level: 'INFO', data: { reason: details.reason } });
});

// --- SW recovery: restore token and detect interrupted tasks on every wake ---
const _startupReady = (async () => {
  // Clean up orphaned alarms BEFORE restoreToken — restoreToken → setToken →
  // _scheduleExpiryAlarm will re-create the expiry alarm if the token is valid.
  chrome.alarms.clear(config.resumePollAlarmName);
  chrome.alarms.clear(config.expiryCheckAlarmName);

  // Clean up stale resume persistence keys from a previous SW lifecycle
  chrome.storage.session.remove([config.resumePromptKey, config.resumeAnswerKey]).catch(() => {});

  // Cache abd_hasToken for three-state token badge ("Sign in" vs "Reload tab")
  const htData = await chrome.storage.local.get('abd_hasToken');
  _hadTokenBefore = !!htData.abd_hasToken;

  await restoreToken();
  await loadLicense();
  await getOrResolveEmail(); // Pre-cache email for license checks
  await getOrResolveGaiaId(); // Pre-cache Gaia ID for license recovery
  await verifyLicenseWithServer(); // Restore license on reinstall; TTL guard throttles repeat wakes
  // Ensure license revalidation alarm exists (may be cleared on browser restart)
  const licAlarm = await chrome.alarms.get(config.licenseVerifyAlarmName);
  if (!licAlarm) {
    chrome.alarms.create(config.licenseVerifyAlarmName, { periodInMinutes: config.licenseVerifyTtlMs / 60000 })
      .catch((e) => logDiagnostic({ event: 'license_alarm_create_error', level: 'WARN', data: { error: e?.message } }));
  }
  await updateUninstallURL(); // Must run after email resolves so email param is populated
  if (getToken()) {
    logDiagnostic({ event: 'sw_wake_token_restored', level: 'INFO' });
    console.log('[ABD background] Token restored from session storage');
  } else {
    logDiagnostic({ event: 'sw_wake_no_token', level: 'WARN' });
  }

  // P2: reconcile downloads that outlived a SW death (size-validate retroactively,
  // clean up truncated/interrupted ones, merge failures into abd_failed_files).
  // Runs BEFORE the task-recovery block: the failed-files restore below re-reads the
  // merged list, and auto-resume can't start new downloads until after this settles.
  try {
    await reconcileActiveDownloads();
  } catch (e) {
    logDiagnostic({ event: 'active_download_sweep_failed', level: 'WARN', data: { error: e?.message } });
  }

  // Check for interrupted task from a previous SW lifecycle
  try {
    const data = await chrome.storage.session.get(config.activeTaskKey);
    const task = data?.[config.activeTaskKey];
    if (task) {
      if (task.type === 'scan') {
        // Scan state is not resumable — user re-scans manually
        await chrome.storage.session.remove(config.activeTaskKey);
        clearConversionJobs();
        events.emit('sw_recovery', { action: 'cleared_stale_scan', task });
      } else if (task.type === 'download' && getToken()) {
        // Leave conversion jobs intact so downloadPSDC/convertAIC can recover in-flight conversions on resume
        // Restore failed files list from session storage
        try {
          const failedData = await chrome.storage.session.get(config.failedFilesKey);
          const rawFailed = failedData?.[config.failedFilesKey];
          if (Array.isArray(rawFailed) && rawFailed.length > 0) {
            state.failedFilesList = rawFailed.slice(0, 500);
          }
        } catch { logDiagnostic({ event: 'failed_list_restore_failed', level: 'WARN' }); }

        // Restore scan context (repositoryId, storageRegion, platformBaseUrl)
        try {
          const ctxData = await chrome.storage.session.get(config.scanContextKey);
          const ctx = ctxData?.[config.scanContextKey];
          if (ctx) {
            state.repositoryId = ctx.repositoryId;
            state.storageRegion = ctx.storageRegion;
            state.platformBaseUrl = ctx.platformBaseUrl;
          }
        } catch (e) {
          logDiagnostic({ event: 'scan_context_restore_failed', level: 'WARN', data: { error: e?.message } });
        }

        // Restore files list from session storage
        try {
          const filesData = await chrome.storage.session.get(config.filesListKey);
          const files = filesData?.[config.filesListKey];
          if (Array.isArray(files) && files.length > 0) {
            state.files = files;
            state.totalFiles = files.length;
            // Mark already-downloaded files using persisted progress
            const progress = await loadProgress();
            if (progress?.downloadedIds) {
              const done = new Set(progress.downloadedIds);
              let restoredCount = 0;
              state.files.forEach(f => {
                if (done.has(f.assetId)) {
                  f.downloaded = true;
                  restoredCount++;
                }
              });
              state.downloadedFiles = restoredCount;
            }
            logDiagnostic({ event: 'files_restored', level: 'INFO', data: { total: files.length, downloaded: state.downloadedFiles } });
          }
        } catch (e) {
          logDiagnostic({ event: 'files_restore_failed', level: 'WARN', data: { error: e?.message } });
        }

        // Auto-resume if files were restored and recovery limit not exceeded
        if (state.files.length > 0 && getToken()) {
          try {
            const countData = await chrome.storage.session.get(config.recoveryCountKey);
            const recoveryCount = (countData?.[config.recoveryCountKey] || 0) + 1;
            await chrome.storage.session.set({ [config.recoveryCountKey]: recoveryCount });

            if (recoveryCount <= config.maxAutoRecoveries) {
              logDiagnostic({ event: 'sw_recovery_auto_resume', level: 'INFO', data: { attempt: recoveryCount, files: state.files.length, downloaded: state.downloadedFiles } });
              state.status = 'downloading';
              events.emit('status_change', { status: 'downloading' });
              chrome.storage.session.set({ [config.activeTaskKey]: { type: 'download', timestamp: Date.now() } });
              downloadAll({ fromRecovery: true }).catch(e => console.error('[ABD] Recovery downloadAll error:', e));
            } else {
              logDiagnostic({ event: 'sw_recovery_limit_reached', level: 'WARN', data: { attempts: recoveryCount } });
              state.status = 'interrupted';
              events.emit('sw_recovery', { action: 'download_interrupted', task });
              events.emit('status_change', { status: 'interrupted' });
            }
          } catch (e) {
            state.status = 'interrupted';
            events.emit('sw_recovery', { action: 'download_interrupted', task });
            events.emit('status_change', { status: 'interrupted' });
          }
        } else {
          state.status = 'interrupted';
          events.emit('sw_recovery', { action: 'download_interrupted', task });
          events.emit('status_change', { status: 'interrupted' });
        }
      } else {
        await chrome.storage.session.remove(config.activeTaskKey);
        clearConversionJobs();
        events.emit('sw_recovery', { action: 'cleared_stale_task', task });
      }
    } else {
      // No active task — clean up any orphaned conversion job data
      logDiagnostic({ event: 'sw_wake_clean', level: 'DEBUG' });
      clearConversionJobs();
    }
  } catch (e) {
    console.warn('[ABD background] SW recovery check failed:', e.message);
    logDiagnostic({ event: 'sw_recovery_failed', level: 'ERROR', data: { error: e?.message } });
  }

  // Capability & environment detection
  const capabilities = {
    setUiOptions: typeof chrome.downloads?.setUiOptions === 'function',
    getContexts: typeof chrome.runtime?.getContexts === 'function',
    chromeVersion: /Chrome\/(\d+)/.exec(navigator.userAgent)?.[1] || 'unknown',
    extensionVersion: chrome.runtime.getManifest().version,
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    sessionStorageQuota: null,
  };
  try {
    const bytes = await chrome.storage.session.getBytesInUse(null);
    const SESSION_STORAGE_LIMIT = 10_485_760; // 10 MB — chrome.storage.session quota
    capabilities.sessionStorageQuota = { used: bytes, limit: SESSION_STORAGE_LIMIT };
  } catch (e) { logDiagnostic({ event: 'storage_bytes_check_failed', level: 'WARN', data: { error: e?.message } }); }
  await chrome.storage.session.set({ [config.capabilitiesKey]: capabilities });
  logDiagnostic({ event: 'capabilities_detected', level: 'INFO', data: capabilities });
  console.log('[ABD] Capabilities:', capabilities);
})();

// --- Event consumers ---

// Consumer 1: Broadcast every event to sidepanel via chrome.runtime.sendMessage.
// If no sidepanel is open the send will fail — that's expected, so we swallow the error.
events.register((entry) => {
  chrome.runtime.sendMessage({ type: 'ABD_EVENT', entry }).catch(() => {});
});

// Consumer 2: Log errors to the service worker console (DevTools visibility).
events.register((entry) => {
  const formatted = formatEventForUI(entry, config);
  if (formatted?.type === 'error') {
    console.error('[ABD]', formatted.message);
  }
});

// Consumer 3: Feed file completion events to ETA calculator.
events.register((entry) => {
  try {
    if (entry.event === 'file_success') onFileSuccess(entry);
    else if (entry.event === 'file_fail') onFileFail(entry);
  } catch (e) {
    console.error('[ABD background] ETA update error:', e, entry);
  }
});

// Consumer 4: Badge text — percentage during downloads, "Scan" during scanning, blank when idle.
// Priority flag: expiry warning badge takes precedence over eta_update percentage.
let _expiryBadgeActive = false;

events.register((entry) => {
  if (entry.event === 'eta_update' && Number.isFinite(entry.percent) && !_expiryBadgeActive) {
    chrome.action.setBadgeText({ text: `${Math.max(0, Math.floor(entry.percent))}%` });
    chrome.action.setBadgeBackgroundColor({ color: '#1473E6' });
  }
  if (entry.event === 'status_change') {
    if (entry.status === 'scanning') {
      chrome.action.setBadgeText({ text: 'Scan' });
      chrome.action.setBadgeBackgroundColor({ color: '#E68619' });
    }
    if (entry.status === 'interrupted') {
      chrome.action.setBadgeText({ text: '!' });
      chrome.action.setBadgeBackgroundColor({ color: '#D7373F' });
    }
    if (TERMINAL_STATUSES.has(entry.status)) {
      chrome.action.setBadgeText({ text: '' });
      _expiryBadgeActive = false;
    }
  }
  if (entry.event === 'token_expiry_warning') {
    _expiryBadgeActive = true;
    chrome.action.setBadgeText({ text: 'Exp!' });
    chrome.action.setBadgeBackgroundColor({ color: '#E68619' });
  }
  if (entry.event === 'token_expired') {
    _expiryBadgeActive = false;
    chrome.action.setBadgeText({ text: 'Exp' });
    chrome.action.setBadgeBackgroundColor({ color: '#D7373F' });
  }
  if (entry.event === 'token_accepted') {
    _expiryBadgeActive = false;
    chrome.action.setBadgeText({ text: '' });
  }
});

// Consumer 5: Notification on download complete.
events.register((entry) => {
  if (entry.event === 'download_complete_banner') {
    chrome.notifications.create('abd-complete', {
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: 'Download Complete',
      message: `${state.downloadedFiles} files downloaded`,
    });
  }
});

// Consumer 6: Keepalive alarm — prevents SW termination during active work.
// Also persists/clears activeTask state for SW recovery.
events.register((entry) => {
  if (entry.event !== 'status_change') return;
  const active = ACTIVE_STATUSES.has(entry.status);
  const terminal = TERMINAL_STATUSES.has(entry.status);

  if (active) {
    chrome.alarms.create(config.keepaliveAlarmName, { periodInMinutes: 0.5 });
    console.debug('[ABD] keepalive started for status:', entry.status);
  } else if (terminal) {
    chrome.alarms.clear(config.keepaliveAlarmName);
    chrome.storage.session.remove(config.activeTaskKey).catch(() => {});
    // Preserve scan data on 'scanned' — user still needs files for download
    if (entry.status === 'scanned') {
      trackEvent('abd_scan_completed', { file_count: state.files.length });
    }
    if (entry.status !== 'scanned') {
      chrome.storage.session.remove(config.filesListKey).catch(() => {});
      chrome.storage.session.remove(config.scanContextKey).catch(() => {});
    }
    chrome.storage.session.remove([config.resumePromptKey, config.resumeAnswerKey]).catch(() => {});
    chrome.storage.session.remove(config.recoveryCountKey).catch(() => {});
    cleanupBlobUrls();
    clearConversionJobs();
    console.debug('[ABD] keepalive stopped for status:', entry.status);
  }
});

// Consumer 7: Structured diagnostic logging — all events flow to the ring buffer with severity.
events.register((entry) => {
  const level = EVENT_LEVELS[entry.event] || 'DEBUG';
  const { event, timestamp, ...data } = entry;
  logDiagnostic({ event, level, data });
});

// --- chrome.alarms listener ---
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === config.keepaliveAlarmName) {
    // API call resets the 30s SW idle timer (event delivery alone is a race)
    chrome.runtime.getPlatformInfo(() => {});
  }
  if (alarm.name === config.expiryCheckAlarmName) {
    checkTokenExpiry();
  }
  if (alarm.name === config.licenseVerifyAlarmName) {
    _startupReady.then(() => verifyLicenseWithServer()).catch((e) =>
      logDiagnostic({ event: 'license_alarm_verify_error', level: 'WARN', data: { error: e?.message } })
    );
  }
});

// --- Token relay listener ---

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  _startupReady.then(() => {
    // Reject messages not from our own extension
    if (sender.id !== chrome.runtime.id) {
      sendResponse({ ok: false, reason: 'unauthorized' });
      return;
    }

    // H3: ABD_TOKEN requires sender.tab (content script in web page)
    if (message.type === 'ABD_TOKEN') {
      if (!sender.tab) {
        logDiagnostic({ event: 'token_rejected', level: 'WARN', data: { reason: 'no_tab' } });
        sendResponse({ ok: false, reason: 'must originate from content script' });
        return;
      }
      const senderUrl = sender.tab.url || sender.url || '';
      if (!senderUrl.startsWith('https://assets.adobe.com') &&
          !senderUrl.startsWith('https://www.adobe.com') &&
          !senderUrl.startsWith('https://adobe.com') &&
          !senderUrl.startsWith('https://acrobat.adobe.com')) {
        logDiagnostic({ event: 'token_rejected', level: 'WARN', data: { reason: 'wrong_origin', origin: senderUrl } });
        sendResponse({ ok: false, reason: 'token must originate from Adobe domain' });
        return;
      }
      if (!message.token) {
        logDiagnostic({ event: 'token_rejected', level: 'WARN', data: { reason: 'empty' } });
        sendResponse({ ok: false, reason: 'missing token' });
        return;
      }
      const prevToken = getToken();
      const accepted = setToken(message.token, message.expiry);
      if (!accepted) {
        logDiagnostic({ event: 'token_rejected', level: 'WARN', data: { reason: 'validation_failed' } });
        sendResponse({ ok: false, reason: 'token validation failed' });
        return;
      }

      // Skip side effects on unchanged tokens: content.js polls every 1s and re-sends
      // the same token. Without this gate, a 30-minute session writes ~1,000 no-op
      // diagnostic entries, storage.local writes, and sidepanel broadcasts.
      if (prevToken !== message.token) {
        logDiagnostic({ event: 'token_cached', level: 'INFO', data: { expiry: message.expiry || null } });
        events.emit('token_accepted', {});
        _hadTokenBefore = true;
        chrome.storage.local.set({ abd_hasToken: true }).catch(() => {});
      }

      try {
        sendResponse({ ok: true });
      } catch { logDiagnostic({ event: 'send_response_failed', level: 'DEBUG' }); }
      return;
    }

    // H3: Control commands require extension-origin sender.url (undefined → rejected)
    if (CONTROL_COMMANDS.has(message.type)) {
      const extOrigin = `chrome-extension://${chrome.runtime.id}/`;
      if (!sender.url?.startsWith(extOrigin)) {
        sendResponse({ ok: false, reason: 'control commands require extension origin' });
        return;
      }
    }

    if (message.type === 'START_SCAN') {
      if (!getToken()) {
        sendResponse({ ok: false, reason: 'no_token' });
        return;
      }
      if (ACTIVE_STATUSES.has(state.status)) {
        sendResponse({ ok: false, reason: `cannot scan while ${state.status}` });
        return;
      }
      // C4: Set status synchronously before async work
      state.status = 'scanning';
      events.emit('status_change', { status: 'scanning' });
      chrome.storage.session.set({ [config.activeTaskKey]: { type: 'scan', timestamp: Date.now() } });
      trackEvent('abd_scan_started');
      // scanAll() calls resetState() internally, which clears stopped/paused
      scanAll().catch((e) => { console.error('[ABD background] scanAll error:', e); logDiagnostic({ event: 'toplevel_scan_error', level: 'ERROR', data: { error: e?.message } }); });
      sendResponse({ ok: true });
    } else if (message.type === 'STOP_SCAN' || message.type === 'STOP_DOWNLOAD') {
      if (state.status === 'idle' || state.status === 'complete' || state.status === 'error') {
        sendResponse({ ok: true });
      } else if (!state.stopped) {
        state.stopped = true;
        state.stoppedPhase = (state.status === 'downloading' || state.status === 'paused' || state.status === 'interrupted') ? 'downloading' : 'scanning';
        state.paused = false;
        events.emit('user_stop', { stoppedPhase: state.stoppedPhase });
        sendResponse({ ok: true });
      } else {
        sendResponse({ ok: true });
      }
    } else if (message.type === 'START_DOWNLOAD') {
      if (!getToken()) {
        sendResponse({ ok: false, reason: 'no_token' });
        return;
      }
      if (state.status === 'downloading') {
        sendResponse({ ok: false, reason: 'already downloading' });
        return;
      }
      // C4: Set status synchronously before async work
      state.status = 'downloading';
      events.emit('status_change', { status: 'downloading' });
      chrome.storage.session.set({ [config.activeTaskKey]: { type: 'download', timestamp: Date.now() } });

      // If SW was terminated after scan, restore files from session storage
      const launch = () => {
        downloadAll().catch((e) => { console.error('[ABD background] downloadAll error:', e); logDiagnostic({ event: 'toplevel_download_error', level: 'ERROR', data: { error: e?.message } }); });
      };
      if (!state.files || state.files.length === 0) {
        _restoreFilesForDownload().then(launch).catch(launch);
      } else {
        launch();
      }
      sendResponse({ ok: true });
    } else if (message.type === 'PAUSE_DOWNLOAD') {
      state.paused = true;
      state.status = 'paused';
      events.emit('status_change', { status: 'paused' });
      events.emit('user_pause', {});
      sendResponse({ ok: true });
    } else if (message.type === 'RESUME_DOWNLOAD') {
      if (state.paused) {
        state.paused = false;
        state.status = 'downloading';
        events.emit('status_change', { status: 'downloading' });
        events.emit('user_resume', {});
      } else if (state.status === 'interrupted' && state.files.length > 0) {
        // Manual recovery: reset counter and re-launch
        chrome.storage.session.set({ [config.recoveryCountKey]: 0 });
        state.status = 'downloading';
        events.emit('status_change', { status: 'downloading' });
        chrome.storage.session.set({ [config.activeTaskKey]: { type: 'download', timestamp: Date.now() } });
        downloadAll({ fromRecovery: true }).catch(e => { console.error('[ABD] Manual recovery downloadAll error:', e); logDiagnostic({ event: 'toplevel_download_error', level: 'ERROR', data: { error: e?.message } }); });
      }
      sendResponse({ ok: true });
    } else if (message.type === 'RETRY_FAILED') {
      if (!getToken()) {
        sendResponse({ ok: false, reason: 'no_token' });
        return;
      }
      if (state.status === 'downloading') {
        sendResponse({ ok: false, reason: 'download already in progress' });
        return;
      }
      // C4: Set status synchronously before async work
      state.status = 'downloading';
      events.emit('status_change', { status: 'downloading' });
      chrome.storage.session.set({ [config.activeTaskKey]: { type: 'download', timestamp: Date.now() } });
      retryFailed().catch((e) => { console.error('[ABD background] retryFailed error:', e); logDiagnostic({ event: 'toplevel_retry_error', level: 'ERROR', data: { error: e?.message } }); });
      sendResponse({ ok: true });
    } else if (message.type === 'FLUSH_DIAGNOSTICS') {
      _flushBatch().then(() => sendResponse({ ok: true })).catch(() => sendResponse({ ok: false }));
    } else if (message.type === 'SET_CONFIG') {
      if (message.concurrency != null) {
        const val = Number(message.concurrency);
        if (Number.isFinite(val)) {
          config.concurrentDownloads = Math.max(1, Math.min(10, Math.round(val)));
        }
      }
      if (message.subfolder != null) {
        const rawSubfolder = String(message.subfolder).trim().replace(/[/\\]/g, '').replace(/[\x00-\x1f]/g, '').replace(/^\.+$/, '').slice(0, 100);
        const RESERVED_SF = /^(CON|PRN|AUX|NUL|COM\d|LPT\d)(\.|$)/i;
        config.downloadSubfolder = RESERVED_SF.test(rawSubfolder) ? '_' + rawSubfolder : rawSubfolder;
      }
      if (message.diagnosticLevel != null) {
        const valid = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
        const lvl = String(message.diagnosticLevel).toUpperCase();
        if (valid.includes(lvl)) {
          config.diagnosticLevel = lvl;
        }
      }
      logDiagnostic({ event: 'config_applied', level: 'INFO', data: { concurrency: config.concurrentDownloads, subfolder: config.downloadSubfolder, diagnosticLevel: config.diagnosticLevel } });
      sendResponse({ ok: true });
    } else if (message.type === 'GET_EMAIL') {
      getOrResolveEmail().then((email) => {
        logDiagnostic({ event: 'msg_get_email', level: 'DEBUG', data: { hasEmail: !!email } });
        sendResponse({ ok: true, email });
      }).catch(() => {
        logDiagnostic({ event: 'msg_get_email_error', level: 'WARN', data: {} });
        sendResponse({ ok: false, email: null });
      });
    } else if (message.type === 'SET_EMAIL') {
      const email = typeof message.email === 'string' ? message.email.trim().toLowerCase() : '';
      if (!email) {
        logDiagnostic({ event: 'msg_set_email', level: 'WARN', data: { rejected: 'empty' } });
        sendResponse({ ok: false, reason: 'empty email' });
      } else {
        const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!EMAIL_RE.test(email) || email.length > 200) {
          logDiagnostic({ event: 'msg_set_email', level: 'WARN', data: { rejected: 'invalid_email' } });
          sendResponse({ ok: false, reason: 'invalid_email' });
        } else {
          setEmail(email).then(() => {
            logDiagnostic({ event: 'msg_set_email', level: 'INFO', data: { ok: true } });
            sendResponse({ ok: true });
          }).catch((e) => {
            logDiagnostic({ event: 'msg_set_email_error', level: 'ERROR', data: { error: e.message } });
            sendResponse({ ok: false, reason: e.message });
          });
        }
      }
    } else if (message.type === 'TRACK_EVENT') {
      trackEvent(message.name, message.params || {});
      sendResponse({ ok: true });
      return;
    } else if (message.type === 'GET_USER_ID') {
      Promise.all([getOrCreateUserId(), getOrResolveGaiaId()]).then(([uid, gaiaId]) => {
        logDiagnostic({ event: 'msg_get_userid', level: 'DEBUG', data: { ok: true } });
        sendResponse({ ok: true, uid, gaiaId });
      }).catch(() => {
        logDiagnostic({ event: 'msg_get_userid_error', level: 'WARN', data: {} });
        sendResponse({ ok: false, uid: '', gaiaId: null });
      });
    } else if (message.type === 'CHECK_LICENSE') {
      loadLicense().then((paid) => {
        logDiagnostic({ event: 'msg_check_license', level: 'INFO', data: { paid } });
        sendResponse({ ok: true, paid });
      }).catch(() => {
        logDiagnostic({ event: 'msg_check_license_error', level: 'WARN', data: {} });
        sendResponse({ ok: false, paid: false });
      });
    } else if (message.type === 'ACTIVATE_LICENSE') {
      verifyLicenseWithServer({ force: true }).then((paid) => {
        logDiagnostic({ event: 'msg_activate_license', level: 'INFO', data: { paid } });
        if (paid) {
          chrome.storage.session.get(config.upgradePendingKey).then((data) => {
            if (data?.[config.upgradePendingKey]) {
              chrome.storage.session.remove(config.upgradePendingKey).catch(() => {});
              trackEvent('abd_license_activated');
            }
          }).catch(() => {});
          events.emit('license_activated', {});
          updateUninstallURL();
        }
        sendResponse({ ok: true, paid });
      }).catch((e) => {
        logDiagnostic({ event: 'msg_activate_license_error', level: 'ERROR', data: { error: e.message } });
        sendResponse({ ok: false, reason: e.message });
      });
    } else {
      logDiagnostic({ event: 'unknown_message', level: 'DEBUG', data: { type: message.type } });
      sendResponse({ ok: false, reason: 'unknown message type' });
    }
  }).catch((err) => {
    sendResponse({ ok: false, reason: 'startup_failed' });
  });
  // Return true to keep the message channel open for async sendResponse
  return true;
});

// --- Post-payment license detection via success page ---
let _lastExternalVerify = 0;
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  _startupReady.then(() => {
    if (message?.type !== 'PAYMENT_COMPLETE') {
      sendResponse({ ok: false });
      return;
    }
    // Validate sender is our site
    const senderOrigin = sender.origin || '';
    if (senderOrigin !== 'https://saltydalton.com') {
      logDiagnostic({ event: 'external_message_rejected', level: 'WARN', data: { origin: senderOrigin } });
      sendResponse({ ok: false });
      return;
    }
    const now = Date.now();
    if (now - _lastExternalVerify < 5000) {
      sendResponse({ ok: false, reason: 'rate_limited' });
      return;
    }
    _lastExternalVerify = now;
    logDiagnostic({ event: 'payment_complete_received', level: 'INFO', data: {} });
    verifyLicenseWithServer({ force: true }).then((paid) => {
      if (paid) {
        chrome.storage.session.get(config.upgradePendingKey).then((data) => {
          if (data?.[config.upgradePendingKey]) {
            chrome.storage.session.remove(config.upgradePendingKey).catch(() => {});
            trackEvent('abd_license_activated');
          }
        }).catch(() => {});
        events.emit('license_activated', {});
        updateUninstallURL();
        logDiagnostic({ event: 'license_post_payment_activated', level: 'INFO', data: { trigger: 'success_page' } });
      }
      sendResponse({ ok: true, paid });
    }).catch(() => {
      sendResponse({ ok: false });
    });
  }).catch((err) => {
    sendResponse({ ok: false, reason: 'startup_failed' });
  });
  return true; // keep channel open for async sendResponse
});

// --- Side panel connection listener ---

chrome.runtime.onConnect.addListener((port) => {
  if (port.name === 'sidepanel') {
    if (port.sender?.id !== chrome.runtime.id ||
        !port.sender?.url?.startsWith(`chrome-extension://${chrome.runtime.id}/sidepanel.html`)) {
      logDiagnostic({ event: 'sidepanel_origin_rejected', level: 'WARN', data: { origin: port.sender?.url } });
      port.disconnect();
      return;
    }
    console.log('[ABD background] Side panel connected');

    // NOTE: this listener is NOT async (and must not become async — see onMessage).
    // Gate the GET_STATE reply on _startupReady via .then() so a panel that connects
    // during an SW cold start receives hasToken AFTER restoreToken() resolves, rather
    // than an early hasToken:false that latches "Sign in to Adobe" forever. Mirrors the
    // onMessage handler's _startupReady.then() gate. Port handlers have no
    // sendResponse-return-true contract, so deferring postMessage is safe.
    port.onMessage.addListener((msg) => {
      if (msg.type === 'GET_STATE') {
        _startupReady.then(() => {
          try {
            port.postMessage({
              type: 'STATE',
              status: state.status,
              totalFiles: state.totalFiles,
              downloadedFiles: state.downloadedFiles,
              failedFiles: state.failedFiles,
              downloadedBytes: state.downloadedBytes,
              totalBytes: state.totalBytes,
              startTime: state.startTime,
              hasToken: !!getToken(),
              hadTokenBefore: _hadTokenBefore,
              failedFilesList: state.failedFilesList || [],
              eta: state.status === 'downloading' ? getDisplayData() : null,
              workerCount: state.status === 'downloading' ? config.concurrentDownloads : 0,
              stoppedPhase: state.stoppedPhase,
              isPaid: isPaid(),
            });
          } catch { logDiagnostic({ event: 'port_message_failed', level: 'DEBUG' }); }
        }).catch(() => { /* startup failed; panel will retry on reconnect */ });
      }
    });

    port.onDisconnect.addListener(() => {
      console.log('[ABD background] Side panel disconnected');
    });
  }
});

// --- Initialization ---

chrome.runtime.onInstalled.addListener((details) => {
  chrome.storage.local.set({ abd_installed: true });
  console.log('[ABD background] Extension installed');
  if (details.reason === 'install') {
    trackEvent('abd_install');
  }
});

// Enable side panel on action click
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
  .catch((err) => console.warn('[ABD background] sidePanel error:', err));

// Build uninstall URL with dynamic params (version, userId, paid status).
// Called on startup and whenever license status changes.
async function updateUninstallURL() {
  try {
    const userId = await getOrCreateUserId();
    const paid = isPaid() ? '1' : '0';
    const params = new URLSearchParams({
      v: chrome.runtime.getManifest().version,
      uid: userId,
      paid,
    });
    chrome.runtime.setUninstallURL(`${config.uninstallSurveyUrl}?${params}`);
    logDiagnostic({ event: 'uninstall_url_updated', level: 'DEBUG', data: { paid } });
  } catch {
    logDiagnostic({ event: 'uninstall_url_error', level: 'WARN', data: {} });
    chrome.runtime.setUninstallURL(config.uninstallSurveyUrl);
  }
}

// Restore scanned files from session storage (used when SW was terminated after scan)
async function _restoreFilesForDownload() {
  const filesData = await chrome.storage.session.get(config.filesListKey);
  const files = filesData?.[config.filesListKey];
  if (Array.isArray(files) && files.length > 0) {
    state.files = files;
    state.totalFiles = files.length;
    logDiagnostic({ event: 'files_restored_for_download', level: 'INFO', data: { count: files.length } });
  }
  const ctxData = await chrome.storage.session.get(config.scanContextKey);
  const ctx = ctxData?.[config.scanContextKey];
  if (ctx) {
    state.repositoryId = ctx.repositoryId;
    state.storageRegion = ctx.storageRegion;
    state.platformBaseUrl = ctx.platformBaseUrl;
  }
}

// --- Helpers ---
