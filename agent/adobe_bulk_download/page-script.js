// page-script.js — Runs in the PAGE context (not isolated world).
// Injected by content.js to access window.adobeIMS.

(function () {
  'use strict';

  function extractToken() {
    try {
      if (window.adobeIMS && typeof window.adobeIMS.getAccessToken === 'function') {
        const tokenInfo = window.adobeIMS.getAccessToken();
        if (tokenInfo && tokenInfo.token) {
          window.postMessage({
            type: 'ABD_TOKEN',
            token: tokenInfo.token,
            expiry: tokenInfo.expire || null,
          }, window.location.origin);
        }
      }
    } catch (err) {
      console.warn('[ABD page-script] Token extraction failed:', err.message);
    }
  }

  extractToken();
})();
