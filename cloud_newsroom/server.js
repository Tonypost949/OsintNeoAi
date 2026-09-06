const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;
const STORIES_FILE = path.join(__dirname, 'data', 'newspaper_stories.json');
const CATALOG_FILE = path.join(__dirname, 'data', 'reports_catalog.json');

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Ensure data directory exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Helper to read stories
function getStories() {
  if (fs.existsSync(STORIES_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(STORIES_FILE, 'utf8'));
    } catch (e) {
      console.error('Error reading stories:', e);
    }
  }
  return [];
}

// API: System Status & Telemetry
app.get('/api/status', (req, res) => {
  res.json({
    service: "OsintNeoAi Cloud Newsroom",
    edition: "The Tax-Funded Dispatch",
    vm: "osintneoai-dev-vm",
    ip: "20.246.121.30",
    port: PORT,
    timestamp: new Date().toISOString(),
    status: "ONLINE",
    active_sources: [
      "Local Knowledge Graph",
      "Massive Library Catalog (7,803 records)",
      "Facebook Developer Tools & Open Graph",
      "Wayback Machine CDX API",
      "Kali Linux WSL2 Engine",
      "IRS Form 990 & USASpending",
      "LexisNexis Statutory Claims Calculator"
    ]
  });
});

// API: List Articles
app.get('/api/articles', (req, res) => {
  const stories = getStories();
  res.json({ count: stories.length, articles: stories });
});

// API: Publish New Article (from exhaustive_osint_engine or Power Apps)
app.post('/api/publish', (req, res) => {
  const payload = req.body;
  if (!payload || !payload.title) {
    return res.status(400).json({ error: "Missing required article title" });
  }

  const stories = getStories();
  const article = {
    id: payload.id || `DISP-${Math.floor(10000 + Math.random() * 90000)}`,
    title: payload.title,
    category: payload.category || "Investigative Audit",
    jurisdiction: payload.jurisdiction || "Public Ledger",
    published_at: payload.published_at || new Date().toISOString(),
    author: payload.author || "OsintNeoAi Forensic Engine",
    excerpt: payload.excerpt || "",
    statutory_notes: payload.statutory_notes || [],
    sources_exhausted: payload.sources_exhausted || [],
    raw_audit_file: payload.raw_audit_file || null
  };

  // Prepend to top of feed
  stories.unshift(article);
  fs.writeFileSync(STORIES_FILE, JSON.stringify(stories, null, 2), 'utf8');

  console.log(`[+] Published new article: ${article.title} (${article.id})`);
  res.status(201).json({ success: true, article });
});

// API: Evidence Catalog Summary
app.get('/api/catalog', (req, res) => {
  if (fs.existsSync(CATALOG_FILE)) {
    try {
      const cat = JSON.parse(fs.readFileSync(CATALOG_FILE, 'utf8'));
      return res.json(cat);
    } catch (e) {
      console.error(e);
    }
  }
  res.json({
    total_indexed: 7803,
    categories: {
      "legal_dossiers": 146,
      "evidence_datasets": 2084,
      "dashboards_and_maps": 478,
      "rag_chunks": 12
    }
  });
});

// Fallback to front page
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[+] Tax-Funded Dispatch Newsroom listening on port ${PORT}`);
});
