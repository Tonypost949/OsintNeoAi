# Research Escalation Protocol Tool
## Rule: Search Before Spawning
1. ALWAYS run web searches first before launching any teamwork agent or subagent swarm.
2. If the answer is found in search results, the task is complete. Done.
3. Only escalate to teamwork agents if search results are insufficient, behind a paywall, or require deep multi-source synthesis.
4. This applies to every investigation, every time, no exceptions.

## 2026-10-04 21:00 - OSINT source links (user-provided, recorded per Law 3)
1. City of Huntington Beach official records (eDocs/WebLink): https://records.huntingtonbeachca.gov/WebLink/DocView.aspx?dbid=0&id=7335745&repo=COHB
   - NOTE: direct fetch from agent transport = failed (JS/session-gated eDocView). Use browser session or OCR export path.
2. NetFile campaign finance (Orange County / COHB jurisdiction): https://netfile.com/public/coc/campaign
   - NOTE: transport error from agent - likely bot-gated; verify in browser session.
3. GeoTracker profile/ESI + HWTS manifests: Cloudflare-walled for bots - requires real browser session (Chrome DevTools MCP or authenticated export).
Status: RECORDED - pending live-session retrieval.
