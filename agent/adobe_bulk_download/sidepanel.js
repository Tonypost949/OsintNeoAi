// sidepanel.js — Side panel UI logic (ES module, Phase 3B).

import { formatEventForUI, formatBytes, friendlyCategory } from './events.js';
import { logDiagnostic } from './diagnostics.js';
import { getAll as getAllDiagEntries } from './diag-store.js';
import { config } from './config.js';

// --- DOM refs ---
const logArea = document.getElementById('log-area');
const logHeader = document.getElementById('log-header');
const fileCount = document.getElementById('file-count');
const progressBar = document.getElementById('progress-bar');
const phaseLabel = document.getElementById('phase-label');
const etaLabel = document.getElementById('eta-label');
const statData = document.getElementById('stat-data');
const statSpeed = document.getElementById('stat-speed');
const heroErrorCount = document.getElementById('hero-error-count');
const tokenBadge = document.getElementById('token-badge');
const resumeDialog = document.getElementById('resume-dialog');
const resumeMessage = document.getElementById('resume-message');
const concurrencySelect = document.getElementById('concurrency-select');
const themeSelect = document.getElementById('theme-select');
const failedFilesSection = document.getElementById('failed-files');
const failedList = document.getElementById('failed-list');
const failedCount = document.getElementById('failed-count');
const subfolderInput = document.getElementById('subfolder-input');
const diagLevelSelect = document.getElementById('diag-level-select');

// --- Local state ---
let totalFiles = 0;
let downloadedFiles = 0;
let failedFiles = 0;
let downloadedBytes = 0;
let startTime = null;
let pendingResumeResponse = null;
let _persistedResumePromptActive = false;
let _failedFilesList = [];
let _failedFilesCount = 0;
let _atFreeLimit = false;
let _isPaid = false;
// Set false right before each GET_STATE; set true when a status_change live event
// is applied. Used to prevent a late STATE snapshot (cold-SW deferred reply) from
// regressing a status already learned from a fresher live event. See connectPort()
// and the STATE branch of _handlePortMessage().
let _statusEventSinceGetState = false;

// --- rAF throttle for strip updates ---
let _pendingWorkerUpdates = new Map();
let _stripRafScheduled = false;

function middleTruncate(str, maxLen = 20) {
  if (str.length <= maxLen) return str;
  const dotIdx = str.lastIndexOf('.');
  const ext = dotIdx > 0 ? str.slice(dotIdx) : '';
  const name = dotIdx > 0 ? str.slice(0, dotIdx) : str;
  const available = maxLen - ext.length - 1;
  if (available < 4) return str.slice(0, maxLen - 1) + '\u2026';
  const headLen = Math.ceil(available / 2);
  const tailLen = Math.floor(available / 2);
  return name.slice(0, headLen) + '\u2026' + name.slice(-tailLen) + ext;
}

function _flushStripUpdates() {
  _stripRafScheduled = false;
  const strip = document.getElementById('worker-strip');
  if (!strip) return;

  // Apply worker updates
  if (_pendingWorkerUpdates.size > 0) {
    for (const [workerId, update] of _pendingWorkerUpdates) {
      const row = strip.querySelector(`[data-worker="${workerId}"]`);
      if (row) {
        if (update.state === 'downloading') {
          row.textContent = '\u2193 ' + middleTruncate(update.fileName || '');
          row.title = update.fileName || '';
        } else if (update.state === 'done') {
          row.textContent = '\u2713 ' + middleTruncate(update.fileName || '');
          row.title = update.fileName || '';
        } else if (update.state === 'idle') {
          row.textContent = '\u2014 idle';
          row.title = '';
        }
      }
    }
    _pendingWorkerUpdates.clear();
  }
}

function _scheduleStripFlush() {
  if (!_stripRafScheduled) {
    _stripRafScheduled = true;
    requestAnimationFrame(_flushStripUpdates);
  }
}

function _renderFailedFile(entry) {
  const div = document.createElement('div');
  const nameSpan = document.createElement('span');
  nameSpan.className = 'fail-name';
  nameSpan.textContent = entry.name || entry.path?.split('/').pop() || 'Unknown';
  nameSpan.title = entry.path || '';
  const reasonSpan = document.createElement('span');
  reasonSpan.className = 'fail-reason';
  reasonSpan.textContent = friendlyCategory(entry.errorCategory);
  div.appendChild(nameSpan);
  div.appendChild(reasonSpan);
  return div;
}

function _updateFailedFilesUI() {
  failedCount.textContent = String(_failedFilesCount);
  failedFilesSection.hidden = _failedFilesCount === 0;
}

function _updateHeroErrorCount() {
  if (failedFiles > 0) {
    heroErrorCount.textContent = `${failedFiles} error${failedFiles !== 1 ? 's' : ''}`;
    heroErrorCount.hidden = false;
  } else {
    heroErrorCount.hidden = true;
  }
}

function _buildFeedbackUrl(errorContext) {
  const base = config.feedbackFormUrl;
  if (!base) return null;
  const fields = config.feedbackFormFields || {};
  const params = new URLSearchParams();
  const version = chrome.runtime.getManifest().version;
  const chromeVersion = /Chrome\/(\d+)/.exec(navigator.userAgent)?.[1] || 'unknown';
  const platform = navigator.platform || 'unknown';
  const license = _isPaid ? 'paid' : 'free';
  const map = {
    version: version,
    chrome: chromeVersion,
    platform: platform,
    license: license,
    errorContext: errorContext || '',
  };
  for (const [key, fieldId] of Object.entries(fields)) {
    if (!fieldId || fieldId.includes('REPLACE_')) continue;
    const val = map[key];
    if (val) params.set(fieldId, val);
  }
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

// --- Helpers ---

let _autoScroll = true;
logArea.addEventListener('scroll', () => {
  _autoScroll = logArea.scrollTop + logArea.clientHeight >= logArea.scrollHeight - 30;
}, { passive: true });

function log(text, level = 'info') {
  logHeader.hidden = false;
  logArea.hidden = false;
  const el = document.createElement('div');
  el.dataset.level = level;
  el.textContent = text;
  logArea.appendChild(el);
  while (logArea.children.length > 200) logArea.firstChild.remove();
  if (_autoScroll) logArea.scrollTop = logArea.scrollHeight;
}

function logRich(element, level = 'info') {
  logHeader.hidden = false;
  logArea.hidden = false;
  const el = document.createElement('div');
  el.dataset.level = level;
  el.appendChild(element);
  logArea.appendChild(el);
  while (logArea.children.length > 200) logArea.firstChild.remove();
  if (_autoScroll) logArea.scrollTop = logArea.scrollHeight;
}

function _onDownloadComplete(entry) {
  // Error reporting link when there were failures and user didn't stop manually
  if (entry.failedFiles > 0 && !entry.stopped) {
    const span = document.createDocumentFragment();
    const text = document.createTextNode('Had issues? ');
    span.appendChild(text);
    const link = document.createElement('a');
    link.className = 'log-link';
    link.textContent = 'Report this issue';
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const ctx = `${entry.failedFiles} failed of ${entry.downloadedFiles + entry.failedFiles} files`;
      const url = _buildFeedbackUrl(ctx);
      if (url) chrome.tabs.create({ url });
    });
    span.appendChild(link);
    logRich(span, 'warning');
  }

  // Review prompt when everything succeeded
  if (entry.failedFiles === 0 && entry.downloadedFiles > 0 && !entry.stopped) {
    chrome.storage.local.get(config.reviewDismissedKey).then((data) => {
      if (data[config.reviewDismissedKey]) return;

      const frag = document.createDocumentFragment();

      const dismiss = document.createElement('button');
      dismiss.className = 'review-dismiss';
      dismiss.textContent = '\u2715';
      dismiss.title = 'Dismiss';
      frag.appendChild(dismiss);

      const text = document.createTextNode('Enjoying Adobe Bulk Download? ');
      frag.appendChild(text);

      const link = document.createElement('a');
      link.className = 'log-link';
      link.textContent = 'Leave a review';
      frag.appendChild(link);

      logRich(frag, 'review');

      // Grab reference to the element that was just appended (last child of logArea)
      const el = logArea.lastElementChild;

      link.addEventListener('click', (e) => {
        e.preventDefault();
        chrome.storage.local.set({ [config.reviewDismissedKey]: true });
        if (config.cwsReviewUrl) chrome.tabs.create({ url: config.cwsReviewUrl });
        el.remove();
      });

      dismiss.addEventListener('click', () => {
        chrome.storage.local.set({ [config.reviewDismissedKey]: true });
        el.remove();
      });
    }).catch(() => {});
  }
}

let scanFilesSoFar = 0;
let scanFoldersSoFar = 0;

function updateFileCount() {
  const status = document.body.dataset.status;
  if (status === 'scanning') {
    fileCount.textContent = `${scanFilesSoFar.toLocaleString()} files · ${scanFoldersSoFar.toLocaleString()} folders`;
  } else if (status === 'scanned') {
    fileCount.textContent = `${totalFiles.toLocaleString()} files found`;
  } else {
    fileCount.textContent = `${downloadedFiles.toLocaleString()} / ${totalFiles.toLocaleString()}`;
  }
}

function updateSpeed() {
  if (!startTime || downloadedBytes === 0) {
    statSpeed.textContent = '\u2014';
    return;
  }
  const elapsed = (Date.now() - startTime) / 1000;
  if (elapsed <= 0) return;
  statSpeed.textContent = '\u2193 ' + formatBytes(downloadedBytes / elapsed) + '/s';
}

// --- Event handling ---

async function handleEvent(entry) {
  switch (entry.event) {
    case 'status_change':
      if (entry.status === 'stopped') {
        document.body.dataset.stoppedPhase = entry.stoppedPhase || 'scanning';
      } else {
        delete document.body.dataset.stoppedPhase;
      }
      document.body.dataset.status = entry.status;
      // Mark that a live status_change has been applied since the last GET_STATE,
      // so a late STATE snapshot won't regress this status (see STATE branch).
      _statusEventSinceGetState = true;
      // Hide worker strip on terminal status
      if (['complete', 'stopped', 'idle', 'error', 'scanned'].includes(entry.status)) {
        const strip = document.getElementById('worker-strip');
        strip.hidden = true;
        strip.innerHTML = '';
        _pendingWorkerUpdates.clear();
      }
      if (entry.status === 'idle' || entry.status === 'scanning') {
        phaseLabel.textContent = '';
        etaLabel.textContent = entry.status === 'scanning' ? 'Scanning\u2026' : 'Idle';
        if (entry.status === 'scanning') {
          scanFilesSoFar = 0;
          scanFoldersSoFar = 0;
          updateFileCount();
        }
      }
      if (entry.status === 'scanned') {
        updateFileCount();
      }
      if (entry.status === 'complete') {
        phaseLabel.textContent = '';
        etaLabel.textContent = 'Complete';
      }
      if (entry.status === 'stopped') {
        phaseLabel.textContent = '';
        etaLabel.textContent = 'Stopped';
      }
      if (entry.status === 'error') {
        phaseLabel.textContent = '';
        etaLabel.textContent = 'Scan failed';
      }
      if (entry.status === 'scanned') {
        phaseLabel.textContent = '';
        etaLabel.textContent = 'Scan complete';
      }
      if (entry.status === 'interrupted') {
        phaseLabel.textContent = '';
        etaLabel.textContent = 'Session interrupted — resume or rescan';
        log('Download interrupted — click Resume to continue', 'warn');
        // Hide worker strip
        const strip = document.getElementById('worker-strip');
        strip.hidden = true;
        strip.innerHTML = '';
        _pendingWorkerUpdates.clear();
        // Hide Resume if no valid resume data exists
        const task = await chrome.storage.session.get('abd_activeTask');
        // Guard: only touch DOM if status hasn't changed during await
        if (document.body.dataset.status === 'interrupted') {
          if (!task?.abd_activeTask) {
            document.getElementById('btn-resume')?.style.setProperty('display', 'none');
          }
        }
      }
      break;

    case 'scan_folder':
      scanFilesSoFar = entry.filesSoFar ?? scanFilesSoFar;
      scanFoldersSoFar = entry.foldersSoFar ?? scanFoldersSoFar;
      if (entry.path) {
        const segs = entry.path.split('/').filter(Boolean);
        phaseLabel.textContent = segs.length > 3
          ? '\u2026/' + segs.slice(-3).join('/')
          : '/' + segs.join('/');
      }
      updateFileCount();
      break;

    case 'scan_complete':
      totalFiles = entry.totalFiles || 0;
      updateFileCount();
      break;

    case 'file_success':
      downloadedFiles++;
      downloadedBytes += entry.downloaded_size ?? entry.size ?? 0;
      updateFileCount();
      updateSpeed();
      statData.textContent = formatBytes(downloadedBytes) + ' downloaded';
      break;

    case 'file_fail':
      failedFiles++;
      _updateHeroErrorCount();
      document.body.dataset.hasErrors = '';
      _failedFilesCount++;
      _failedFilesList.push({
        path: entry.path,
        name: entry.name,
        error: entry.error,
        errorCategory: entry.error_category,
        interruptReason: entry.interrupt_reason || null,
        size: entry.size,
        category: entry.category,
        httpStatus: entry.httpStatus || entry.http_status || null,
        stage: entry.stage || null,
        url: entry.url || null,
        durationMs: entry.durationMs || entry.duration_ms || null,
        retryCount: entry.retry_count ?? entry.retryCount ?? 0,
        tierLog: entry.tierLog || [],
        responseHeaders: entry.responseHeaders || null,
        timestamp: entry.timestamp || new Date().toISOString(),
        expectedBytes: entry.expected_bytes ?? entry.expectedBytes ?? null,
        actualBytes: entry.actual_bytes ?? entry.actualBytes ?? null,
      });
      failedList.appendChild(_renderFailedFile(_failedFilesList[_failedFilesList.length - 1]));
      _updateFailedFilesUI();
      break;

    case 'eta_update':
      progressBar.value = Math.max(0, Math.min(100, entry.percent || 0));
      if (entry.completedFiles != null && entry.totalFiles != null) {
        downloadedFiles = entry.completedFiles;
        totalFiles = entry.totalFiles;
        updateFileCount();
      }
      if (entry.phaseLabel) phaseLabel.textContent = entry.phaseLabel;
      if (entry.displayText) etaLabel.textContent = entry.displayText;
      break;

    case 'download_start':
      if (!entry.fromRecovery) {
        // Fresh download — zero all counters
        downloadedFiles = 0;
        failedFiles = 0;
        downloadedBytes = 0;
        _atFreeLimit = false;
        delete document.body.dataset.hasErrors;
        _failedFilesList = [];
        _failedFilesCount = 0;
        failedList.innerHTML = '';
        _updateFailedFilesUI();
        _updateHeroErrorCount();
        statData.textContent = '\u2014';
        statSpeed.textContent = '\u2014';
      }
      // Reset startTime for speed/ETA calculation in both cases
      startTime = Date.now();
      updateFileCount();
      break;

    case 'session_initialized':
      downloadedFiles = 0;
      failedFiles = 0;
      downloadedBytes = 0;
      totalFiles = 0;
      startTime = null;
      delete document.body.dataset.hasErrors;
      _updateHeroErrorCount();
      statData.textContent = '\u2014';
      statSpeed.textContent = '\u2014';
      progressBar.value = 0;
      updateFileCount();
      break;

    case 'token_invalid':
      tokenBadge.textContent = 'Sign in to Adobe';
      tokenBadge.title = 'Token rejected \u2014 open Adobe Creative Cloud';
      tokenBadge.dataset.connected = 'false';
      break;

    case 'token_accepted':
      tokenBadge.textContent = 'Connected to Adobe';
      tokenBadge.title = 'Auth token detected and valid';
      tokenBadge.dataset.connected = 'true';
      break;

    case 'token_expiry_warning':
      tokenBadge.textContent = 'Reload Adobe tab';
      tokenBadge.title = 'Session ending soon \u2014 refresh to continue';
      tokenBadge.dataset.connected = 'warn';
      break;

    case 'token_expired':
      tokenBadge.textContent = 'Session expired';
      tokenBadge.title = 'Reload your Adobe tab or sign in again';
      tokenBadge.dataset.connected = 'false';
      break;

    case 'free_limit_reached': {
      _atFreeLimit = true;
      const ud = document.getElementById('upgrade-dialog');
      document.getElementById('upgrade-message').textContent =
        `You've downloaded ${entry.downloaded} files \u2014 the free limit. Upgrade for $19 to download unlimited files.`;
      if (!ud.open) ud.showModal();
      etaLabel.textContent = `${entry.downloaded} of ${totalFiles} files \u2014 Upgrade to download all`;
      break;
    }

    case 'license_activated':
      _isPaid = true;
      _showLicenseBadge();
      // Log line handled by events.js with 'success' type
      { const ud = document.getElementById('upgrade-dialog');
        if (ud.open) ud.close(); }
      if (_atFreeLimit && document.body.dataset.status === 'paused') {
        chrome.runtime.sendMessage({ type: 'RESUME_DOWNLOAD' }).catch(() => {});
      }
      _atFreeLimit = false;
      break;

    case 'download_complete':
      _onDownloadComplete(entry);
      break;
  }
}

// --- Listen for broadcast ABD events and resume prompts ---
// Registered BEFORE port.connect() to avoid losing events emitted between connect and GET_STATE.

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id) return;

  if (msg.type === 'ABD_EVENT') {
    // Worker/scan strip handling (fire-and-forget UI updates)
    if (msg.entry.event === 'workers_init') {
      const strip = document.getElementById('worker-strip');
      const count = Math.min(Math.max(0, msg.entry.count || 0), 20);
      if (count <= 0) { strip.hidden = true; return; }
      strip.hidden = false;
      strip.innerHTML = '';
      for (let i = 0; i < count; i++) {
        const row = document.createElement('div');
        row.dataset.worker = String(i);
        row.textContent = '\u2014 idle';
        strip.appendChild(row);
      }
    } else if (msg.entry.event === 'worker_status') {
      const wid = parseInt(msg.entry.workerId, 10);
      if (!Number.isFinite(wid) || wid < 0) return;
      const strip = document.getElementById('worker-strip');
      if (!strip || wid >= strip.children.length) return;
      _pendingWorkerUpdates.set(wid, {
        state: msg.entry.state,
        fileName: msg.entry.fileName,
      });
      _scheduleStripFlush();
    }
    handleEvent(msg.entry).catch((err) => {
      console.error('[ABD sidepanel] handleEvent error:', err, msg.entry);
    });
    const formatted = formatEventForUI(msg.entry, config);
    if (formatted) log(formatted.message, formatted.type);
    sendResponse();
    return;
  }

  if (msg.type === 'ABD_RESUME_PROMPT') {
    const extOrigin = `chrome-extension://${chrome.runtime.id}/`;
    if (sender.tab || !sender.url?.startsWith(extOrigin)) {
      console.warn('[ABD sidepanel] Resume prompt rejected: wrong origin');
      sendResponse({ choice: 'fresh' });
      return true;
    }
    if (pendingResumeResponse) {
      try { pendingResumeResponse({ choice: 'fresh' }); } catch {}
      pendingResumeResponse = null;
    }
    pendingResumeResponse = sendResponse;
    resumeMessage.textContent = `Found ${Math.max(0, Number(msg.skippedCount) || 0)} previously downloaded files out of ${Math.max(0, Number(msg.totalFiles) || 0)} total. Resume where you left off?`;
    if (!resumeDialog.open) resumeDialog.showModal();
    return true;
  }
});

// --- Service worker connection ---

// `port` is reassigned by connectPort() after the SW terminates (MV3 service
// workers idle out and disconnect the port roughly every 5 min). `let`, not `const`.
let port;
// True once the page is unloading — stops reconnect attempts so we don't spin
// while the panel is closing.
let _panelUnloading = false;

function _handlePortMessage(msg) {
  if (msg.type === 'STATE') {
    // Restore state from background snapshot.
    // Invariant: a STATE snapshot must not regress a status received via a live
    // event after this GET_STATE was issued. On a cold service worker the STATE
    // reply is deferred until startup completes and can arrive AFTER a fresher
    // status_change live event; applying the (stale) snapshot status here would
    // clobber it. Everything else below (hasToken/badge, counts, failed list,
    // ETA, stoppedPhase, isPaid) still applies unconditionally.
    if (!_statusEventSinceGetState) {
      document.body.dataset.status = msg.status || 'idle';
    }
    if (msg.stoppedPhase) {
      document.body.dataset.stoppedPhase = msg.stoppedPhase;
    } else {
      delete document.body.dataset.stoppedPhase;
    }
    totalFiles = msg.totalFiles || 0;
    downloadedFiles = msg.downloadedFiles || 0;
    failedFiles = msg.failedFiles || 0;
    downloadedBytes = msg.downloadedBytes || 0;
    startTime = msg.startTime || null;
    _isPaid = !!msg.isPaid;

    updateFileCount();
    statData.textContent = downloadedBytes > 0 ? formatBytes(downloadedBytes) + ' downloaded' : '\u2014';
    _updateHeroErrorCount();
    if (failedFiles > 0) document.body.dataset.hasErrors = '';
    else delete document.body.dataset.hasErrors;
    // Restore failed files list
    _failedFilesCount = msg.failedFiles || 0;
    if (msg.failedFilesList?.length > 0) {
      _failedFilesList = msg.failedFilesList;
      failedList.innerHTML = '';
      for (const entry of _failedFilesList) {
        failedList.appendChild(_renderFailedFile(entry));
      }
      _updateFailedFilesUI();
    }
    updateSpeed();

    if (msg.hasToken) {
      tokenBadge.textContent = 'Connected to Adobe';
      tokenBadge.title = 'Auth token detected and valid';
      tokenBadge.dataset.connected = 'true';
    } else if (msg.hadTokenBefore) {
      tokenBadge.textContent = 'Reload Adobe tab';
      tokenBadge.title = 'Reload your Adobe tab to connect';
      tokenBadge.dataset.connected = 'warn';
    } else {
      tokenBadge.textContent = 'Sign in to Adobe';
      tokenBadge.title = 'Open Adobe Creative Cloud and sign in';
      tokenBadge.dataset.connected = 'false';
    }

    // Restore ETA display. A real eta payload is genuine restore data and always
    // applies. The scanning/idle label fallbacks below are derived purely from the
    // snapshot status, so they obey the same no-regression invariant as the status
    // itself: don't let a stale snapshot overwrite a label set by a later live event.
    if (msg.eta) {
      progressBar.value = msg.eta.percent || 0;
      if (msg.eta.phaseLabel) phaseLabel.textContent = msg.eta.phaseLabel;
      if (msg.eta.displayText) etaLabel.textContent = msg.eta.displayText;
    } else if (!_statusEventSinceGetState) {
      if (msg.status === 'scanning') {
        etaLabel.textContent = 'Scanning\u2026';
      } else if (totalFiles === 0) {
        etaLabel.textContent = 'Idle';
      }
    }

    // Restore worker strip if download is active
    if (msg.workerCount > 0) {
      const strip = document.getElementById('worker-strip');
      strip.hidden = false;
      strip.innerHTML = '';
      for (let i = 0; i < msg.workerCount; i++) {
        const row = document.createElement('div');
        row.dataset.worker = String(i);
        row.textContent = '\u2014 idle';
        strip.appendChild(row);
      }
    }

    // A4: Check for persisted resume prompt from background
    _checkPendingResumePrompt();
  }
}

// Create (or re-create) the port to the service worker, wire its listeners, and
// request a fresh state snapshot. Called on load and again after each disconnect
// so the badge and other GET_STATE-derived UI recover across SW restarts.
function connectPort() {
  if (_panelUnloading) return;
  try {
    port = chrome.runtime.connect({ name: 'sidepanel' });
  } catch {
    // Extension context invalidated (e.g. reload/update) — give up; the panel
    // will be torn down with the old context anyway.
    return;
  }
  port.onMessage.addListener(_handlePortMessage);
  port.onDisconnect.addListener(() => {
    console.log('[ABD] Disconnected from service worker.');
    if (_panelUnloading) return;
    // Reconnecting fires runtime.onConnect, which wakes a terminated SW; the
    // fresh GET_STATE then refreshes hasToken/hadTokenBefore (and the badge).
    // Small delay avoids a tight loop if the SW is unavailable momentarily.
    setTimeout(connectPort, 250);
  });
  // Request initial state (also re-requested on every reconnect).
  // Reset the live-event guard immediately before issuing GET_STATE so that any
  // status_change arriving after this point (the cold-SW race) takes precedence
  // over the upcoming STATE snapshot.
  _statusEventSinceGetState = false;
  try {
    port.postMessage({ type: 'GET_STATE' });
  } catch { /* port already closed; onDisconnect will trigger a reconnect */ }
}

// Stop reconnecting once the panel is tearing down.
window.addEventListener('pagehide', () => { _panelUnloading = true; });

connectPort();

// --- Resume dialog handlers ---

document.getElementById('btn-fresh').addEventListener('click', () => {
  if (_persistedResumePromptActive) {
    chrome.storage.session.set({ [config.resumeAnswerKey]: { choice: 'fresh' } }).catch(() => {});
    chrome.storage.session.remove(config.resumePromptKey).catch(() => {});
    _persistedResumePromptActive = false;
  }
  if (pendingResumeResponse) {
    pendingResumeResponse({ choice: 'fresh' });
    pendingResumeResponse = null;
  }
  resumeDialog.close();
});

document.getElementById('btn-dialog-resume').addEventListener('click', () => {
  if (_persistedResumePromptActive) {
    chrome.storage.session.set({ [config.resumeAnswerKey]: { choice: 'resume' } }).catch(() => {});
    chrome.storage.session.remove(config.resumePromptKey).catch(() => {});
    _persistedResumePromptActive = false;
  }
  if (pendingResumeResponse) {
    pendingResumeResponse({ choice: 'resume' });
    pendingResumeResponse = null;
  }
  resumeDialog.close();
});

resumeDialog.addEventListener('close', () => {
  if (_persistedResumePromptActive) {
    chrome.storage.session.set({ [config.resumeAnswerKey]: { choice: 'fresh' } }).catch(() => {});
    chrome.storage.session.remove(config.resumePromptKey).catch(() => {});
    _persistedResumePromptActive = false;
  }
  if (pendingResumeResponse) {
    pendingResumeResponse({ choice: 'fresh' });
    pendingResumeResponse = null;
  }
});

// --- Upgrade dialog handlers ---

document.getElementById('btn-upgrade-later').addEventListener('click', () => {
  document.getElementById('upgrade-dialog').close();
});

document.getElementById('btn-upgrade').addEventListener('click', async () => {
  // Set upgradePendingKey BEFORE opening the tab so it's ready before the success page redirect fires
  chrome.storage.session.set({ [config.upgradePendingKey]: true }).catch(() => {});
  if (config.stripeCheckoutUrl) {
    try {
      const emailResp = await chrome.runtime.sendMessage({ type: 'GET_EMAIL' });
      const email = emailResp?.email || '';
      logDiagnostic({ event: 'stripe_checkout_open', level: 'INFO', data: { hasEmail: !!email } });
      const params = new URLSearchParams();
      if (email) params.set('prefilled_email', email);
      const uidResp = await chrome.runtime.sendMessage({ type: 'GET_USER_ID' });
      if (uidResp?.uid) params.set('client_reference_id', uidResp.uid);
      const qs = params.toString();
      let url = config.stripeCheckoutUrl;
      if (qs) url += `?${qs}`;
      chrome.runtime.sendMessage({ type: 'TRACK_EVENT', name: 'abd_payment_link_opened' }).catch(() => {});
      chrome.tabs.create({ url });
    } catch {
      logDiagnostic({ event: 'stripe_checkout_open', level: 'INFO', data: { fallback: true } });
      chrome.tabs.create({ url: config.stripeCheckoutUrl });
    }
  } else {
    logDiagnostic({ event: 'stripe_checkout_not_configured', level: 'WARN', data: {} });
    log('Payment not yet configured \u2014 check back in a future update', 'warn');
  }
  document.getElementById('upgrade-dialog').close();
});

// --- Pending resume prompt check (A4: resume persistence) ---

async function _checkPendingResumePrompt() {
  if (_persistedResumePromptActive || resumeDialog.open) return; // already showing
  try {
    const data = await chrome.storage.session.get(config.resumePromptKey);
    const prompt = data?.[config.resumePromptKey];
    if (!prompt) return;
    // Stale check: timestamp + extendedTimeout + 5s grace
    if (Date.now() - prompt.timestamp > config.resumePromptExtendedTimeoutMs + 5000) {
      chrome.storage.session.remove([config.resumePromptKey, config.resumeAnswerKey]).catch(() => {});
      return;
    }
    _persistedResumePromptActive = true;
    resumeMessage.textContent = `Found ${prompt.skippedCount ?? 0} previously downloaded files out of ${prompt.totalFiles ?? 0} total. Resume where you left off?`;
    if (!resumeDialog.open) resumeDialog.showModal();
  } catch {
    // Session storage unavailable
  }
}

// --- Controls ---

function _handleStartScan() {
  chrome.runtime.sendMessage({ type: 'START_SCAN' }).then((resp) => {
    if (resp && resp.reason === 'no_token') {
      tokenBadge.classList.remove('flash');
      void tokenBadge.offsetWidth;
      tokenBadge.classList.add('flash');
    }
  }).catch(() => log('Failed to reach service worker', 'error'));
}
document.getElementById('btn-scan').addEventListener('click', _handleStartScan);

document.getElementById('btn-download').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'START_DOWNLOAD' }).catch(() => log('Failed to reach service worker', 'error'));
});

document.getElementById('btn-pause').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'PAUSE_DOWNLOAD' }).catch(() => log('Failed to reach service worker', 'error'));
});

document.getElementById('btn-resume').addEventListener('click', () => {
  if (_atFreeLimit) {
    const ud = document.getElementById('upgrade-dialog');
    if (!ud.open) ud.showModal();
    return;
  }
  chrome.runtime.sendMessage({ type: 'RESUME_DOWNLOAD' }).catch(() => log('Failed to reach service worker', 'error'));
});

document.getElementById('btn-stop').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'STOP_DOWNLOAD' }).catch(() => log('Failed to reach service worker', 'error'));
});

document.getElementById('btn-retry').addEventListener('click', () => {
  if (_atFreeLimit) {
    const ud = document.getElementById('upgrade-dialog');
    if (!ud.open) ud.showModal();
    return;
  }
  chrome.runtime.sendMessage({ type: 'RETRY_FAILED' }).catch(() => log('Failed to reach service worker', 'error'));
});

function _formatFileTimestamp() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}_${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}`;
}

document.getElementById('btn-export-errors').addEventListener('click', () => {
  if (_failedFilesList.length === 0) return;
  const header = 'File Name\tPath\tCategory\tError\tError Category\tHTTP Status\tStage\tTier Chain\tDuration (ms)\tRetry Count\tURL Domain\tResponse Headers\tExpected Bytes\tActual Bytes\tTimestamp\n';
  const safe = (v) => String(v ?? '').replace(/[\t\n\r]/g, ' ');
  const rows = _failedFilesList.map((f) => {
    const tierChain = (f.tierLog || []).map((t) => `T${t.tier}:${t.result || '?'}`).join('>') || '-';
    const hdrs = f.responseHeaders ? Object.entries(f.responseHeaders).map(([k, v]) => `${k}=${v}`).join('; ') : '-';
    return [
      safe(f.name), safe(f.path), safe(f.category), safe(f.error),
      safe(f.errorCategory), safe(f.httpStatus || '-'), safe(f.stage || '-'), safe(tierChain),
      safe(f.durationMs || '-'), safe(f.retryCount || 0), safe(f.url || '-'), safe(hdrs),
      safe(f.expectedBytes ?? '-'), safe(f.actualBytes ?? '-'), safe(f.timestamp),
    ].join('\t');
  }).join('\n');
  const tsv = header + rows;
  const blob = new Blob([tsv], { type: 'text/tab-separated-values' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const ts = _formatFileTimestamp();
  a.download = `abd-errors-${ts}.tsv`;
  a.click();
  URL.revokeObjectURL(url);
});

document.getElementById('btn-export-diagnostics').addEventListener('click', async () => {
  // Flush any pending diagnostic entries in the SW's memory before export
  try { await chrome.runtime.sendMessage({ type: 'FLUSH_DIAGNOSTICS' }); } catch {}

  // Build the NDJSON header line with session summary + capabilities
  let capabilities = {};
  try {
    const data = await chrome.storage.session.get(config.capabilitiesKey);
    capabilities = data[config.capabilitiesKey] || {};
  } catch {}

  const errorBreakdown = {};
  for (const f of _failedFilesList) {
    const cat = f.errorCategory || 'unknown';
    errorBreakdown[cat] = (errorBreakdown[cat] || 0) + 1;
  }

  const header = {
    _type: 'header',
    exportedAt: new Date().toISOString(),
    capabilities,
    sessionSummary: {
      totalFiles,
      downloadedFiles,
      failedFiles,
      downloadedBytes,
      startTime,
      endTime: Date.now(),
      durationMs: startTime ? Date.now() - startTime : 0,
      filesPerMinute: startTime && downloadedFiles > 0
        ? Math.round((downloadedFiles / ((Date.now() - startTime) / 1000)) * 60 * 10) / 10
        : 0,
      bytesPerSecond: startTime && downloadedBytes > 0
        ? Math.round(downloadedBytes / ((Date.now() - startTime) / 1000))
        : 0,
      errorBreakdown,
    },
    failedFiles: _failedFilesList,
    config: {
      concurrentDownloads: parseInt(concurrencySelect.value, 10) || 3,
      downloadSubfolder: subfolderInput.value || '',
    },
  };

  // Stream NDJSON through gzip — sidepanel reads IndexedDB directly (same origin as SW)
  const { readable, writable } = new TransformStream();
  const gzipStream = readable.pipeThrough(new CompressionStream('gzip'));
  const writer = writable.getWriter();
  const encoder = new TextEncoder();

  // Collect compressed output
  const chunks = [];
  const readerPromise = (async () => {
    const reader = gzipStream.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }
  })();

  // Write header line
  await writer.write(encoder.encode(JSON.stringify(header) + '\n'));

  // Write diagnostic entries from IndexedDB (no message round-trip)
  try {
    const entries = await getAllDiagEntries();
    for (const entry of entries) {
      await writer.write(encoder.encode(JSON.stringify(entry) + '\n'));
    }
  } catch {}

  await writer.close();
  await readerPromise;

  const blob = new Blob(chunks, { type: 'application/gzip' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const ts = _formatFileTimestamp();
  a.download = `abd-diagnostics-${ts}.ndjson.gz`;
  a.click();
  URL.revokeObjectURL(url);
});

// --- Settings ---

async function loadSettings() {
  try {
    const data = await chrome.storage.sync.get({ abd_concurrency: 10, abd_theme: '', abd_diagnosticLevel: 'INFO' });
    // abd_subfolder fetched separately — absence means "use config default", empty string means "user cleared it"
    const subfolderData = await chrome.storage.sync.get('abd_subfolder');
    const val = data.abd_concurrency;
    const clamped = Math.max(1, Math.min(10, Number.isInteger(val) ? val : 10));
    concurrencySelect.value = String(clamped);
    const VALID_THEMES = ['', 'light', 'dark'];
    const theme = VALID_THEMES.includes(data.abd_theme) ? data.abd_theme : '';
    themeSelect.value = theme;
    document.documentElement.dataset.theme = theme;
    const subfolder = 'abd_subfolder' in subfolderData ? subfolderData.abd_subfolder : 'Adobe Downloads';
    subfolderInput.value = subfolder.slice(0, 100);
    const VALID_LEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
    const diagLevel = VALID_LEVELS.includes(data.abd_diagnosticLevel) ? data.abd_diagnosticLevel : 'INFO';
    diagLevelSelect.value = diagLevel;
    chrome.runtime.sendMessage({
      type: 'SET_CONFIG',
      concurrency: clamped,
      subfolder: subfolder,
      diagnosticLevel: diagLevel,
    }).catch(() => {});
  } catch (err) {
    console.warn('[ABD sidepanel] loadSettings failed:', err.message);
    concurrencySelect.value = '10';
    themeSelect.value = '';
    document.documentElement.dataset.theme = '';
    subfolderInput.value = '';
    diagLevelSelect.value = 'INFO';
  }
}

concurrencySelect.addEventListener('change', () => {
  const raw = parseInt(concurrencySelect.value, 10);
  const val = Math.max(1, Math.min(10, Number.isFinite(raw) ? raw : 5));
  chrome.runtime.sendMessage({ type: 'SET_CONFIG', concurrency: val });
  chrome.storage.sync.set({ abd_concurrency: val });
});

themeSelect.addEventListener('change', () => {
  const val = themeSelect.value;
  document.documentElement.dataset.theme = val;
  chrome.storage.sync.set({ abd_theme: val });
});

let _subfolderDebounce = null;
subfolderInput.addEventListener('input', () => {
  clearTimeout(_subfolderDebounce);
  _subfolderDebounce = setTimeout(() => {
    const val = subfolderInput.value.trim().replace(/[\0/\\]/g, '').slice(0, 100);
    chrome.runtime.sendMessage({ type: 'SET_CONFIG', subfolder: val });
    chrome.storage.sync.set({ abd_subfolder: val });
  }, 500);
});

diagLevelSelect.addEventListener('change', () => {
  const val = diagLevelSelect.value;
  chrome.runtime.sendMessage({ type: 'SET_CONFIG', diagnosticLevel: val })
    .catch(() => log('Failed to reach service worker', 'error'));
  chrome.storage.sync.set({ abd_diagnosticLevel: val });
});

loadSettings();

// Side panel ready — no activity log entry needed.

function _showLicenseBadge() {
  const badge = document.getElementById('license-badge');
  if (badge) badge.hidden = false;
}

// --- License check on load ---
chrome.storage.session.get(config.upgradePendingKey).then((data) => {
  const msgType = data?.[config.upgradePendingKey] ? 'ACTIVATE_LICENSE' : 'CHECK_LICENSE';
  return chrome.runtime.sendMessage({ type: msgType }).then((resp) => {
    logDiagnostic({ event: 'license_check_on_load', level: 'INFO', data: { paid: !!resp?.paid, type: msgType } });
    return resp;
  });
}).then((resp) => {
  if (resp?.paid) {
    chrome.storage.session.remove(config.upgradePendingKey).catch(() => {});
    _showLicenseBadge();
  }
}).catch(() => {});

// --- Cancel event guards: prevent dialogs closing via Escape/CloseWatcher when the settings drawer is open ---
// Chrome 120+ uses CloseWatcher internally for <dialog>; keydown preventDefault is not reliable.
[resumeDialog, document.getElementById('upgrade-dialog'), document.getElementById('email-dialog')].forEach((dlg) => {
  if (!dlg) return;
  dlg.addEventListener('cancel', (e) => {
    if (document.getElementById('settings-drawer').classList.contains('drawer-open')) {
      e.preventDefault();
    }
  });
});

// --- Email restore dialog ---
const emailDialog = document.getElementById('email-dialog');
const emailInput = document.getElementById('email-input');

document.getElementById('link-restore-license').addEventListener('click', (e) => {
  e.preventDefault();
  emailDialog.showModal();
});

document.getElementById('btn-email-cancel').addEventListener('click', () => {
  emailDialog.close();
});

document.getElementById('btn-email-confirm').addEventListener('click', async () => {
  const email = emailInput.value.trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return;

  logDiagnostic({ event: 'license_restore_attempt', level: 'INFO', data: {} });
  try {
    await chrome.runtime.sendMessage({ type: 'SET_EMAIL', email });
    emailDialog.close();

    // Re-verify with server using the entered email
    const resp = await chrome.runtime.sendMessage({ type: 'ACTIVATE_LICENSE' });
    if (resp?.paid) {
      logDiagnostic({ event: 'license_restore_success', level: 'INFO', data: {} });
      _showLicenseBadge();
      log('License restored!', 'success');
    } else {
      logDiagnostic({ event: 'license_restore_not_found', level: 'WARN', data: {} });
      log('No license found for that email. Check the address and try again.', 'warn');
    }
  } catch {
    logDiagnostic({ event: 'license_restore_error', level: 'ERROR', data: {} });
    log('Failed to reach service worker \u2014 try again', 'error');
  }
});

// --- Version (in settings drawer) ---
const _version = chrome.runtime.getManifest().version;
const drawerVersion = document.getElementById('drawer-version');
if (drawerVersion) drawerVersion.textContent = `v${_version}`;

// --- Feedback link ---
const feedbackLink = document.getElementById('link-feedback');
if (feedbackLink) {
  feedbackLink.addEventListener('click', (e) => {
    e.preventDefault();
    const url = _buildFeedbackUrl();
    if (url) chrome.tabs.create({ url });
  });
}

// --- Settings drawer ---

function _openDrawer() {
  const drawer = document.getElementById('settings-drawer');
  const backdrop = document.getElementById('settings-backdrop');
  drawer.classList.remove('drawer-closed');
  drawer.classList.add('drawer-open');
  drawer.inert = false;
  backdrop.hidden = false;
}

function _closeDrawer() {
  const drawer = document.getElementById('settings-drawer');
  const backdrop = document.getElementById('settings-backdrop');
  drawer.classList.remove('drawer-open');
  drawer.classList.add('drawer-closed');
  drawer.inert = true;
  backdrop.hidden = true;
}

document.getElementById('btn-settings-gear').addEventListener('click', () => {
  const drawer = document.getElementById('settings-drawer');
  if (drawer.classList.contains('drawer-open')) {
    _closeDrawer();
  } else {
    _openDrawer();
  }
});

document.getElementById('btn-settings-close').addEventListener('click', _closeDrawer);
document.getElementById('settings-backdrop').addEventListener('click', _closeDrawer);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const drawer = document.getElementById('settings-drawer');
    if (drawer.classList.contains('drawer-open')) {
      _closeDrawer();
    }
  }
});
