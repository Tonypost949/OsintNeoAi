"""Universal Terminal AI Agent Launcher & Swarm Dispatcher for OsintNeoAi."""

import os
import sys
import subprocess
import shutil

AGENT_CATALOG = {
    "1": {
        "name": "Qwen Code",
        "description": "Qwen's AI coding agent with advanced tool use & reasoning",
        "command": "ollama run qwen2.5-coder:7b",
        "alt_command": "ollama launch qwen",
        "status": "Installed (qwen2.5-coder:7b)"
    },
    "2": {
        "name": "Claude Code",
        "description": "Anthropic's coding tool with autonomous subagents",
        "command": "claude",
        "alt_command": "ollama launch claude",
        "status": "Available"
    },
    "3": {
        "name": "OpenCode",
        "description": "Anomaly's open-source multi-file autonomous coding agent",
        "command": "opencode",
        "alt_command": "ollama launch opencode",
        "status": "Available"
    },
    "4": {
        "name": "Hermes Agent",
        "description": "Self-improving AI agent built by Nous Research",
        "command": "ollama run hermes3",
        "alt_command": "ollama launch hermes",
        "status": "Available"
    },
    "5": {
        "name": "Cline",
        "description": "Autonomous coding agent with parallel execution & MCP support",
        "command": "cline",
        "alt_command": "ollama launch cline",
        "status": "Available"
    },
    "6": {
        "name": "DeepSeek Harness",
        "description": "DeepSeek's high-performance open-source agent harness",
        "command": "ollama run deepseek-coder-v2",
        "alt_command": "ollama launch dsh",
        "status": "Available"
    },
    "7": {
        "name": "OpenClaw",
        "description": "Personal autonomous AI with 100+ investigative skills",
        "command": "openclaw",
        "alt_command": "ollama launch openclaw",
        "status": "Available"
    },
    "8": {
        "name": "Codex",
        "description": "OpenAI's open-source coding agent harness",
        "command": "codex",
        "alt_command": "ollama launch codex",
        "status": "Available"
    },
    "9": {
        "name": "Droid",
        "description": "Factory's coding agent across terminal and IDEs",
        "command": "droid",
        "alt_command": "ollama launch droid",
        "status": "Available"
    },
    "10": {
        "name": "Copilot CLI",
        "description": "GitHub's AI coding agent for the terminal",
        "command": "gh copilot",
        "alt_command": "ollama launch copilot",
        "status": "Available"
    },
    "11": {
        "name": "Pi / Oh My Pi",
        "description": "Minimal AI agent toolkit with plugin & IDE support",
        "command": "omp",
        "alt_command": "ollama launch omp",
        "status": "Available"
    },
    "12": {
        "name": "Ollama Interactive Terminal",
        "description": "Run local LLMs directly from your terminal",
        "command": "ollama run qwen2.5-coder:7b",
        "alt_command": "ollama",
        "status": "Ready"
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
