import json
import subprocess

sub_id = "f055033f-83fb-4ae9-9c36-be48f0c86158"
rg = "opencode-rg"
account = "opencode-ai-8609"

print("=== CHECKING AVAILABLE MODELS & VERSIONS FOR OPENCODE-AI-8609 ===")

cmd = f'az cognitiveservices account list-models --name {account} --resource-group {rg} --output json'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if res.returncode == 0:
    models = json.loads(res.stdout)
    gpt4o_models = [m for m in models if m.get('name') == 'gpt-4o' or m.get('model', {}).get('name') == 'gpt-4o']
    print(f"Total Models Supported by Account: {len(models)}")
    print(f"gpt-4o Models Found: {len(gpt4o_models)}")
    for m in models:
        m_name = m.get('name') or m.get('model', {}).get('name')
        m_ver = m.get('version') or m.get('model', {}).get('version')
        if 'gpt-4' in str(m_name).lower() or 'gpt-4o' in str(m_name).lower():
            print(f"  - Model Name: {m_name} | Version: {m_ver} | Format: {m.get('format', 'OpenAI')}")
else:
    print(f"Error fetching models: {res.stderr}")
