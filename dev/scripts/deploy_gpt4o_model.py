import subprocess
import json

account = "opencode-ai-8609"
rg = "opencode-rg"
deployment_name = "gpt-4o"
model_name = "gpt-4o"
model_version = "2024-11-20"
sku_name = "GlobalStandard"
capacity = 10  # 10k TPM

print(f"=== DEPLOYING AZURE OPENAI MODEL: {model_name} ({model_version}) ===")
print(f"Target Account: {account} | Resource Group: {rg} | SKU: {sku_name}\n")

cmd = f'az cognitiveservices account deployment create --name {account} --resource-group {rg} --deployment-name {deployment_name} --model-name {model_name} --model-version {model_version} --model-format OpenAI --sku-name {sku_name} --sku-capacity {capacity} --output json'

res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if res.returncode == 0:
    dep = json.loads(res.stdout)
    print("✓ SUCCESS! Model deployment completed successfully:")
    print(f"  - Deployment Name: {dep.get('name')}")
    print(f"  - Provisioning State: {dep.get('properties', {}).get('provisioningState')}")
    print(f"  - Model: {model_name} ({model_version})")
else:
    print(f"Deployment output:")
    print(res.stdout)
    print(res.stderr)
