/**
 * OSINT Neo AI — Evidence Collector Popup Controller
 */

async function sha256(text) {
  const msgUint8 = new TextEncoder().encode(text);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

let activeTabInfo = {
  url: '',
  title: '',
  selection: ''
};

// Switch Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.content-pane').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const tabId = btn.getAttribute('data-tab');
    document.getElementById(tabId).classList.add('active');
    if (tabId === 'tab-vault') loadVaultReceipts();
  });
});

async function initActiveTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      activeTabInfo.url = tab.url || '';
      activeTabInfo.title = tab.title || '';
      document.getElementById('page-title').textContent = activeTabInfo.title.substring(0, 35) + (activeTabInfo.title.length > 35 ? '...' : '');
      document.getElementById('page-url').textContent = activeTabInfo.url.substring(0, 40) + '...';
      
      const hash = await sha256(activeTabInfo.url + '|' + activeTabInfo.title);
      document.getElementById('page-hash').textContent = hash.substring(0, 16) + '...';

      // Get page selection if possible
      try {
        const results = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => window.getSelection().toString()
        });
        if (results && results[0] && results[0].result) {
          activeTabInfo.selection = results[0].result;
          document.getElementById('evidence-selection').value = activeTabInfo.selection;
        }
      } catch (e) {
        // Permission or internal page
      }
    }
  } catch (err) {
    document.getElementById('page-title').textContent = 'Unable to query tab';
  }
}

// Submit Evidence
document.getElementById('btn-submit-evidence').addEventListener('click', async () => {
  const statusEl = document.getElementById('status-msg');
  statusEl.className = '';
  statusEl.textContent = 'Submitting to Genesis ledger...';
  statusEl.style.display = 'block';

  const category = document.getElementById('evidence-category').value;
  const notes = document.getElementById('evidence-selection').value;
  const timestamp = new Date().toISOString();
  const rawData = `${activeTabInfo.url}|${activeTabInfo.title}|${category}|${notes}|${timestamp}`;
  const evidenceHash = await sha256(rawData);

  const payload = {
    url: activeTabInfo.url,
    title: activeTabInfo.title,
    category: category,
    evidence_text: notes,
    timestamp: timestamp,
    evidence_hash: evidenceHash,
    source: 'CHROME_EXTENSION_V2'
  };

  try {
    // Save to local storage vault
    const storageData = await chrome.storage.local.get(['osint_receipts']);
    const receipts = storageData.osint_receipts || [];
    receipts.unshift({
      ...payload,
      id: 'EVD-' + evidenceHash.substring(0, 8).toUpperCase()
    });
    await chrome.storage.local.set({ osint_receipts: receipts.slice(0, 50) });

    // Send payload to local API or Azure backend
    const endpoints = [
      'http://127.0.0.1:8000/api/genesis/ingest',
      'http://localhost:8000/api/genesis/ingest'
    ];
    let ingested = false;
    for (const ep of endpoints) {
      try {
        const res = await fetch(ep, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          ingested = true;
          break;
        }
      } catch (netErr) {}
    }

    statusEl.className = 'status-ok';
    statusEl.textContent = ingested
      ? `✅ Ingested & Hashed: ${evidenceHash.substring(0, 8)}...`
      : `✅ Vaulted Locally: ${evidenceHash.substring(0, 8)}...`;
  } catch (err) {
    statusEl.className = 'status-err';
    statusEl.textContent = '❌ Error saving receipt: ' + err.message;
  }
});

// Copy as Markdown
document.getElementById('btn-copy-markdown').addEventListener('click', async () => {
  const notes = document.getElementById('evidence-selection').value;
  const md = `### [OSINT Evidence] ${activeTabInfo.title}\n- **URL**: ${activeTabInfo.url}\n- **Date**: ${new Date().toISOString()}\n- **Notes**: ${notes || 'N/A'}\n`;
  await navigator.clipboard.writeText(md);
  const statusEl = document.getElementById('status-msg');
  statusEl.className = 'status-ok';
  statusEl.textContent = '📋 Markdown copied to clipboard!';
});

// Dump Window as JSON
document.getElementById('btn-dump-json').addEventListener('click', async () => {
  const tabs = await chrome.tabs.query({ currentWindow: true });
  const dump = tabs.map(t => ({ title: t.title, url: t.url, id: t.id }));
  await navigator.clipboard.writeText(JSON.stringify(dump, null, 2));
  document.getElementById('dump-count').textContent = `✅ Exported ${dump.length} tabs to clipboard (JSON)!`;
});

// Dump Window as Markdown
document.getElementById('btn-dump-markdown').addEventListener('click', async () => {
  const tabs = await chrome.tabs.query({ currentWindow: true });
  const md = tabs.map(t => `- [${t.title}](${t.url})`).join('\n');
  await navigator.clipboard.writeText(md);
  document.getElementById('dump-count').textContent = `✅ Exported ${tabs.length} tabs to clipboard (Markdown)!`;
});

// Load Vault Receipts
async function loadVaultReceipts() {
  const vaultEl = document.getElementById('receipts-list');
  const storageData = await chrome.storage.local.get(['osint_receipts']);
  const receipts = storageData.osint_receipts || [];
  if (receipts.length === 0) {
    vaultEl.innerHTML = '<div style="text-align:center; color:var(--text-muted); font-size:11px; padding:12px;">No receipts yet. Ingest evidence to generate cryptographic proofs.</div>';
    return;
  }
  vaultEl.innerHTML = receipts.map(r => `
    <div class="receipt-item">
      <div style="font-weight:600; color:var(--accent);">${r.id} · <span style="font-size:10px; color:var(--text-muted);">${r.category}</span></div>
      <div style="font-size:11px; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${r.title}</div>
      <div style="font-size:10px; font-family:monospace; color:var(--text-muted); margin-top:2px;">HASH: ${r.evidence_hash ? r.evidence_hash.substring(0, 18) + '...' : 'N/A'}</div>
    </div>
  `).join('');
}

document.addEventListener('DOMContentLoaded', initActiveTab);
