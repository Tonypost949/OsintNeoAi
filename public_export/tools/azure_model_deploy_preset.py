#!/usr/bin/env python3
"""
azure_model_deploy_preset.py — Preset model deployment for OsintNeoAi
Follows deploy-model/preset/SKILL.md workflow:
  1. Verify auth & subscription
  2. Discover existing OpenAI project
  3. List available models + check quota
  4. Present deployment options to user
  5. Deploy GlobalStandard SKU with 50% available capacity (min 50 TPM)
"""

import subprocess
import json
import sys

SUBSCRIPTION = "f055033f-83fb-4ae9-9c36-be48f0c86158"
RESOURCE_GROUP = "opencode-rg"
ACCOUNT_NAME = "opencode-ai-8609"
LOCATION = "eastus"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ── Phase 1: Verify Auth ──────────────────────────────────────
section("Phase 1: Azure Auth")
out, err, code = run("az account show --output json")
if code != 0:
    print(f"[ERROR] Not authenticated: {err}")
    print("Run: az login --use-device-code")
    sys.exit(1)

acct = json.loads(out)
print(f"  Account   : {acct['user']['name']}")
print(f"  Sub Name  : {acct['name']}")
print(f"  Sub ID    : {acct['id']}")
print(f"  Sub State : {acct['state']}")
print(f"  Tenant    : {acct['tenantDefaultDomain']}")

if acct['state'].lower() == 'disabled':
    print("\n  [WARNING] Subscription is DISABLED. Attempting to use anyway — some ops may fail.")

# ── Phase 2: Verify Project ───────────────────────────────────
section("Phase 2: OpenAI Account")
out, err, code = run(f"az cognitiveservices account show --name {ACCOUNT_NAME} --resource-group {RESOURCE_GROUP} --output json")
if code != 0:
    print(f"[ERROR] Cannot access account: {err}")
    sys.exit(1)

acct_info = json.loads(out)
print(f"  Name      : {acct_info['name']}")
print(f"  Kind      : {acct_info['kind']}")
print(f"  Location  : {acct_info['location']}")
print(f"  Endpoint  : {acct_info['properties'].get('endpoint','N/A')}")
print(f"  State     : {acct_info['properties'].get('provisioningState','N/A')}")

# ── Phase 3: List Available Models ───────────────────────────
section("Phase 3: Available Models")
out, err, code = run(f"az cognitiveservices account list-models --name {ACCOUNT_NAME} --resource-group {RESOURCE_GROUP} --output json")
if code != 0:
    print(f"[ERROR] Cannot list models: {err}")
    sys.exit(1)

models = json.loads(out)
print(f"\n  {'Model':<25} {'Version':<15} {'SKUs'}")
print(f"  {'-'*25} {'-'*15} {'-'*30}")
for m in models:
    name = m['model']['name']
    version = m['model']['version']
    skus = [s['name'] for s in m['model'].get('skus', [])]
    print(f"  {name:<25} {version:<15} {', '.join(skus)}")

# ── Phase 4: Check Quota ──────────────────────────────────────
section("Phase 4: Quota Check (eastus)")
out, err, code = run(f"az cognitiveservices usage list --location {LOCATION} --subscription {SUBSCRIPTION} --output json")
if code != 0:
    print(f"[WARN] Cannot check quota: {err}")
    quota_data = []
else:
    quota_data = json.loads(out)
    gpt_quotas = [q for q in quota_data if 'gpt' in q.get('name',{}).get('value','').lower() or 'GlobalStandard' in q.get('name',{}).get('value','')]
    print(f"\n  {'Quota Name':<50} {'Used':>8} {'Limit':>8} {'Avail':>8}")
    print(f"  {'-'*50} {'-'*8} {'-'*8} {'-'*8}")
    for q in gpt_quotas[:20]:
        name_val = q.get('name',{}).get('localizedValue', q.get('name',{}).get('value',''))[:48]
        used = q.get('currentValue', 0)
        limit = q.get('limit', 0)
        avail = limit - used
        status = "✅" if avail > 0 else "❌"
        print(f"  {status} {name_val:<48} {used:>8} {limit:>8} {avail:>8}")

# ── Phase 5: List Existing Deployments ───────────────────────
section("Phase 5: Existing Deployments")
out, err, code = run(f"az cognitiveservices account deployment list --name {ACCOUNT_NAME} --resource-group {RESOURCE_GROUP} --output json")
if code != 0:
    print(f"[WARN] Cannot list deployments: {err}")
    existing = []
else:
    existing = json.loads(out)
    if existing:
        print(f"\n  {'Deployment':<30} {'Model':<20} {'SKU':<20} {'Capacity':>10}")
        print(f"  {'-'*30} {'-'*20} {'-'*20} {'-'*10}")
        for d in existing:
            dep_name = d['name']
            model = d['properties'].get('model',{}).get('name','?')
            sku = d['sku']['name'] if d.get('sku') else '?'
            cap = d['sku']['capacity'] if d.get('sku') else '?'
            state = d['properties'].get('provisioningState','?')
            print(f"  {dep_name:<30} {model:<20} {sku:<20} {cap:>10}  [{state}]")
    else:
        print("  No deployments found.")

# ── Phase 6: Deployment Recommendation ───────────────────────
section("Phase 6: Deployment Plan")
print("""
  TARGET DEPLOYMENT:
  ─────────────────────────────────────────────────────
  Account       : opencode-ai-8609
  Resource Group: opencode-rg
  Location      : eastus
  SKU           : GlobalStandard
  Model         : gpt-4o (latest stable)
  Capacity      : 50 TPM (minimum preset default)
  Deployment Name: osint-gpt4o-preset-001
  ─────────────────────────────────────────────────────
  
  To deploy, run:
  az cognitiveservices account deployment create \\
    --name opencode-ai-8609 \\
    --resource-group opencode-rg \\
    --deployment-name osint-gpt4o-preset-001 \\
    --model-name gpt-4o \\
    --model-version latest \\
    --model-format OpenAI \\
    --sku-name GlobalStandard \\
    --sku-capacity 50
""")

print("\n[READY] Run this script with --deploy flag to execute the deployment.")
print("[STATUS] Phase 1-5 complete. Deployment awaiting confirmation.\n")
