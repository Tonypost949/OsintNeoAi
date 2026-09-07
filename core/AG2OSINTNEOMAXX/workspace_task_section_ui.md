# OsintNeoAi Workspace: Task Section UI

This is the designated Task Management interface embedded directly into the end user's workspace. It strictly follows the routing rules defined in `task_system_registry.json`.

---

## 🟢 1. Active User Action Required
Tasks that require the human investigator to take a specific, legally binding, or personal action.
- **`[FOIA_REQUESTS]`** - Pending Freedom of Information Act requests waiting for signature or review.
- **`[CONTACT_FOR_COMPLAINT]`** - Auto-drafted complaints (e.g., DA, State Bar, DTSC) waiting for the user to hit "Send".
- **`[CONTACT_FOR_ASSISTANCE]`** - Outreach to whistleblowers, journalists, or legal aid.

## 🤖 2. Suggestive Work (AI Autonomous)
*Description: "AI should be doing this work. It might just have to be off-hours, or after the user is finished something else."*
- **`[SUGGESTIVE_WORK]`** - Background scraping, heavy OCR, or timeline cross-referencing. The AI handles this while the user sleeps or focuses on other tasks. 

## 🛡️ 3. Site Admin & Support
*Description: "This covers anything to contact us about and the ONLY task for us that we answer too."*
- **`[CONTACT_SITE_ADMIN]`** - Direct line to the Dev/Admin team for Help, FAQs, bug reports, or system access issues. This is the only queue the core team monitors and replies to.

## 🔴 4. Failed Completely
*Description: "Tasks that hit a total dead end. Placed on this list and instantly sent to the dev team via telemetry. We don't have to answer it, but we want to know what fails."*
- **`[FAILED_COMPLETELY]`** - Impossible captchas, 404 dead links, or hostile infrastructure that blocked even the AnythingLLM proxy. 
  - *Action:* Logged for the user's visibility -> Telemetry instantly pinged to Admins -> **No Admin Reply Required**.

## 🏁 5. Completed
- **`[COMPLETED]`** - Historical archive of all successfully ripped evidence, filed FOIAs, and finished suggestive work.
