// scanner.js — Folder traversal and scan orchestration (ES module).
// Ported from adobe-bulk-download-v1.5.3.js lines 137-145, 662-800.

import { fetchWithRetry, sleep } from './api.js';
import { events, formatBytes } from './events.js';
import { config } from './config.js';
import { state, saveProgress, resetState, waitForResume } from './state.js';
import { logDiagnostic } from './diagnostics.js';
import { getToken } from './token.js';

async function resolveRegion(repositoryId, path) {
  const url = `https://platform-cs-edge.adobe.io/content/directory/resolve?repositoryId=${encodeURIComponent(repositoryId)}&path=${encodeURIComponent(path)}`;
  try {
    const token = getToken();
    const resp = await fetch(url, {
      method: 'HEAD',
      redirect: 'manual',
      headers: {
        Accept: '*/*',
        ...(token ? { Authorization: 'Bearer ' + token, 'X-Api-Key': config.apiKey } : {}),
      },
    });
    if (resp.status < 300 || resp.status > 399) return null;
    const location = resp.headers.get('Location');
    if (!location) return null;
    const match = location.match(/^https:\/\/platform-cs-edge-([a-z0-9]+)\.adobe\.io\//i);
    if (!match) return null;
    if (!/^[a-z0-9]{2,10}$/i.test(match[1])) return null;
    return { region: match[1].toUpperCase(), baseUrl: `https://platform-cs-edge-${match[1].toLowerCase()}.adobe.io` };
  } catch (e) {
    logDiagnostic({ event: 'scan_region_resolve_error', level: 'WARN',
      data: { error: e?.message || 'unknown', repositoryId, path } });
    return null;
  }
}

/** Discover repository info from Adobe platform index. */
export async function initialize() {
  events.emit('initializing', {});
  const resp = await fetchWithRetry('https://platform-cs.adobe.io/index', {
    headers: { Accept: '*/*' },
  });
  const data = await resp.json();
  const regions = data['repo:regions'] || [];
  const rawRegion = regions[0] || 'VA6C2';
  logDiagnostic({
    event: 'index_response', level: 'INFO',
    data: { regions: regions.slice(0, 10), selectedRegion: rawRegion, usedFallback: regions.length === 0 },
  });
  if (!/^[a-z0-9]{2,10}$/i.test(rawRegion)) {
    throw new Error(`Invalid storage region from API: "${rawRegion}"`);
  }
  state.storageRegion = rawRegion.toUpperCase();
  state.regions = regions.filter(r => /^[a-z0-9]{2,10}$/i.test(r)).map(r => r.toUpperCase());
  const embed = data.children?.[0]?._embedded;
  if (embed) {
    const meta = embed['http://ns.adobe.com/adobecloud/rel/metadata/repository'];
    const repoId = meta?.['repo:repositoryId'];
    if (repoId && !/^urn:aaid:sc:[A-Za-z0-9]+:[a-f0-9-]{36}$/.test(repoId)) {
      throw new Error(`Invalid repositoryId from API: "${repoId}"`);
    }
    state.repositoryId = repoId;
  }
  if (!state.repositoryId) {
    throw new Error('repositoryId not found in /index response');
  }
  state.platformBaseUrl = `https://platform-cs-edge-${state.storageRegion.toLowerCase()}.adobe.io`;
  events.emit('session_initialized', {
    repositoryId: state.repositoryId,
    storageRegion: state.storageRegion,
    platformBaseUrl: state.platformBaseUrl,
  });
}

/** List children of a folder path, consuming all pages. */
export async function listFolder(folderPath, region = null) {
  const children = [];
  const baseUrl = region
    ? `https://platform-cs-edge-${region.toLowerCase()}.adobe.io`
    : state.platformBaseUrl;
  let url = `${baseUrl}/content/storage/path/${state.repositoryId}${folderPath}`;
  let page = 1;
  while (url) {
    await sleep(config.requestDelay);
    // §10.5 fix: check stopped after sleep in pagination loop
    if (state.stopped) return children;
    const resp = await fetchWithRetry(url, {
      headers: { Accept: 'application/vnd.adobecloud.directory+json' },
    });
    const data = await resp.json();
    for (const c of data.children || []) {
      children.push({
        name: c['repo:name'],
        path: c['repo:path'],
        type: c['dc:format'],
        size: c['repo:size'] || 0,
        assetId: c['repo:assetId'],
        modified: c['repo:modifyDate'],
        assetClass: c['repo:assetClass'],
        state: c['repo:state'],
        region: c['storage:region'] || state.storageRegion,
        version: c['repo:version'] ?? null,
      });
    }
    const next = data._links?.next;
    if (next?.href) {
      try {
        const nextHost = new URL(next.href).hostname;
        if (!nextHost.endsWith('.adobe.io') && !nextHost.endsWith('.adobe.com')) {
          throw new Error(`Untrusted pagination URL hostname: ${nextHost}`);
        }
      } catch (e) {
        events.emit('scan_error', { path: folderPath, error: e.message });
        url = null; break;
      }
      url = next.href;
      page++;
      events.emit('scan_pagination', {
        path: folderPath,
        page,
        items_so_far: children.length,
      });
    } else {
      url = null;
    }
  }
  return children;
}

/** Recursively scan a folder, populating state.files and state.folders. */
export async function scanFolder(folderPath, depth = 0) {
  if (depth >= config.maxScanDepth) {
    events.emit('scan_depth_limit', { path: folderPath, depth, maxDepth: config.maxScanDepth });
    return;
  }
  events.emit('scan_folder', { path: folderPath, depth, filesSoFar: state.files.length, foldersSoFar: state.totalFolders });
  state.currentFolder = folderPath;
  let children;
  try {
    children = await listFolder(folderPath);
  } catch (e) {
    events.emit('scan_error', { path: folderPath, error: e.message });
    await saveProgress();
    return;
  }
  for (const child of children) {
    // §10.5 fix: abort traversal if user stopped
    if (state.stopped) {
      logDiagnostic({ event: 'scan_folder_aborted', level: 'DEBUG', data: { path: folderPath } });
      return;
    }

    if (child.state !== 'ACTIVE') {
      logDiagnostic({ event: 'scan_item_skipped', level: 'DEBUG', data: { name: child.name, state: child.state } });
      continue;
    }
    const isDir =
      child.type === 'application/vnd.adobecloud.directory+json' ||
      child.type === 'application/vnd.adobe.directory+json' ||
      child.assetClass === 'directory';
    if (isDir) {
      state.folders.push(child);
      state.totalFolders++;
      await scanFolder(child.path, depth + 1);
    } else {
      let category = 'other';
      if (child.type === 'document/vnd.adobe.cpsd+dcx') category = 'psdc';
      else if (child.type === 'application/pdf') category = 'pdf';
      else if (child.type === 'document/vnd.adobe.illustrator+dcx') category = 'aic';
      else if (child.type === 'application/vnd.adobe.hz.express+dcx') category = 'express';
      else if (child.type === 'application/vnd.adobe.firefly-generation-image+dcx') category = 'ffgenimg';
      else if (child.type === 'application/vnd.adobe.firefly-generation-video+dcx') category = 'ffgenvid';
      else if (child.type === 'application/vnd.adobe.firefly-generation-audio+dcx') category = 'ffgenaud';
      else if (child.type?.includes('photoshop') || child.name?.endsWith('.psd')) category = 'psd';
      child.category = category;
      child.downloaded = false;
      child.failed = false;
      child.retryCount = 0;
      state.files.push(child);
      state.totalFiles++;
      state.totalBytes += child.size || 0;
    }
  }
}

/** Full scan: initialize session, traverse /cloud-content, emit summary. */
export async function scanAll() {
  // Reset all fields except status — status is already set by the message handler (C4 pattern).
  // Calling full resetState() would briefly revert to 'idle', causing badge/keepalive glitches.
  const preservedStatus = state.status;
  resetState();
  state.status = preservedStatus;
  // C4: Status may already be set synchronously by handler — idempotent
  if (state.status !== 'scanning') {
    state.status = 'scanning';
    events.emit('status_change', { status: 'scanning' });
  }

  try {
    await initialize();
    await saveProgress();

    events.emit('scan_start', {
      repositoryId: state.repositoryId,
      storageRegion: state.storageRegion,
    });

    // --- Primary scan: try /cloud-content ---
    let cloudContentError = null;
    const errorCapture = (entry) => {
      if (entry.event === 'scan_error' && (entry.path === '/cloud-content' || entry.path?.startsWith('/cloud-content/'))) {
        cloudContentError = entry.error;
      }
    };

    async function scanCloudContent() {
      cloudContentError = null;
      events.register(errorCapture);
      try {
        await scanFolder('/cloud-content');
      } finally {
        events.unregister(errorCapture);
      }
    }

    function checkStopped() {
      if (state.stopped) {
        state.status = 'stopped';
        events.emit('status_change', { status: 'stopped' });
        return true;
      }
      return false;
    }

    await scanCloudContent();
    if (checkStopped()) return;

    // --- Region resolve: if /cloud-content failed, ask the global resolver ---
    const originalRegion = state.storageRegion;
    if (state.files.length === 0 && cloudContentError) {
      events.emit('scan_fallback_triggered', {
        reason: 'cloud_content_404',
        error: cloudContentError,
      });

      const resolved = await resolveRegion(state.repositoryId, '/cloud-content');
      if (resolved && resolved.baseUrl !== state.platformBaseUrl) {
        state.storageRegion = resolved.region;
        state.platformBaseUrl = resolved.baseUrl;
        logDiagnostic({
          event: 'scan_region_resolved', level: 'WARN',
          data: { originalRegion, resolvedRegion: resolved.region, resolvedBaseUrl: resolved.baseUrl },
        });

        await scanCloudContent();
      } else if (resolved) {
        logDiagnostic({ event: 'scan_region_resolved', level: 'INFO',
          data: { sameRegion: true, region: resolved.region } });
      }
    }

    if (checkStopped()) return;

    // --- Region cycle: try remaining regions from /index ---
    if (state.regions.length > 1) {
      const tried = new Set([originalRegion, state.storageRegion].filter(Boolean));
      let lastTriedRegion = state.storageRegion;
      events.emit('scan_region_cycle_start', { regionsToTry: state.regions.length - 1, filesAlreadyFound: state.files.length });
      for (const alt of state.regions) {
        if (tried.has(alt)) continue;
        tried.add(alt);
        state.storageRegion = alt;
        state.platformBaseUrl = `https://platform-cs-edge-${alt.toLowerCase()}.adobe.io`;
        logDiagnostic({
          event: 'scan_region_cycle', level: 'WARN',
          data: { previousRegion: lastTriedRegion, tryingRegion: alt },
        });
        await scanCloudContent();
        lastTriedRegion = alt;
        if (state.stopped) break;
      }
      // After the for loop ends, restore original region
      state.storageRegion = originalRegion;
      state.platformBaseUrl = `https://platform-cs-edge-${originalRegion.toLowerCase()}.adobe.io`;
      // Deduplicate files by assetId
      const seenFiles = new Set();
      const dedupedFiles = [];
      let dedupedBytes = 0;
      for (const f of state.files) {
        if (seenFiles.has(f.assetId)) continue;
        seenFiles.add(f.assetId);
        dedupedFiles.push(f);
        dedupedBytes += f.size || 0;
      }
      // Deduplicate folders by path
      const seenFolders = new Set();
      const dedupedFolders = [];
      for (const d of state.folders) {
        if (seenFolders.has(d.path)) continue;
        seenFolders.add(d.path);
        dedupedFolders.push(d);
      }
      if (dedupedFiles.length < state.files.length || dedupedFolders.length < state.folders.length) {
        logDiagnostic({ event: 'scan_dedup', level: 'INFO',
          data: { filesBefore: state.files.length, filesAfter: dedupedFiles.length,
                  foldersBefore: state.folders.length, foldersAfter: dedupedFolders.length } });
        state.files = dedupedFiles;
        state.totalFiles = dedupedFiles.length;
        state.totalBytes = dedupedBytes;
        state.folders = dedupedFolders;
        state.totalFolders = dedupedFolders.length;
      }
    }

    if (checkStopped()) return;

    events.emit('scan_complete', {
      totalFiles: state.totalFiles,
      totalFolders: state.totalFolders,
      totalBytes: state.totalBytes,
    });

    // Persist files list and scan context to session storage for SW recovery
    try {
      await chrome.storage.session.set({
        [config.filesListKey]: state.files.map(f => ({
          assetId: f.assetId,
          name: f.name,
          path: f.path,
          type: f.type,
          size: f.size,
          category: f.category,
          region: f.region,
          modified: f.modified,
          version: f.version,
          downloaded: false,
          failed: false,
          retryCount: 0,
        })),
        [config.scanContextKey]: {
          repositoryId: state.repositoryId,
          storageRegion: state.storageRegion,
          platformBaseUrl: state.platformBaseUrl,
        },
      });
    } catch (e) {
      console.warn('[ABD] Failed to persist files list:', e.message);
      logDiagnostic({ event: 'scan_persist_failed', level: 'ERROR', data: { error: e?.message } });
    }

    // Emit summary lines
    const categoryLabel = { psdc: 'PSD', aic: 'AI', pdf: 'PDF', psd: 'PSD', express: 'Adobe Express', ffgenimg: 'Firefly Image', ffgenvid: 'Firefly Video', ffgenaud: 'Firefly Audio', other: 'Other' };
    events.emit('scan_summary_line', { message: `Total Size: ${formatBytes(state.totalBytes)}` });
    const cats = {};
    state.files.forEach((f) => {
      cats[f.category] = cats[f.category] || { count: 0, size: 0 };
      cats[f.category].count++;
      cats[f.category].size += f.size || 0;
    });
    events.emit('scan_summary_line', { message: '--- File Summary ---' });
    const sorted = Object.entries(cats).sort(([a], [b]) => (a === 'other') - (b === 'other'));
    for (const [cat, info] of sorted) {
      const label = categoryLabel[cat] || cat;
      events.emit('scan_summary_line', { message: `  ${label}: ${info.count} files (${formatBytes(info.size)})`, category: cat, count: info.count, size: info.size });
    }
    events.emit('scan_summary_line', { message: `  Folders: ${state.totalFolders}` });
    events.emit('scan_summary_line', { message: `  Total: ${state.totalFiles} files, ${formatBytes(state.totalBytes)}` });
    events.emit('scan_summary_line', { message: 'Click "Download All" to begin downloading.' });

    await saveProgress();
    state.status = 'scanned';
    events.emit('status_change', { status: 'scanned' });
  } catch (e) {
    state.status = 'error';
    events.emit('status_change', { status: 'error' });
    events.emit('scan_failed', { error: e.message });
  }
}
