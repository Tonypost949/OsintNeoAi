chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "EXTRACT_ENTITIES") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: () => {
            if (window.DomainLearner) {
              const learner = new DomainLearner();
              const entities = learner.extractEntities(document);
              return { entities, url: window.location.href, title: document.title };
            }
            return { entities: [], url: window.location.href, title: document.title };
          },
        }, (results) => {
          sendResponse(results?.[0]?.result || { entities: [] });
        });
      }
    });
    return true;
  }
});
