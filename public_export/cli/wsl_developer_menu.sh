#!/bin/bash
clear
echo -e "\033[1;36m=========================================\033[0m"
echo -e "\033[1;33m     OSINTNEOAI DEVELOPER CLI LAUNCHER   \033[0m"
echo -e "\033[1;36m=========================================\033[0m"
echo -e "\033[1;33m  PRIMARY AI & AGENT CLIs:\033[0m"
echo -e "   [1]  Antigravity (agy)"
echo -e "   [2]  OpenCode Pentest (Kali + OsintNeoAi + GitHub Auto-Installer & Clarifier)"
echo -e "   [3]  Gemini CLI (gemini)"
echo -e "   [4]  OSINTNEOAI Master Intelligence (osintneoai)"
echo -e "   [5]  Standard OpenCode (opencode)"
echo -e "   [6]  GitHub Copilot (gh copilot)"
echo -e "   [7]  Ollama (ollama)"

echo -e "\n\033[1;33m  DEVELOPMENT & RUNTIMES:\033[0m"
echo -e "   [8]  Python 3 (python3)"
echo -e "   [9]  Git (git)"
echo -e "   [10] VS Code (code .)"
echo -e "   [Q]  Quit / Cancel"
echo -e "\033[1;36m=========================================\033[0m"

read -p "Select a CLI tool to launch [1-10, Q]: " choice
case "$choice" in
    1) agy "$@" ;;
    2)
        echo -e "\nPaste your target prompt, code snippet, or tool request below:"
        read -p "> " tool_prompt
        opencode-pentest "$tool_prompt"
        ;;
    3) gemini "$@" ;;
    4) osintneoai "$@" ;;
    5) opencode "$@" ;;
    6) gh copilot suggest ;;
    7) ollama run qwen2.5-coder:7b ;;
    8) python3 ;;
    9) git ;;
    10) code . ;;
    q|Q) exit 0 ;;
    *) echo "Invalid selection." ;;
esac
