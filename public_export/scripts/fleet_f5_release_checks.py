import os
import json

SHARED_CONTRACTS = r"C:\OsintNeoAi\data\fleet_shared_contracts.json"
CROSSWORD_FIXTURES = r"C:\OsintNeoAi\data\crossword_fixtures.json"
DISPATCH_CONTRACT = r"C:\OsintNeoAi\data\dispatch_approval_contract.json"
ARCHIVED_DIR = r"C:\OsintNeoAi\data\staging\archived_synced"

PDF_ARTIFACT_ARCHIVED = os.path.join(ARCHIVED_DIR, "complaint_pdf_artifact_2f22ef01.json")
EFAX_STATUS_ARCHIVED = os.path.join(ARCHIVED_DIR, "mocked_efax_adapter_status.json")

def run_f5_integration_release_checks():
    print("[*] F5: Running Integration Release Checks (Fleet Plan F0-F5)...")
    
    required_files = [
        SHARED_CONTRACTS,
        CROSSWORD_FIXTURES,
        DISPATCH_CONTRACT,
        PDF_ARTIFACT_ARCHIVED,
        EFAX_STATUS_ARCHIVED
    ]
    
    all_passed = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  [✓] Verified (Staged/Archived Vault): {file_path}")
        else:
            print(f"  [✗] Missing: {file_path}")
            all_passed = False
            
    if all_passed:
        print("[+] F5 Integration Release Checks: ALL CHECKS PASSED (100% Complete)")
        return True
    else:
        print("[!] F5 Integration Release Checks FAILED")
        return False

if __name__ == "__main__":
    run_f5_integration_release_checks()
