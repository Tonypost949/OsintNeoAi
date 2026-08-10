const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT_DIR, 'skills');
const CHANGES_LOG_ROOT = path.join(ROOT_DIR, '.changes.json');
const CHANGES_LOG_PUBLIC = path.join(ROOT_DIR, 'public', 'data', 'changes.json');
const EXTRACT_SCRIPT = path.join(__dirname, 'extract-skills.js');

const MAX_HISTORY = 100;

function loadChanges() {
  try {
    if (fs.existsSync(CHANGES_LOG_ROOT)) {
      return JSON.parse(fs.readFileSync(CHANGES_LOG_ROOT, 'utf8'));
    }
  } catch (err) {
    console.warn('[watcher] Warning reading changes log:', err.message);
  }
  return [];
}

function saveChanges(changes) {
  const payload = JSON.stringify(changes.slice(0, MAX_HISTORY), null, 2);
  fs.writeFileSync(CHANGES_LOG_ROOT, payload, 'utf8');
  
  const publicDataDir = path.dirname(CHANGES_LOG_PUBLIC);
  if (!fs.existsSync(publicDataDir)) {
    fs.mkdirSync(publicDataDir, { recursive: true });
  }
  fs.writeFileSync(CHANGES_LOG_PUBLIC, payload, 'utf8');
}

function logChange(eventType, filename) {
  if (!filename || filename.includes('.changes.json') || filename.includes('skills.json')) {
    return;
  }

  const changes = loadChanges();
  const entry = {
    id: 'chg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
    timestamp: new Date().toISOString(),
    event: eventType,
    file: filename.replace(/\\/g, '/'),
    skill: filename.split(/[\\\/]/)[0] || 'root'
  };

  changes.unshift(entry);
  saveChanges(changes);
  console.log(`[watcher] [${entry.timestamp}] [${eventType.toUpperCase()}] ${filename}`);
}

let debounceTimer = null;
function triggerExtraction() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    console.log('[watcher] Triggering automatic skills re-extraction...');
    exec(`node "${EXTRACT_SCRIPT}"`, (error, stdout, stderr) => {
      if (error) {
        console.error('[watcher] Extraction failed:', error.message);
        return;
      }
      if (stdout) console.log(stdout.trim());
      if (stderr) console.error(stderr.trim());
    });
  }, 400);
}

function startWatching() {
  console.log('=====================================================');
  console.log('  OsintNeoAi Skills File Watcher Active');
  console.log(`  Watching directory: ${SKILLS_DIR}`);
  console.log(`  Logging changes to: .changes.json & public/data/changes.json`);
  console.log('=====================================================');

  if (!fs.existsSync(SKILLS_DIR)) {
    fs.mkdirSync(SKILLS_DIR, { recursive: true });
  }

  // Initial extract
  exec(`node "${EXTRACT_SCRIPT}"`, (err, stdout) => {
    if (stdout) console.log(stdout.trim());
  });

  // Watch skills folder
  try {
    fs.watch(SKILLS_DIR, { recursive: true }, (eventType, filename) => {
      if (filename) {
        logChange(eventType, filename);
        triggerExtraction();
      }
    });
  } catch (e) {
    console.error('[watcher] Native recursive watch error:', e.message);
  }
}

// Support direct CLI invocation
if (require.main === module) {
  startWatching();
}

module.exports = { startWatching, logChange, loadChanges };
