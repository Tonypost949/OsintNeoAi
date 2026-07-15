// state.js — State management and chrome.storage.local persistence (ES module).
// Ported from adobe-bulk-download-v1.5.3.js lines 88-126, 1487-1514.

import { events } from './events.js';
import { serializeState as serializeETA, restoreState as restoreETA, resetETA } from './eta.js';
import { config } from './config.js';

/**
 * Default values for mutable state fields.
 * Used by resetState() and as the initial shape.
 */
const STATE_DEFAULTS = {
  status: 'idle',
  files: [],
  folders: [],
  totalFiles: 0,
  downloadedFiles: 0,
  failedFiles: 0,
  totalBytes: 0,
  downloadedBytes: 0,
  currentFile: null,
  currentFolder: '',
  folderIndex: 0,
  totalFolders: 0,
  startTime: null,
  errors: [],
  sessionId: Date.now().toString(36),
  paused: false,
  _freeLimitEmitted: false,
  _freeFilesUsed: 0,
  stopped: false,
  stoppedPhase: null,
  repositoryId: null,
  storageRegion: null,
  regions: [],
  platformBaseUrl: null,
  adaptiveDelay: 1000,
  lastThrottleTime: 0,
  failedFilesList: [],
  sessionMetrics: {
    startTime: null,
    endTime: null,
    bytesPerSecond: 0,
    filesPerMinute: 0,
    peakConcurrency: 0,
    consecutiveFailures: 0,
    maxConsecutiveFailures: 0,
  },
};

/**
 * Mutable runtime state. Same shape as v1.5.3 ABD.state minus directoryHandle
 * (chrome.downloads replaces File System Access).
 */
export const state = { ...STATE_DEFAULTS };

/**
 * Reset mutable state fields to defaults (useful for fresh scan).
 * Generates a new sessionId.
 */
export function resetState() {
  Object.assign(state, STATE_DEFAULTS, {
    sessionId: Date.now().toString(36),
    files: [],
    folders: [],
    errors: [],
    failedFilesList: [],
    regions: [],
    sessionMetrics: {
      startTime: null,
      endTime: null,
      bytesPerSecond: 0,
      filesPerMinute: 0,
      peakConcurrency: 0,
      consecutiveFailures: 0,
      maxConsecutiveFailures: 0,
    },
  });
  resetETA();
}

/**
 * Wait until state.paused is cleared (or state.stopped is set).
 * Uses a short setTimeout loop (1s) instead of chrome.alarms (30s minimum).
 * A chrome.runtime.getPlatformInfo heartbeat every 25s keeps the SW alive
 * during the wait (each extension API call resets the 30s idle timeout).
 */
export function waitForResume() {
  // Fast path: already unpaused or stopped
  if (!state.paused || state.stopped) return Promise.resolve();

  return new Promise((resolve) => {
    // Heartbeat: call a Chrome API every 25s to reset the SW idle timer
    const heartbeat = setInterval(() => chrome.runtime.getPlatformInfo(() => {}), 25_000);

    const check = () => {
      if (!state.paused || state.stopped) {
        clearInterval(heartbeat);
        resolve();
      } else {
        setTimeout(check, 1000);
      }
    };
    setTimeout(check, 1000);
  });
}

/**
 * Save current download progress to chrome.storage.local.
 * Replaces localStorage.setItem from v1.5.3.
 */
export async function saveProgress() {
  try {
    const key = config.storageKeyPrefix + state.sessionId;
    await chrome.storage.local.set({
      [key]: {
        sessionId: state.sessionId,
        timestamp: Date.now(),
        downloadedIds: state.files.filter((f) => f.downloaded).map((f) => f.assetId),
        failedIds: state.files.filter((f) => f.failed).map((f) => f.assetId),
        totalFiles: state.totalFiles,
        downloadedBytes: state.downloadedBytes,
        eta: serializeETA(),
      },
    });
  } catch (e) {
    events.emit('progress_save_failed', { error: e.message });
  }
}

/**
 * Load the most recent valid progress from chrome.storage.local.
 * Replaces localStorage scan from v1.5.3. Same 24h TTL.
 *
 * @returns {Promise<object|null>} Progress data or null if none/expired.
 */
export async function loadProgress() {
  try {
    const all = await chrome.storage.local.get(null);
    const keys = Object.keys(all).filter((k) => k.startsWith(config.storageKeyPrefix));
    if (!keys.length) return null;
    // Base-36 Date.now() suffixes are same-length (10 chars) until 2059, so alpha sort = chronological
    const data = all[keys.sort().pop()];
    if (!data?.timestamp) return null;
    return Date.now() - data.timestamp < 86400000 ? data : null;
  } catch (e) {
    events.emit('progress_load_failed', { error: e.message });
    return null;
  }
}
