"""
azure_setup.py — Provision Azure AI services for OSINTNeoAi investigation.
Run: python azure_setup.py --provision
Requires: AZURE_SUBSCRIPTION_ID env var or az CLI login.
"""
import os, sys, json, time

RESOURCE_GROUP = "osint-neo-ai-rg"
LOCATION = "westus2"
SEARCH_SERVICE = "osint-search"
DOC_INTEL_SERVICE = "osint-doc-intel"
SPEECH_SERVICE = "osint-speech"

def run(cmd):
    print(f"  RUN: {cmd[:120]}")
    r = os.popen(cmd).read()
    if r.strip(): print(r[:500])
    return r

def provision():
    print("=== Provisioning Azure AI Services ===\n")
    
    sub_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not sub_id:
        print("ERROR: Set AZURE_SUBSCRIPTION_ID environment variable or run 'az login'.")
        print("  $env:AZURE_SUBSCRIPTION_ID='your-sub-id'")
        return
    
    # 1. Resource group
    print(f"[1/4] Resource Group: {RESOURCE_GROUP}")
    run(f'az group create --name {RESOURCE_GROUP} --location {LOCATION}')
    
    # 2. AI Search
    print(f"\n[2/4] AI Search: {SEARCH_SERVICE}")
    run(f'az search service create --name {SEARCH_SERVICE} --resource-group {RESOURCE_GROUP} --sku basic --location {LOCATION}')
    search_key = run(f'az search admin-key show --service-name {SEARCH_SERVICE} --resource-group {RESOURCE_GROUP} --query primaryKey -o tsv').strip()
    print(f"  Search key: {search_key[:8]}...")
    
    # 3. Document Intelligence
    print(f"\n[3/4] Document Intelligence: {DOC_INTEL_SERVICE}")
    run(f'az cognitiveservices account create --name {DOC_INTEL_SERVICE} --resource-group {RESOURCE_GROUP} --kind FormRecognizer --sku F0 --location {LOCATION} --yes')
    doc_key = run(f'az cognitiveservices account keys list --name {DOC_INTEL_SERVICE} --resource-group {RESOURCE_GROUP} --query key1 -o tsv').strip()
    doc_endpoint = run(f'az cognitiveservices account show --name {DOC_INTEL_SERVICE} --resource-group {RESOURCE_GROUP} --query properties.endpoint -o tsv').strip()
    print(f"  DocIntel endpoint: {doc_endpoint}")
    
    # 4. Speech
    print(f"\n[4/4] Speech: {SPEECH_SERVICE}")
    run(f'az cognitiveservices account create --name {SPEECH_SERVICE} --resource-group {RESOURCE_GROUP} --kind SpeechServices --sku F0 --location {LOCATION} --yes')
    speech_key = run(f'az cognitiveservices account keys list --name {SPEECH_SERVICE} --resource-group {RESOURCE_GROUP} --query key1 -o tsv').strip()
    speech_region = LOCATION
    
    # Write config
    config = {
        "search_endpoint": f"https://{SEARCH_SERVICE}.search.windows.net",
        "search_key": search_key,
        "search_index_gmail": "gmail-index",
        "search_index_drive": "drive-index",
        "doc_intel_endpoint": doc_endpoint.strip(),
        "doc_intel_key": doc_key,
        "speech_key": speech_key,
        "speech_region": speech_region,
        "resource_group": RESOURCE_GROUP,
        "subscription_id": sub_id,
    }
    
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure_config.json")
    config_path2 = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\azure_config.json"
    
    for p in [config_path, config_path2]:
        with open(p, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  Config saved: {p}")
    
    print("\n=== DONE ===")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--provision":
        provision()
    else:
        print("Run with --provision to create Azure resources.")
        print("Requires: AZURE_SUBSCRIPTION_ID or az login")
