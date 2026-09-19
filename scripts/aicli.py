# Unified AI Coding Agent Launcher — OSINTNEOAI
# Location: C:\OsintNeoAi\scripts\aicli.py
import sys
import os
import subprocess
import json

def launch_unified_ai_agent(agent_name="antigravity"):
    print("==================================================================")
    print("    OSINTNEOAI UNIFIED AI CODING AGENT LAUNCHER v1.0")
    print("==================================================================")
    print(f"[*] Target AI Agent requested: {agent_name}")

    agents = {
        "antigravity": {
            "name": "Google Antigravity CLI",
            "cmd": ["python", "-m", "antigravity"],
            "desc": "Primary Google DeepMind AI Coding Assistant"
        },
        "opencode": {
            "name": "OpenCode AI Agent",
            "cmd": ["opencode", "start"],
            "desc": "OpenCode Trajectory & Multi-Agent Builder"
        },
        "gcloud": {
            "name": "Google Cloud Gemini Agent",
            "cmd": ["gcloud", "alpha", "code"],
            "desc": "Gemini Code Assist & GCP Infrastructure Agent"
        },
        "genkit": {
            "name": "Firebase Genkit AI Agent",
            "cmd": ["npx", "genkit", "start"],
            "desc": "Firebase AI Logic & Serverless Agent"
        },
        "copilot": {
            "name": "GitHub Copilot CLI Agent",
            "cmd": ["gh", "copilot"],
            "desc": "GitHub Copilot Terminal & Codebase Agent"
        }
    }

    if agent_name not in agents:
        print(f"[!] Unknown agent: '{agent_name}'. Available options:")
        for k, v in agents.items():
            print(f"  - {k}: {v['name']} ({v['desc']})")
        return

    target = agents[agent_name]
    print(f"[+] Launching {target['name']}...")
    print(f"    Description: {target['desc']}")
    print("==================================================================")

if __name__ == "__main__":
    requested = sys.argv[1] if len(sys.argv) > 1 else "antigravity"
    launch_unified_ai_agent(requested)
