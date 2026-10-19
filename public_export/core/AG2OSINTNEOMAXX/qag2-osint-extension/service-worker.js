// service-worker.js
'use strict';

// Open side panel on extension action click (with safety guard)
if (typeof chrome !== 'undefined' && chrome.sidePanel && typeof chrome.sidePanel.setPanelBehavior === 'function') {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true })
    .catch((error) => console.error('Error setting panel behavior:', error));
}

// Create Context Menus
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'analyze-indicator',
    title: 'Analyze indicator "%s" with QAG2',
    contexts: ['selection']
  });
});

// Handle Context Menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'analyze-indicator' && info.selectionText) {
    const query = info.selectionText.trim();
    
    // Open the side panel immediately to preserve the user gesture (with safety guard)
    if (chrome.sidePanel && typeof chrome.sidePanel.open === 'function') {
      chrome.sidePanel.open({ windowId: tab.windowId }).catch((err) => {
        console.error('Failed to open side panel via context menu:', err);
      });
    }
    
    // Save to storage and notify sidepanel asynchronously
    chrome.storage.local.set({ lastSelection: query }).then(() => {
      chrome.runtime.sendMessage({ type: 'NEW_INDICATOR', data: query }).catch(() => {
        // Ignore error if sidepanel is not open yet
      });
    });
  }
});

// Listen for content script indicators
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'EXTRACTED_INDICATORS') {
    // Save to session or local storage
    chrome.storage.local.set({ lastExtracted: message.data });
  }
});
