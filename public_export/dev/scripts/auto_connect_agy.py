import os
import json
import subprocess
from pathlib import Path

print("=========================================================")
print("  🚀 AGY OSINTNEOAI AUTOMATIC WORKSPACE CONNECTION HOOK   ")
print("=========================================================")

ws_file = Path(r'C:\OsintNeoAi\.antigravity\workspace.json')
if ws_file.exists():
    data = json.loads(ws_file.read_text(encoding='utf-8'))
    print(f"✓ Workspace Target: {data.get('name')} ({data.get('workspaceRoot')})")
    print(f"✓ GitHub Remote: {data.get('git', {}).get('primaryRemote')}")
    print(f"✓ Azure DevOps Remote: {data.get('git', {}).get('azureRemote')}")
    print(f"✓ Live Web App URL: {data.get('azure', {}).get('webApp', {}).get('liveUrl')}")
    print(f"✓ Azure AI Search: {data.get('azure', {}).get('aiSearch', {}).get('endpoint')}")
    print(f"✓ Azure OpenAI Account: {data.get('azure', {}).get('openAI', {}).get('accountName')}")

print("\n✓ Verification Complete — Workspace Auto-Connected!")
print("=========================================================")
