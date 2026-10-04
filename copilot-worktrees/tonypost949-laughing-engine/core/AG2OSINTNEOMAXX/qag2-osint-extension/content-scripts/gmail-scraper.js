// content-scripts/gmail-scraper.js
'use strict';

// RegExp patterns for threat indicators
const PATTERNS = {
  ip: /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g,
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  btc: /\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b/g,
  domain: /\b(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|gov|edu|mil|biz|info|io|xyz|ru|cn|ua)\b/gi,
  phone: /(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b/g
};

let scanTimeout = null;

// Extractor function
function extractIndicators() {
  // Check if context is invalidated
  if (!chrome.runtime || !chrome.runtime.id) {
    return;
  }

  const text = document.body.innerText || "";
  const results = {
    ips: [...new Set(text.match(PATTERNS.ip) || [])],
    emails: [...new Set(text.match(PATTERNS.email) || [])],
    btcAddresses: [...new Set(text.match(PATTERNS.btc) || [])],
    domains: [...new Set(text.match(PATTERNS.domain) || [])],
    phones: [...new Set(text.match(PATTERNS.phone) || [])]
  };

  // Convert all domain names to lowercase
  results.domains = results.domains.map(d => d.toLowerCase());

  // Filter out common false positives for domains
  const ignoreDomains = ['google.com', 'gmail.com', 'youtube.com', 'microsoft.com', 'apple.com', 'fonts.googleapis.com', 'gstatic.com'];
  results.domains = results.domains.filter(d => !ignoreDomains.includes(d));

  // Send to extension service worker / sidepanel
  try {
    chrome.runtime.sendMessage({
      type: 'EXTRACTED_INDICATORS',
      data: {
        url: window.location.href,
        title: document.title,
        results,
        timestamp: new Date().toISOString()
      }
    }).catch(() => {
      // Ignore runtime port disconnected errors
    });
  } catch (e) {
    // Catch extension context invalidated silently
  }
}

// Set up observer to scan Gmail dynamically when email loads
const observer = new MutationObserver(() => {
  // Disconnect if extension is reloaded/invalidated
  if (!chrome.runtime || !chrome.runtime.id) {
    observer.disconnect();
    return;
  }
  if (scanTimeout) clearTimeout(scanTimeout);
  scanTimeout = setTimeout(extractIndicators, 1500); // Debounce to prevent lag
});

// Start observer
observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Run once on load
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  extractIndicators();
} else {
  window.addEventListener('DOMContentLoaded', extractIndicators);
}
