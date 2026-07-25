// sidepanel/panel.js
'use strict';

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize Tab switching
  setupTabs();

  // Initialize Scanner functionality
  await initScanner();

  // Initialize Dorking Generator
  initDorkGenerator();

  // Initialize Leak Intel Lookup
  initLeakIntel();

  // Initialize Profile and Configuration
  await initProfileSettings();
});

// 1. Tab Navigation Routing
function setupTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Deactivate current active tab
      document.querySelector('.tab-btn.active').classList.remove('active');
      document.querySelector('.panel.active').classList.remove('active');

      // Activate clicked tab
      tab.classList.add('active');
      const targetPanel = tab.getAttribute('data-tab');
      document.getElementById(targetPanel).classList.add('active');
    });
  });
}

// 2. Active Page Scanner
async function initScanner() {
  const scanTimeEl = document.getElementById('scan-time');
  const scannedUrlEl = document.getElementById('scanned-url');
  const emptyStateEl = document.getElementById('no-indicators');

  // Load from local storage initially
  const data = await chrome.storage.local.get(['lastExtracted', 'lastSelection']);
  if (data.lastExtracted) {
    displayIndicators(data.lastExtracted);
  }

  if (data.lastSelection) {
    // If we have a selection from context menu, load into dork query automatically
    document.getElementById('dork-query').value = data.lastSelection;
    updateDorkPreview();
  }

  // Listen for message broadcasts from service worker or content scripts
  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'EXTRACTED_INDICATORS') {
      displayIndicators(message.data);
    } else if (message.type === 'NEW_INDICATOR') {
      // Focus dork tab and prefill
      document.getElementById('tab-dorks').click();
      document.getElementById('dork-query').value = message.data;
      updateDorkPreview();
    }
  });

  function displayIndicators(info) {
    if (!info || !info.results) return;

    scanTimeEl.textContent = new Date(info.timestamp).toLocaleTimeString();
    scannedUrlEl.textContent = info.url || "Unknown Source";

    const { ips = [], emails = [], domains = [], phones = [], btcAddresses = [] } = info.results;
    const totalCount = ips.length + emails.length + domains.length + phones.length + btcAddresses.length;

    if (totalCount === 0) {
      emptyStateEl.classList.remove('hidden');
      toggleWrapper('ips-wrapper', false);
      toggleWrapper('emails-wrapper', false);
      toggleWrapper('domains-wrapper', false);
      toggleWrapper('phones-wrapper', false);
      toggleWrapper('btc-wrapper', false);
      return;
    }

    emptyStateEl.classList.add('hidden');

    renderIndicatorList('ips', ips, '🌐 IP Address');
    renderIndicatorList('emails', emails, '✉️ Email');
    renderIndicatorList('domains', domains, '🔗 Domain');
    renderIndicatorList('phones', phones, '📞 Phone');
    renderIndicatorList('btc', btcAddresses, '🪙 BTC Addr');
  }

  function renderIndicatorList(key, items, label) {
    const wrapper = document.getElementById(`${key}-wrapper`);
    const countEl = document.getElementById(`${key}-count`);
    const listEl = document.getElementById(`${key}-list`);

    if (items.length === 0) {
      toggleWrapper(`${key}-wrapper`, false);
      return;
    }

    toggleWrapper(`${key}-wrapper`, true);
    countEl.textContent = items.length;
    listEl.innerHTML = '';

    items.forEach(item => {
      const chip = document.createElement('div');
      chip.className = 'indicator-chip';

      const textNode = document.createElement('span');
      textNode.className = 'chip-text';
      textNode.textContent = item;

      const actions = document.createElement('div');
      actions.className = 'chip-actions';

      const copyBtn = document.createElement('button');
      copyBtn.className = 'btn chip-btn';
      copyBtn.textContent = '📋 Copy';
      copyBtn.addEventListener('click', async () => {
        await navigator.clipboard.writeText(item);
        copyBtn.textContent = '✅ Copied';
        setTimeout(() => { copyBtn.textContent = '📋 Copy'; }, 1500);
      });

      const dorkBtn = document.createElement('button');
      dorkBtn.className = 'btn chip-btn btn-secondary';
      dorkBtn.textContent = '🔬 Dork';
      dorkBtn.addEventListener('click', () => {
        document.getElementById('tab-dorks').click();
        document.getElementById('dork-query').value = item;
        updateDorkPreview();
      });

      actions.appendChild(copyBtn);
      actions.appendChild(dorkBtn);
      chip.appendChild(textNode);
      chip.appendChild(actions);
      listEl.appendChild(chip);
    });
  }

  function toggleWrapper(id, show) {
    const el = document.getElementById(id);
    if (show) el.classList.remove('hidden');
    else el.classList.add('hidden');
  }
}

// 3. Google Dorking Engine
function initDorkGenerator() {
  const queryInput = document.getElementById('dork-query');
  const previewText = document.getElementById('dork-preview-text');
  const launchBtn = document.getElementById('btn-generate-dork');

  const checkboxes = [
    'chk-pdf', 'chk-xls', 'chk-gov', 'chk-edu', 'chk-leak', 'chk-pass'
  ];

  // Update preview on inputs change
  queryInput.addEventListener('input', updateDorkPreview);
  checkboxes.forEach(id => {
    document.getElementById(id).addEventListener('change', updateDorkPreview);
  });

  launchBtn.addEventListener('click', () => {
    const dorkQuery = generateDorkQuery();
    if (!dorkQuery.trim()) return;
    
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(dorkQuery)}`;
    chrome.tabs.create({ url: searchUrl });
  });

  window.updateDorkPreview = updateDorkPreview; // expose globally
}

function generateDorkQuery() {
  const baseTerm = document.getElementById('dork-query').value.trim();
  if (!baseTerm) return "";

  let parts = [`"${baseTerm}"`];

  const filetypes = [];
  if (document.getElementById('chk-pdf').checked) filetypes.push('pdf');
  if (document.getElementById('chk-xls').checked) filetypes.push('xls', 'xlsx', 'csv');

  if (filetypes.length > 0) {
    if (filetypes.length === 1) {
      parts.push(`filetype:${filetypes[0]}`);
    } else {
      parts.push(`(filetype:${filetypes.join(' OR filetype:')})`);
    }
  }

  const sites = [];
  if (document.getElementById('chk-gov').checked) sites.push('gov');
  if (document.getElementById('chk-edu').checked) sites.push('edu');

  if (sites.length > 0) {
    if (sites.length === 1) {
      parts.push(`site:${sites[0]}`);
    } else {
      parts.push(`(site:${sites.join(' OR site:')})`);
    }
  }

  if (document.getElementById('chk-leak').checked) {
    parts.push('(intext:leak OR intext:dump OR intext:exfiltrated)');
  }

  if (document.getElementById('chk-pass').checked) {
    parts.push('(intext:password OR intext:credentials OR intext:login)');
  }

  return parts.join(' ');
}

function updateDorkPreview() {
  const dorkQuery = generateDorkQuery();
  const previewText = document.getElementById('dork-preview-text');
  previewText.textContent = dorkQuery || "[Please enter a search term]";
}

// 4. Leak Intel Lookups
function initLeakIntel() {
  const searchInput = document.getElementById('intel-search-input');
  const searchBtn = document.getElementById('intel-search-btn');
  const cards = document.querySelectorAll('.intel-card');

  function filterCards() {
    const q = searchInput.value.toLowerCase().trim();
    cards.forEach(card => {
      const keywords = card.getAttribute('data-keywords').toLowerCase();
      const title = card.querySelector('h3').textContent.toLowerCase();
      const desc = card.querySelector('p').textContent.toLowerCase();

      if (!q || keywords.includes(q) || title.includes(q) || desc.includes(q)) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  }

  searchInput.addEventListener('input', filterCards);
  searchBtn.addEventListener('click', filterCards);
}

// 5. Profile Settings Config
async function initProfileSettings() {
  const saveBtn = document.getElementById('btn-save-profile');
  const emailInput = document.getElementById('override-profile');
  const badgeNameEl = document.getElementById('active-profile-name');
  const textDisplayEl = document.getElementById('profile-text-display');

  // Load saved profile override
  const data = await chrome.storage.local.get(['profileOverride']);
  const defaultProfile = data.profileOverride || "amd949609@gmail.com";

  emailInput.value = defaultProfile;
  badgeNameEl.textContent = defaultProfile;
  textDisplayEl.textContent = `${defaultProfile} (Custom Override)`;

  saveBtn.addEventListener('click', async () => {
    const newEmail = emailInput.value.trim();
    if (!newEmail) return;

    await chrome.storage.local.set({ profileOverride: newEmail });
    badgeNameEl.textContent = newEmail;
    textDisplayEl.textContent = `${newEmail} (Custom Override)`;
    
    saveBtn.textContent = '💾 Saved!';
    setTimeout(() => { saveBtn.textContent = '💾 Save Profile Target'; }, 1500);
  });
}
