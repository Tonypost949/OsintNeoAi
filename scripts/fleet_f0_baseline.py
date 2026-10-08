import os
import json
import unittest

SHARED_CONTRACTS_FILE = r"C:\OsintNeoAi\data\fleet_shared_contracts.json"

def establish_shared_contracts():
    print("[*] F0: Establishing Baseline & Shared Contracts...")
    
    contracts = {
        "version": "1.0",
        "boundaries": {
            "no_live_fax_by_default": True,
            "mocked_transport_default": True,
            "approved_clues_only": True,
            "deterministic_hashing": True
        },
        "dispatch_schema": {
            "required_fields": ["dispatch_id", "timestamp", "recipient", "document_payload_path", "approval_gate"],
            "allowed_gates": ["SYSTEM_APPROVED_ZERO_TRUST", "USER_MANUAL_OVERRIDE"],
            "default_gate": "SYSTEM_APPROVED_ZERO_TRUST"
        },
        "crossword_schema": {
            "required_fields": ["puzzle_id", "date", "clues", "verification_hash"],
            "min_clues": 5
        }
    }
    
    with open(SHARED_CONTRACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contracts, f, indent=2)
        
    print(f"[+] F0 Complete: Shared contracts established at {SHARED_CONTRACTS_FILE}")

if __name__ == "__main__":
    establish_shared_contracts()
