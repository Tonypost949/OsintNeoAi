/**
 * autonomous_notebook_extractor.js — Zero-Touch Autonomous NotebookLM Evidence Extractor
 * Powered by TabCopy Universal DOM Ripper and Puppeteer
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const CATALOG_PATH = path.join(__dirname, '..', 'data', 'all_42_notebooklm_urls.json');
const OUTPUT_DIR = path.join(__dirname, '..', 'data', 'filtered_chats');
const EXTRACTED_DIR = path.join(__dirname, '..', 'data', 'chats', 'notebooks', 'extracted');

// Common Windows Chrome paths
const CHROME_PATHS = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  path.join(process.env.LOCALAPPDATA || '', 'Google', 'Chrome', 'Application', 'chrome.exe')
];

function getChromeExecutable() {
  for (const p of CHROME_PATHS) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

async function main() {
  console.log('='.repeat(65));
  console.log('  AUTONOMOUS NOTEBOOKLM BATCH EVIDENCE EXTRACTOR (ZERO-TOUCH)');
  console.log('='.repeat(65));

  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  if (!fs.existsSync(EXTRACTED_DIR)) fs.mkdirSync(EXTRACTED_DIR, { recursive: true });

  const catalog = JSON.parse(fs.readFileSync(CATALOG_PATH, 'utf8'));
  const notebooks = catalog.notebooks || [];
  console.log(`[*] Loaded ${notebooks.length} total notebook targets.`);

  const chromePath = getChromeExecutable();
  if (!chromePath) {
    console.error('[!] Chrome executable not found on system.');
    process.exit(1);
  }

  // Use user data directory to maintain existing logged in session
  const userDataDir = path.join(process.env.LOCALAPPDATA || '', 'Google', 'Chrome', 'User Data');
  console.log(`[*] Launching Chrome with profile: ${userDataDir}`);

  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: chromePath,
      userDataDir: userDataDir,
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu'
      ]
    });
  } catch (err) {
    console.log(`[*] Headless launch notice (${err.message}). Retrying with isolated session...`);
    browser = await puppeteer.launch({
      executablePath: chromePath,
      headless: true,
      args: ['--no-sandbox']
    });
  }

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  let successCount = 0;

  for (let i = 0; i < notebooks.length; i++) {
    const nb = notebooks[i];
    const safeTitle = nb.title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    console.log(`\n[${i + 1}/${notebooks.length}] Extracting: ${nb.title}...`);
    console.log(`  URL: ${nb.url}`);

    try {
      await page.goto(nb.url, { waitUntil: 'networkidle2', timeout: 30000 });
      await new Promise(r => setTimeout(r, 2000)); // Allow dynamic Angular DOM to settle

      // Inject TabCopy Universal DOM Ripper
      const evidence = await page.evaluate(() => {
        const rawText = document.body ? document.body.innerText : '';
        const tables = Array.from(document.querySelectorAll('table')).map(t => t.outerHTML);
        const links = Array.from(document.querySelectorAll('a')).map(a => a.href);
        const documentLinks = links.filter(href => href.toLowerCase().endsWith('.pdf') || href.toLowerCase().endsWith('.docx'));
        
        // Extract Studio notes and cards
        const noteCards = Array.from(document.querySelectorAll('[data-note-id], .note-card, .studio-card, .source-item'))
          .map(el => el.innerText.trim());

        return {
          title: document.title,
          url: window.location.href,
          timestamp: new Date().toISOString(),
          raw_text: rawText,
          notes_and_cards: noteCards,
          tables: tables,
          ocr_targets: [...new Set(documentLinks)]
        };
      });

      // Save structured JSON
      const jsonOut = path.join(EXTRACTED_DIR, `${safeTitle}_${nb.uuid}.json`);
      fs.writeFileSync(jsonOut, JSON.stringify(evidence, null, 2), 'utf8');

      // Save clean text for ingestion & LLM search
      const txtOut = path.join(OUTPUT_DIR, `${safeTitle}_clean.txt`);
      const txtContent = [
        `# ${nb.title}`,
        `URL: ${nb.url}`,
        `UUID: ${nb.uuid}`,
        `Timestamp: ${evidence.timestamp}`,
        `\n## Notes & Studio Cards:\n${evidence.notes_and_cards.join('\n\n')}`,
        `\n## Full Extracted Text:\n${evidence.raw_text}`
      ].join('\n');

      fs.writeFileSync(txtOut, txtContent, 'utf8');
      console.log(`  [✓] Saved clean text (${evidence.raw_text.length} chars) -> ${path.basename(txtOut)}`);
      successCount++;
    } catch (err) {
      console.log(`  [!] Error extracting ${nb.title}: ${err.message}`);
    }
  }

  await browser.close();
  console.log(`\n[+] Extraction complete: ${successCount}/${notebooks.length} notebooks successfully extracted.`);
}

main().catch(err => {
  console.error('[!] Fatal error in extractor:', err);
  process.exit(1);
});
