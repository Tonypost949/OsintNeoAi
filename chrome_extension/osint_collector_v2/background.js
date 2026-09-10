/**
 * OSINT Neo AI — Background Service Worker (Manifest V3)
 */

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "osint-capture-selection",
    title: "⚡ Send Selection to OSINT Evidence Ledger",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "osint-capture-page",
    title: "📑 Capture Entire Page to Genesis Wiki",
    contexts: ["page"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const timestamp = new Date().toISOString();
  let textToHash = "";
  let payload = {};

  if (info.menuItemId === "osint-capture-selection" && info.selectionText) {
    textToHash = `${tab.url}|${tab.title}|${info.selectionText}|${timestamp}`;
    payload = {
      url: tab.url,
      title: tab.title,
      category: "CONTEXT_MENU_SELECTION",
      evidence_text: info.selectionText,
      timestamp: timestamp,
      source: "CHROME_CONTEXT_MENU"
    };
  } else if (info.menuItemId === "osint-capture-page") {
    textToHash = `${tab.url}|${tab.title}|FULL_PAGE|${timestamp}`;
    payload = {
      url: tab.url,
      title: tab.title,
      category: "FULL_PAGE_CAPTURE",
      evidence_text: tab.title,
      timestamp: timestamp,
      source: "CHROME_CONTEXT_MENU"
    };
  }

  if (textToHash) {
    // Generate SHA-256
    const msgUint8 = new TextEncoder().encode(textToHash);
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hash = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
    payload.evidence_hash = hash;
    payload.id = "EVD-" + hash.substring(0, 8).toUpperCase();

    // Store in chrome.storage
    const storage = await chrome.storage.local.get(["osint_receipts"]);
    const receipts = storage.osint_receipts || [];
    receipts.unshift(payload);
    await chrome.storage.local.set({ osint_receipts: receipts.slice(0, 50) });

    // Update badge
    chrome.action.setBadgeText({ text: "✓" });
    chrome.action.setBadgeBackgroundColor({ color: "#22c55e" });
    setTimeout(() => {
      chrome.action.setBadgeText({ text: "" });
    }, 2500);

    // Forward to local API endpoint if reachable
    try {
      fetch("http://127.0.0.1:8000/api/genesis/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).catch(() => {});
    } catch (e) {}
  }
});

chrome.commands.onCommand.addListener(async (command) => {
  if (command === "capture-active-tab") {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      chrome.action.openPopup();
    }
  }
});
