"""Universal Terminal AI Agent Launcher & Swarm Dispatcher for OsintNeoAi.

Provides live tool discovery, tiered local open-weight inference (Ollama Edge/Mid),
OpenOSINT MCP bindings, and modern Windows Terminal integration with Rich terminal UI.
"""

import os
import sys
import subprocess
import shutil

# Check if rich is installed for advanced terminal formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

AGENT_CATALOG = {
    "0": {
        "name": "Windows Terminal (wt-dev)",
        "description": "Zero-lag modern ConPTY terminal with bracketed paste mode",
        "command": "wt-dev",
        "check_cmd": "wt.exe",
        "tier": "Terminal Core"
    },
    "1": {
        "name": "Antigravity (agy)",
        "description": "Google Antigravity autonomous multi-agent coding framework",
        "command": "agy",
        "check_cmd": "agy",
        "tier": "Cloud / Autonomous"
    },
    "2": {
        "name": "OpenCode Pentest",
        "description": "Kali APT + OsintNeoAi + GitHub repository tool auto-runner",
        "command": "wsl -d kali-linux --cd /mnt/c/OsintNeoAi -- opencode-pentest",
        "check_cmd": "wsl",
        "tier": "WSL Security"
    },
    "3": {
        "name": "Gemini CLI",
        "description": "Google Gemini terminal AI assistant",
        "command": "gemini",
        "check_cmd": "gemini",
        "tier": "Cloud AI"
    },
    "4": {
        "name": "OSINTNEOAI Master CLI",
        "description": "OsintNeoAi forensic entity analysis & transform CLI",
        "command": "python C:\\OsintNeoAi\\cli\\cli.py",
        "check_cmd": "python",
        "tier": "Forensic Intelligence"
    },
    "5": {
        "name": "OpenOSINT MCP Server",
        "description": "19 automated reconnaissance & entity resolution tools",
        "command": "python C:\\OsintNeoAi\\tools\\openosint_mcp_server.py",
        "check_cmd": "python",
        "tier": "MCP Tools"
    },
    "6": {
        "name": "Ollama Edge (Qwen 1.5B)",
        "description": "Ultra-fast local open-weight model for terminal scripting",
        "command": "ollama run qwen2.5-coder:1.5b",
        "check_cmd": "ollama",
        "tier": "Local Edge (Low VRAM)"
    },
    "7": {
        "name": "Ollama Mid (Qwen 7B)",
        "description": "Balanced local coding & entity extraction model",
        "command": "ollama run qwen2.5-coder:7b",
        "check_cmd": "ollama",
        "tier": "Local Mid-Tier"
    },
    "8": {
        "name": "Standard OpenCode",
        "description": "Anomaly open-source multi-file autonomous coding agent",
        "command": "opencode",
        "check_cmd": "opencode",
        "tier": "Agent CLI"
    },
    "9": {
        "name": "GitHub Copilot CLI",
        "description": "GitHub terminal assistant & shell command suggest",
        "command": "gh copilot suggest",
        "check_cmd": "gh",
        "tier": "Developer Tools"
    },
    "10": {
        "name": "VS Code Workspace",
        "description": "Open OsintNeoAi repository in Visual Studio Code",
        "command": "code C:\\OsintNeoAi",
        "check_cmd": "code",
        "tier": "IDE"
    }
}

def check_status(check_cmd: str) -> str:
    """Check if the command executable exists in PATH."""
    if shutil.which(check_cmd):
        return "Ready"
    # Special check for local python or scripts
    if check_cmd == "python" and shutil.which("python"):
        return "Ready"
    if check_cmd == "wt.exe":
        wt_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe")
        if os.path.exists(wt_path):
            return "Ready"
    return "Not Installed"

def display_menu():
    if RICH_AVAILABLE:
        table = Table(title="⚡ OSINTNEOAI UNIVERSAL TERMINAL AGENT LAUNCHER & SWARM DISPATCHER", style="cyan")
        table.add_column("#", style="bold yellow", width=4)
        table.add_column("Agent / Tool", style="bold white", width=24)
        table.add_column("Tier", style="magenta", width=18)
        table.add_column("Description", style="dim white", width=36)
        table.add_column("Status", style="green", width=12)

        for key, info in AGENT_CATALOG.items():
            status = check_status(info["check_cmd"])
            status_style = "bold green" if status == "Ready" else "bold red"
            table.add_row(key, info["name"], info["tier"], info["description"], Text(status, style=status_style))

        console.print(table)
        console.print("[yellow]Enter option [0-10] or 'q' to exit:[/yellow] ", end="")
    else:
        print("=" * 80)
        print("⚡ OSINTNEOAI UNIVERSAL TERMINAL AGENT LAUNCHER & SWARM DISPATCHER")
        print("=" * 80)
        print(f"{'#':<3} {'AGENT / TOOL':<24} {'TIER':<18} {'STATUS':<12} {'DESCRIPTION'}")
        print("-" * 80)
        for key, info in AGENT_CATALOG.items():
            status = check_status(info["check_cmd"])
            print(f"{key:<3} {info['name']:<24} {info['tier']:<18} {status:<12} {info['description']}")
        print("-" * 80)
        print("q. Quit / Exit")
        print("=" * 80)
        print("Enter option [0-10, q]: ", end="")

def launch_agent(choice: str):
    choice = choice.strip()
    if choice.lower() in ["q", "quit", "exit"]:
        print("[+] Exiting.")
        return
    if choice not in AGENT_CATALOG:
        print(f"[-] Invalid selection: {choice}")
        return
    agent = AGENT_CATALOG[choice]
    print(f"\n[🚀] Launching {agent['name']} ({agent['tier']})...")
    print(f"[CMD] {agent['command']}\n")
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
        user_choice = input().strip()
        if user_choice:
            launch_agent(user_choice)
