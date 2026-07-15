// eta.js — ETA calculator with three-bucket EMA model (ES module).
// Spec §13: classifies files at scan time, self-corrects as downloads proceed.

import { events } from './events.js';

// --- Seed constants (§13.2 calibration data) ---

const SEEDS = {
  non_psdc:    { avg: 1000,  optRatio: 0.40,  pessRatio: 1.50 },
  psdc_direct: { avg: 8500,  optRatio: 0.918, pessRatio: 1.00 },
  psdc_fb:     { avg: 18300, optRatio: 0.689, pessRatio: 0.923 },
};

const PSDC_SIZE_THRESHOLD = 10_000_000; // 10 MB decimal

// EMA constants
const ALPHA = 0.8; // existing average weight
const BETA  = 1 - ALPHA; // new observation weight
const DAMPEN_OLD = 0.7;
const DAMPEN_NEW = 1 - DAMPEN_OLD;

// --- Internal state ---

let buckets = _freshBuckets();
let concurrency = 1;
let completedFiles = 0;
let totalFiles = 0;
let displayedETA = null; // null = first call
let _lastResult = null;
let _dirty = true;

function _freshBuckets() {
  return {
    non_psdc:    { avg: SEEDS.non_psdc.avg,    remaining: 0, count: 0 },
    psdc_direct: { avg: SEEDS.psdc_direct.avg, remaining: 0, count: 0 },
    psdc_fb:     { avg: SEEDS.psdc_fb.avg,     remaining: 0, count: 0 },
  };
}

// --- Classification ---

export function classifyFile(file) {
  if (file.category === 'psdc') {
    return (file.size || 0) < PSDC_SIZE_THRESHOLD ? 'psdc_direct' : 'psdc_fb';
  }
  return 'non_psdc';
}

// --- Friendly rounding ---

const STEPS = [
  1, 2, 3, 5, 10, 15, 20, 30, 45, 50, 60, 90, 120,
];

function _friendlyRound(ms) {
  const minutes = ms / 60000;
  if (minutes <= 0) return null;

  for (const step of STEPS) {
    if (step <= 60 && minutes <= step) {
      return step === 60 ? '1 hour' : `${step} min`;
    }
    if (step === 90 && minutes <= 90) return '1.5 hours';
    if (step === 120 && minutes <= 120) return '2 hours';
  }
  return `${Math.ceil(minutes / 60)} hours`;
}

// --- Core calculation ---

function _recalculate() {
  let workMs = 0;
  let optMs = 0;
  let pessMs = 0;
  let totalRemaining = 0;

  for (const [key, b] of Object.entries(buckets)) {
    workMs += b.remaining * b.avg;
    optMs  += b.remaining * b.avg * SEEDS[key].optRatio;
    pessMs += b.remaining * b.avg * SEEDS[key].pessRatio;
    totalRemaining += b.remaining;
  }

  const rawEta = concurrency > 0 ? workMs / concurrency : 0;
  const optimisticMs = concurrency > 0 ? optMs / concurrency : 0;
  const pessimisticMs = concurrency > 0 ? pessMs / concurrency : 0;

  if (displayedETA === null) {
    displayedETA = rawEta;
  } else {
    displayedETA = (DAMPEN_OLD * displayedETA) + (DAMPEN_NEW * rawEta);
  }

  const friendly = _friendlyRound(displayedETA);
  const displayText = totalRemaining === 0
    ? 'Finishing up\u2026'
    : friendly
      ? `less than ${friendly} remaining`
      : 'Finishing up\u2026';

  if (completedFiles > totalFiles && totalFiles > 0) {
    events.emit('eta_invariant_violation', {
      completedFiles,
      totalFiles,
      delta: completedFiles - totalFiles,
    });
  }

  _lastResult = {
    phaseLabel: 'Downloading files\u2026',
    etaMs: displayedETA,
    optimisticMs,
    pessimisticMs,
    displayText,
    completedFiles,
    totalFiles,
    percent: totalFiles > 0
      ? Math.min(100, Math.max(0, Math.floor((Math.min(completedFiles, totalFiles) / totalFiles) * 100)))
      : 0,
  };
  _dirty = false;

  return _lastResult;
}

// --- Exported API ---

export function initializeETA(files, conc) {
  buckets = _freshBuckets();
  concurrency = Math.max(1, conc || 1);
  completedFiles = 0;
  totalFiles = files.length;
  displayedETA = null;
  _dirty = true;
  _lastResult = null;

  for (const f of files) {
    if (f.downloaded) {
      completedFiles++;
      continue;
    }
    const bucket = classifyFile(f);
    buckets[bucket].remaining++;
  }
}

export function onFileSuccess(entry) {
  const bucket = classifyFile(entry);
  const b = buckets[bucket];
  if (b.remaining > 0) b.remaining--;
  completedFiles++;

  // EMA update if we have a duration
  if (entry.duration_ms != null && entry.duration_ms > 0 && Number.isFinite(entry.duration_ms)) {
    const clamped = Math.min(entry.duration_ms, b.avg * 10);
    b.avg = (ALPHA * b.avg) + (BETA * clamped);
    b.count++;
  }

  _dirty = true;
  const data = _recalculate();
  events.emit('eta_update', data);
}

export function onFileFail(entry) {
  const bucket = classifyFile(entry);
  const b = buckets[bucket];
  if (b.remaining > 0) b.remaining--;
  completedFiles++;

  _dirty = true;
  const data = _recalculate();
  events.emit('eta_update', data);
}

export function getDisplayData() {
  if (_dirty) _recalculate();
  return _lastResult;
}

export function serializeState() {
  return {
    buckets: {
      non_psdc:    { avg: buckets.non_psdc.avg,    count: buckets.non_psdc.count },
      psdc_direct: { avg: buckets.psdc_direct.avg, count: buckets.psdc_direct.count },
      psdc_fb:     { avg: buckets.psdc_fb.avg,     count: buckets.psdc_fb.count },
    },
    completedFiles,
    displayedETA,
  };
}

export function restoreState(data) {
  if (!data?.buckets) return;
  for (const key of Object.keys(buckets)) {
    if (data.buckets[key]) {
      const restored = data.buckets[key].avg;
      if (typeof restored === 'number' && Number.isFinite(restored) && restored > 0) {
        buckets[key].avg = restored;
      }
      const cnt = data.buckets[key].count;
      if (typeof cnt === 'number' && Number.isFinite(cnt) && cnt >= 0) {
        buckets[key].count = Math.floor(cnt);
      }
    }
  }
  if (data.completedFiles != null) completedFiles = data.completedFiles;
  if (data.displayedETA != null && Number.isFinite(data.displayedETA)) displayedETA = data.displayedETA;
}

export function resetETA() {
  buckets = _freshBuckets();
  concurrency = 1;
  completedFiles = 0;
  totalFiles = 0;
  displayedETA = null;
  _dirty = true;
  _lastResult = null;
}
