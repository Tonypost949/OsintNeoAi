# SPACES AUDIT — Neo's 17 Spaces (read-only audit, 2026-11-18)
Forwarded by Neo to the OsintNeoAi Muse, per the owner's Spaces handover order (SPACES_HANDOVER_2026-11-18.md). This audit was READ-ONLY: nothing was edited, shared, unshared, or deleted.

Method: artifact.list returned 17 Spaces in Neo's account; each was checked with artifact.status (live version, saved-at timestamp, public-share state). The one publicly shared Space was also given a delegated read-only content inspection.

## Headline — only ONE Space is publicly shared, and it is the highest risk
**OsintNeoAi Hub (`osintneoai-hub`) — the only publicly shared Space in the catalog.**
- Content is hard-coded in a single index.html; figures are dated **Nov 4, 2026**: 6,065 files, 91 projects, 36.96 GB, 2,653 entities, 785 links.
- Last build/audit: **Nov 6, 2026** — frozen since then.
- Runtime is static, client-only: no server actions, no database, no data source, no scheduled refresh (`managedCronJobs` empty).
- **No comment/feedback mechanism anywhere** — no form or feedback control in source or render. The only contact affordance is a `mailto:contact@osintneoai.me` link. This confirms the owner's complaint: there is no way to comment on it.
- No page-level "last updated" stamp, no dated entries.
- Whether any Nov 4 figure is factually wrong today was **NOT verified** — the inspection did not fetch live external sources. What is established: the content is frozen and un-updatable by design.
- Compounding factor: a public link serves the **last shared version** — later edits do not reach visitors until the Space is shared again.

## High risk — "live" claims on static snapshots
- **Bridge Live Viewer (`bridge-live-viewer`)** — Library, v2 Nov 12, 2026. A snapshot of the live Neo↔agy bridge channel; it ages the moment it is pulled and only updates when refreshed. (It is the only Space found with server actions.)
- **Smoking Gun Hunt — Live Board (`smoking-gun-hunt-live-board`)** — Sidebar, v7 Nov 17, 2026, but its own "WHAT'S GOING ON" panel is headed **"updated Sun Nov 15, 2026, evening"** and it is client-only/static — the "live" claims do not auto-update. The Nov 15 panel is stale on its face.
- **Swarm Visual Calendar (`swarm-visual-calendar`)** — Sidebar, v1 Nov 15, 2026, never updated. A one-shot snapshot of a continuously running swarm; activity counts/status age immediately. Client-only. (This is the calendar layout the owner likes — the style is right; the data freezes.)

## Never edited after creation — divergence risk
- **Smoking Guns #1–#5** (`smoking-gun-1-the-extortion`, `-2-the-protection-they-ran-over`, `-3-the-paper-eviction`, `-4-the-same-night-email`, `-5-the-conviction`) — Library, all v1 only, Nov 15, 2026 ~6:17 PM, never edited. The board above them was consolidated/revised through Nov 17, so board and gun pages can diverge.
- **DiSole (`disole`)** — Sidebar, v1 only, **Nov 9, 2026** — the oldest live version in the catalog. Atlas/business figures have moved since.

## Partial by its own labels
- **The Chronological Order (`the-chronological-order`)** — Sidebar, v11 Nov 16, 2026. The Mar 5–Aug 31, 2021 email layer is marked PARTIAL (9.2 GB mbox tail missing; completeness is an open pull). Later pulls supersede it; nothing added since Nov 16.

## Lower risk — fixed documents / fresher pages
- **RAS Form — Official Documents** (Nov 10, v1), **RAS Form Presentation** (Nov 10, v1), **RAS Form — The Document** (Nov 10, v1) — fixed official-document set; content does not age unless a new pull appears.
- **Trip Report — The Document** (Nov 10, v1) — utility/test document viewer, no time-sensitive claims found.
- **Extortion — Official Documents (`extortion-official-documents`)** — Sidebar, v10 Nov 17, 2026, actively maintained to Nov 17 — but **NOT shared**, so nothing on it is currently going out. Case work after Nov 17 is not in it.
- **Tecolote / Huntington Beach — Wells, Plants & Land (`tecolote-huntington-beach-wells-plants-land`)** — Sidebar, v6 Nov 17, 2026, the freshest of all 17. Carries an explicitly *estimated* land boundary, so it is the most sensitive to a later survey/document pull.

Placement totals: 8 sidebar, 9 library.

## For you (the receiving Muse) — priority order
1. **The Hub is priority #1.** Before anything public goes out under your ownership: re-verify every figure against the canonical atlas/repo sources, and stamp the verification date on the page. No new figures without a source check.
2. The owner may also choose to unshare Neo's Hub copy in the meantime — that is **his call, not yet ordered**. Do not unshare it yourself, and Neo has not.
3. Any Space you rebuild that presents live/ongoing activity needs a real refresh mechanism or an honest "snapshot as of [date/time]" stamp — the owner's core complaint is stale content passing as current, with no way for him to comment or correct it.
4. Volatile Spaces (Hub, Swarm Calendar, Live Board, Bridge Viewer) are the refresh-cycle candidates; fixed-document Spaces (RAS, Trip Report) do not need it.

— Neo, 2026-11-19 (audit performed 2026-11-18)
