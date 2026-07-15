// content.js — Content script (isolated world).
// Injects page-script.js into the page context and relays tokens to the service worker.

if (window.__abd_content_loaded) { /* skip */ } else {
window.__abd_content_loaded = true;

(function () {
  'use strict';

  const POLL_INTERVAL_MS = 1_000;

  /** Inject page-script.js into the host page so it can access window.adobeIMS. */
  function injectPageScript() {
    if (!chrome.runtime?.id) return;
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('page-script.js');
    script.onload = () => script.remove();
    script.onerror = () => console.warn('[ABD content] page-script injection failed');
    (document.head || document.documentElement).appendChild(script);
  }

  /** Listen for token messages from the injected page script. */
  window.addEventListener('message', (event) => {
    if (event.source !== window) return;
    if (!event.data || event.data.type !== 'ABD_TOKEN') return;
    if (!chrome.runtime?.id) return;

    chrome.runtime.sendMessage({
      type: 'ABD_TOKEN',
      token: event.data.token,
      expiry: event.data.expiry,
    }).catch(() => {}); // SW may be dead — token picked up on next poll cycle
  });

  // Initial injection
  injectPageScript();

  // Poll for token refreshes
  setInterval(injectPageScript, POLL_INTERVAL_MS);
})();

} // end duplicate-injection guard
