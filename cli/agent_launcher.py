"""Universal Terminal AI Agent Launcher & Swarm Dispatcher for OsintNeoAi."""

import os
import sys
import subprocess
import shutil

AGENT_CATALOG = {
    "1": {
        "name": "Antigravity (agy)",
        "description": "Google Antigravity autonomous multi-agent coding framework",
        "command": "agy",
        "alt_command": "agy --help",
        "status": "Installed & Ready"
    },
    "2": {
        "name": "OpenCode Pentest",
        "description": "Kali APT + OsintNeoAi + GitHub repository tool auto-installer & runner",
        "command": "wsl opencode-pentest",
        "alt_command": "opencode-pentest",
        "status": "Installed & Ready"
    },
    "3": {
        "name": "Gemini CLI",
        "description": "Google Gemini terminal AI assistant",
        "command": "gemini",
        "alt_command": "npx @google/gemini-cli",
        "status": "Installed & Ready"
    },
    "4": {
        "name": "OSINTNEOAI Master Intelligence",
        "description": "OsintNeoAi forensic entity analysis & transform CLI",
        "command": "python cli/cli.py",
        "alt_command": "osintneoai",
        "status": "Installed & Ready"
    },
    "5": {
        "name": "Standard OpenCode",
        "description": "Anomaly's open-source multi-file autonomous coding agent",
        "command": "opencode",
        "alt_command": "wsl opencode",
        "status": "Installed & Ready"
    },
    "6": {
        "name": "Qwen Code",
        "description": "Qwen's AI coding agent with advanced tool use & reasoning",
        "command": "ollama run qwen2.5-coder:7b",
        "alt_command": "ollama launch qwen",
        "status": "Installed (qwen2.5-coder:7b)"
    },
    "7": {
        "name": "Claude Code",
        "description": "Anthropic's coding tool with autonomous subagents",
        "command": "claude",
        "alt_command": "ollama launch claude",
        "status": "Available"
    },
    "8": {
        "name": "Cline",
        "description": "Autonomous coding agent with parallel execution & MCP support",
        "command": "cline",
        "alt_command": "ollama launch cline",
        "status": "Available"
    },
    "9": {
        "name": "Copilot CLI",
        "description": "GitHub's AI coding agent for the terminal",
        "command": "gh copilot",
        "alt_command": "gh copilot suggest",
        "status": "Available"
    }
}

def display_menu():
    print("=" * 75)
    print("⚡ OSINTNEOAI UNIVERSAL TERMINAL AGENT LAUNCHER & SWARM DISPATCHER")
    print("=" * 75)
    print(f"{'#':<3} {'AGENT NAME':<22} {'DESCRIPTION':<36} {'STATUS'}")
    print("-" * 75)
    for key, info in AGENT_CATALOG.items():
        print(f"{key:<3} {info['name']:<22} {info['description'][:35]:<36} {info['status']}")
    print("-" * 75)
    print("q. Quit / Exit")
    print("=" * 75)

def launch_agent(choice: str):
    if choice not in AGENT_CATALOG:
        print(f"[-] Invalid selection: {choice}")
        return
    agent = AGENT_CATALOG[choice]
    print(f"\n[🚀] Launching {agent['name']}...")
    print(f"[CMD] {agent['command']}")
    try:
        subprocess.run(agent['command'], shell=True)
    except Exception as e:
        print(f"[-] Error launching {agent['name']}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        launch_agent(arg)
    else:
        display_menu()
