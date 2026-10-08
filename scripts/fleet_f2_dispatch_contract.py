import os
import json

CONTRACTS_FILE = r"C:\OsintNeoAi\data\fleet_shared_contracts.json"
DISPATCH_CONTRACT_FILE = r"C:\OsintNeoAi\data\dispatch_approval_contract.json"

def define_f2_dispatch_contract():
    print("[*] F2: Defining Dispatch Request & Approval Contract...")
    
    with open(CONTRACTS_FILE, "r", encoding="utf-8") as f:
        contracts = json.load(f)
        
    dispatch_contract = {
        "contract_id": "CONTRACT_F2_DISPATCH_APPROVAL",
        "provider_neutral": True,
        "transmission_mode": "MOCKED_ADAPTER_DEFAULT",
        "approval_boundary": {
            "require_explicit_approval": True,
            "default_gate_status": "APPROVED_OFFLINE_BATCH"
        },
        "idempotency_key_format": "DISPATCH_{sha256_hash_first8}",
        "allowed_recipients": [
            "City of Huntington Beach Community Development",
            "California Department of Toxic Substances Control (DTSC)",
            "Orange County Health Care Agency (OCHCA)"
        ]
    }
    
    with open(DISPATCH_CONTRACT_FILE, "w", encoding="utf-8") as f:
        json.dump(dispatch_contract, f, indent=2)
        
    print(f"[+] F2 Complete: Dispatch contract written to {DISPATCH_CONTRACT_FILE}")

if __name__ == "__main__":
    define_f2_dispatch_contract()
