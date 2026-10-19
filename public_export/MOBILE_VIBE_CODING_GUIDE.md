# 💜 Android & Mobile Vibe-Coding Guide (Termux, iOS & Codespaces)

This guide explains how to run full-stack AI vibe coding, execute terminal workflows, and manage this repository natively on mobile devices.

---

## 🤗 1. Android Native Vibe-Coding with Termux
"You can run a full AI pair-programming assistant natively on your Android device using **Termux** + **Aider** (or Gemini CLI).

### Quickstart Setup in Termux:
```bash
# 1. Update Termux packages & install Python, Git, and build tools
pkg update -y && pkg install -y python git build-essential nodejs

# 2. Install Aider (The #1 Terminal Vibe-Coding Tool)
pip install aider-chat

# 3. Clone this repository
git clone https://github.com/Tonypost949/OsintNeoAi.git
cd OsintNeoAi
pip install -r requirements.txt

# 4. Export your Gemini API Key
export GEMINI_API_KEY="your_gemini_api_key_here"

# 5. Launch Vibe Coding Session
aider --model gemini/gemini-1.5-pro
```

### Alternative: Google Gemini CLI in Termux
```bash
npm install -g @google/gemini-cli
gemini
```

---

## 🍏 2. iOS (iPhone / iPad) & Cloud Browser Vibe Coding

Since iOS restricts native package managers, the recommended way to get full vibe-coding on an iPhone or iPad is via **GitHub Codespaces**:

1. Open [**github.com/Tonypost949/OsintNeoAi**](https://github.com/Tonypost949/OsintNeoAi) in Safari or Chrome.
2. Tap **`Code`** → select **`Codespaces`** → tap **`Create codespace on main`**.
3. A full VS Code / Terminal environment opens right inside your mobile browser.
4. Launch the AI coding assistant or run `python OSINTNeoAiCLI.py` with zero installation required.

---

## 🌋 3. Mobile Live Endpoints (Zero Installation)

If you only need to access the live dashboards, tactical GIS maps, or victim registries on your phone, open:
* 🚀 **Live Portal:** https://osintneoai-app-949.azurewebsites.net/
* 👬 **Live Chat Transcript:** https://osintneoai-app-949.azurewebsites.net/chat
* 🗺 **Tactical GIS Maps:** https://osintneoai-app-949.azurewebsites.net/maps
* 📊 **Victims Board:** https://osintneoai-app-949.azurewebsites.net/victims-board
