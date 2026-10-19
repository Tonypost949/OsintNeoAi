/**
 * OSINT Neo AI — Content Script (In-Page DOM & Metadata Extractor)
 */

(() => {
  // Listen for messages from popup or background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extract_metadata") {
      const ogTitle = document.querySelector('meta[property="og:title"]')?.content || "";
      const ogDesc = document.querySelector('meta[property="og:description"]')?.content || "";
      const metaDesc = document.querySelector('meta[name="description"]')?.content || "";
      const canonical = document.querySelector('link[rel="canonical"]')?.href || window.location.href;
      
      sendResponse({
        url: window.location.href,
        canonical: canonical,
        title: ogTitle || document.title,
        description: ogDesc || metaDesc,
        selection: window.getSelection().toString(),
        timestamp: new Date().toISOString()
      });
    }
  });
})();
