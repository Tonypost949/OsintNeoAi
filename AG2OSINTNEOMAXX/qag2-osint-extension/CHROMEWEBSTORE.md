# CHROMEWEBSTORE.md — QAG2 OSINT & Gmail Companion Listing

This document is the Single Source of Truth (SSoT) for the Chrome Web Store (CWS) submission of the **QAG2 OSINT & Gmail Companion** extension.

---

## 1. Store Listing Metadata

* **Extension Name**: QAG2 OSINT & Gmail Companion
* **Detailed Description**:
  The QAG2 OSINT & Gmail Companion is a premium, state-of-the-art sidebar designed for threat intelligence analysts and local forensic investigators. 
  
  Equipped with real-time indicator extraction and advanced search utilities, this extension allows you to:
  - **Auto-scrape Threat Indicators**: Extract IP addresses, emails, phone numbers, and BTC addresses in real-time as you browse web pages or Gmail threads, bypassing complex OAuth setup.
  - **Generate Advanced Google Dorks**: Instantly construct and launch targeted search-operator queries (e.g. site overrides, specific filetypes like PDF/XLS, leak mentions) directly from the sidebar.
  - **Cross-reference Leak Indexes**: Query and match local metadata indexes for investigative targets.
  - **Manage Local Target Sessions**: Track the active profile target session to ensure correct data correlation.

* **Summary / One-line Description**:
  Premium sidebar companion to scrape threat indicators, perform custom Google Dorks, and assist active investigations.

* **Category**: Productivity / Developer Tools

---

## 2. Permissions Justification

Every permission and host permission declared in `manifest.json` is justified below for review by the Chrome Web Store team:

| Permission / Host | Specific Plain-English Justification |
|-------------------|--------------------------------------|
| `sidePanel`       | Required to render the persistent, feature-rich investigator sidebar interface beside Gmail and web pages. |
| `activeTab`       | Required to capture the metadata (URL, Title) of the user's active tab to contextually correlate extracted threat indicators. |
| `scripting`       | Required to dynamically coordinate indicator-scraper functions with active pages when requested. |
| `storage`         | Required to save and persist target profile settings, custom queries, and extracted indicators across sessions. |
| `tabs`            | Required to launch new query tabs when opening advanced Google Dork links. |
| `contextMenus`    | Required to add a right-click search option allowing investigators to highlight text and instantly dork/analyze it via the sidebar. |
| `*://mail.google.com/*` | Required to inject the threat indicator scraper into Gmail threads to extract indicators without requiring OAuth access tokens. |
| `*://*.google.com/*`   | Required to execute automated search dorks and index relevant public threat findings. |

---

## 3. Privacy & Data Use Disclosures

* **Data Collection**: No personal information, user accounts, browser history, or communication logs are ever collected or exfiltrated.
* **Local Processing**: All threat indicator parsing (regular expression matching) and dork query generation are executed strictly locally on your machine within the sandboxed extension context.
* **Data Storage**: Session states (saved overrides, last extracted elements) are stored locally in `chrome.storage.local` and never transmitted to external servers.

---

## 4. Version History

### Version 1.0.0 (2026-07-01)
- Initial release containing:
  - Real-time indicator extraction from Gmail/web pages.
  - Custom Google Dorking generator with interactive checkboxes.
  - Interactive mock threat leak database index for target lookups.
  - Chrome profile setting guidelines and active account session display.
