---
name: osint
description: Complete multi-vector OSINT investigation toolchain integrating OSINT Cabal Live Center (30+ real-time tools), credential breach monitoring, entity reconnaissance, social network footprinting, and forensic domain intelligence.
---

# 🕵️ Multi-Vector OSINT Investigation & Intelligence Framework

This skill guides the selection and deployment of open-source intelligence (OSINT) tools and methods from the **OSINT Cabal Live Center** (`https://osintcabal.org/livecenter/live.html`) and external repositories for verifying entities, emails, usernames, domains, and data leaks.

---

## 1. Email Reconnaissance & Identity Verification

| Tool | Capability & Investigation Purpose | Live Endpoint / Method |
| :--- | :--- | :--- |
| **Zehef** | Cross-checks email registration across 18+ social media platforms and initial breach indicators. | `https://osintcabal.org/livecenter/zehef.html` |
| **Holehe** | Deep social media account detection across 120+ sites without notifying target. | `https://osintcabal.org/livecenter/holehe.html` |
| **Mailsleuth** | Comprehensive social presence scanner by email. | `https://osintcabal.org/livecenter/mailsleuth.html` |
| **Mailcat** | Scrapes for username handles matching domain aliases. | `https://osintcabal.org/livecenter/mailcat.html` |
| **Email Validator** | Verifies MX records, server responsiveness, SMTP handshakes, and creation metadata. | `https://osintcabal.org/livecenter/emailvalidator.html` |
| **Eyes** | Advanced social reconnaissance tool for aggregating linked email identities. | `https://osintcabal.org/livecenter/eyes.html` |
| **Hashtray** | Identifies Gravatar profiles and MD5 hashes associated with email addresses. | `https://osintcabal.org/livecenter/hashtray.html` |
| **Blackbird** | Executes multi-platform email and account correlation modules. | `https://osintcabal.org/livecenter/blackbird.html` |
| **Hunter.io** | Domain-based corporate email pattern discovery and employee address extraction. | `https://osintcabal.org/livecenter/Hunterio.html` |
| **Proton Intelligence** | Reconnaissance on ProtonMail keys, creation date ranges, and public PGP keys. | `https://osintcabal.org/livecenter/protonintelligence.html` |

---

## 2. Web, Domain & Network Infrastructure Intelligence

| Tool | Capability & Investigation Purpose | Live Endpoint / Method |
| :--- | :--- | :--- |
| **Webdiver** | Deep website crawling, technology stack discovery, and structural asset extraction. | `https://osintcabal.org/livecenter/webdiver.html` |
| **Subcat** | Passive multi-source subdomain discovery and DNS aggregation. | `https://osintcabal.org/livecenter/subcat.html` |
| **FinalRecon** | All-in-one web reconnaissance (SSL info, WHOIS, DNS, headers, crawl maps). | `https://osintcabal.org/livecenter/finalrecon.html` |
| **The Harvester** | Gathers emails, names, subdomains, IPs, and open ports from public search engines. | `https://osintcabal.org/livecenter/theharvester.html` |
| **Sublist3r** | Subdomain brute-forcing and multi-engine enumeration. | `https://osintcabal.org/livecenter/sublist3r.html` |
| **ASN Lookup** | Autonomous System Number routing, BGP prefixes, and IP range identification. | `https://osintcabal.org/livecenter/asn.html` |
| **Webcheck** | Comprehensive security headers, TLS posture, server location, and DNS telemetry. | `https://osintcabal.org/livecenter/webcheck.html` |
| **Proxy / VPN Checker** | Queries IP risk scores, detecting commercial VPNs, proxies, and Tor exit nodes. | `https://osintcabal.org/livecenter/proxyvpnchecker.html` |
| **Darkus** | Deep/dark web search engine querying Tor/Onion hidden services. | `https://osintcabal.org/livecenter/darkus.html` |

---

## 3. Breach, Leak & Credential Monitoring

| Tool | Capability & Investigation Purpose | Live Endpoint / Method |
| :--- | :--- | :--- |
| **Have I Been Pwned** | Queries HIBP v3 API to detect account involvement in public data breaches. | `https://osintcabal.org/livecenter/cabalbreach-haveibeenpwned.html` |
| **Hudson Rock (Cavalier)** | Real-time database of compromised enterprise credentials harvested by info-stealers. | `https://osintcabal.org/livecenter/hudsonrock.html` |
| **Chiasmodon** | OSINT credential and asset scanner aggregating multi-breach exposures. | `https://osintcabal.org/livecenter/cabalbreach-chiasmodon.html` |
| **HuntPastebin** | Scrapes Pastebin, GitHub Gists, and text drops for sensitive query leaks. | `https://osintcabal.org/livecenter/huntpastebin.html` |
| **Hash ID** | Cryptographic hash identification engine (MD5, SHA-1, NTLM, bcrypt). | `https://osintcabal.org/livecenter/cabalbreach-hashid.html` |
| **Telegram Breach Monitor** | Monitors threat actor channels and dump repositories for live credential drops. | `https://osintcabal.org/livecenter/telegrambreach.html` |
| **Dorksint** | Automated Google dork generator for discovering unindexed files and config dumps. | `https://osintcabal.org/livecenter/dorksint.html` |

---

## 4. Social Media, Forum & Messaging Intelligence

| Tool | Target Network & Investigation Purpose | Live Endpoint / Method |
| :--- | :--- | :--- |
| **MastOSINT** | Federated Fediverse/Mastodon user, instance, and toot discovery. | `https://osintcabal.org/livecenter/mastosint.html` |
| **OSINTSky** | BlueSky platform reconnaissance using public firehose APIs. | `https://osintcabal.org/livecenter/OSINTSky.html` |
| **OSINTChan** | Searches 4Chan / imageboard archival threads and board postings. | `https://osintcabal.org/livecenter/OSINTChan.html` |
| **TeleGramSint** | Multi-API Telegram entity, channel, and message history extraction. | `https://osintcabal.org/livecenter/TeleGramSint.html` |
| **WhatsApp Profile API** | Queries phone number registration, status metadata, and profile pictures. | `https://osintcabal.org/livecenter/whatsappprofileapi.html` |
| **Reddit Push-Pull** | Restores and investigates deleted Reddit submissions and comments via Pushshift. | `https://osintcabal.org/livecenter/redditpushpull.html` |
| **TikTok Metadata Kit** | Bellingcat timestamp extractor and user profile metadata inspector. | `https://osintcabal.org/livecenter/tiktoktimestamp.html` |
| **SnapIntel & IG Sniffer** | Username validation and public metadata retrieval on Snapchat and Instagram. | `https://osintcabal.org/livecenter/snapintel.html` |

---

## 5. Investigation Workflow & Evidence Preservation
1. **Initial Pivot**: Start with known identifiers (email, username, domain, or phone).
2. **Multi-Platform Correlation**: Run through the respective module (Email Recon ➔ Social Footprint ➔ Breach Exposure).
3. **Evidence Hash Logging**: Calculate SHA-256 hashes of all harvested artifacts and record in `evidence/` with source URL and timestamp.
4. **Graph Integration**: Add discovered nodes and relations to the BigQuery graph and Dataverse `cr_entities` / `cr_relationships` tables.
