# RECAP #002: Developer Terminals, Gemini 3.7 Flash & Remote Phone Architecture
Date: 2026-09-12T00:15:00-07:00
Conversation ID: 3610a799-567d-4231-a823-dbf333681a98
User: amd949609@gmail.com

---

## 1. Developer Terminals Standardized (vsdev FIRST ➔ aicli THEN)
- **Startup Sequence:** All environments initialize VS 2022 Developer Shell (`-arch=amd64`) first, then inject PATH, resolve workspace directory, and load the 10-Agent `aicli` launcher.
- **Windows Terminal Profiles Configured (`settings.json`):**
  1. `Developer Terminal (OsintNeoAi)` ➔ `C:\OsintNeoAi` (Default)
  2. `Developer Terminal (TaxFunded)` ➔ `C:\TaxFunded`
  3. `Developer Terminal (C:)` ➔ `C:\`
  4. `Developer Terminal (Kali Linux)` ➔ `//wsl.localhost/kali-linux/home/osintneoai`
- **Window Fixes Applied:** `launchMode` restored to `"default"`, `alwaysOnTop: false` — standard Windows 11 title bar controls, resizing borders, and double-click maximize/restore fully operational.

---

## 2. OpenCode Diagnosed & Upgraded to Gemini 3.7 Flash
- **Issue Resolved:** `Cannot connect to API: Unable to connect...` error in OpenCode (captured in `OpenCode.txt`) caused by invalid model identifier `gemini-3.6-flash`.
- **Active Configurations:** Updated both Windows (`C:\Users\Amd949609\.config\opencode\opencode.jsonc`) and Kali Linux (`\\wsl.localhost\kali-linux\home\osintneoai\.config\opencode\opencode.jsonc`) to `google/gemini-3.7-flash` (with low thinking budget support).
- **Environment Keys:** `GEMINI_API_KEY`, `GOOGLE_API_KEY` validated and active.

---

## 3. Phone-to-Linux Remote PowerShell Connection Architectures
- **Goal:** Connect Samsung Galaxy A16 5G to high-compute Linux machine to run PowerShell 7 (`pwsh`), OpenCode, and AI tools.
- **Method 1 (Web Terminal):** `ttyd -W -p 7681 pwsh` — instant touch browser terminal at `http://<LINUX_IP>:7681`.
- **Method 2 (Tailscale Mesh VPN):** Secure remote SSH via Termux/JuiceSSH over mobile 5G data.
- **Method 3 (Google Cloud):** GCE Linux instance / Cloud Shell (`noble-beanbag-497411-m4`).

---

## 4. Starter Prompt for Chat #3
"Let's set up the phone connection to the Linux machine to run PowerShell (pwsh) and test our Developer Terminal environments."
