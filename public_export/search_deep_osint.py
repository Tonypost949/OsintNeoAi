import json
import os

def search_deep_osint_vectors():
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            categories = {
                "mercy_house_records": ["mercy", "mercy house", "shelter_intake", "homeless_system"],
                "chase_bank_shutdown": ["chase", "jpmorgan", "bank_account", "account_closure", "wire_freeze"],
                "identity_theft_records": ["id theft", "identity_theft", "stolen_identity", "impersonation", "fraud_alert"],
                "tmobile_account_breach": ["tmobile", "t-mobile", "sim_swap", "cellular_breach", "phone_hijack"],
                "identity_theft_insurance": ["id_theft_insurance", "insurance_claim", "fraud_insurance", "identity_policy"]
            }
            
            results = {cat: [] for cat in categories}
            
            for item in data:
                item_str = json.dumps(item).lower()
                for cat, kw_list in categories.items():
                    if any(kw in item_str for kw in kw_list):
                        results[cat].append(item)
            
            summary = {cat: len(results[cat]) for cat in results}
            print("[+] Deep OSINT Vector Evidence Summary:")
            print(json.dumps(summary, indent=2))
            
            output_file = r"C:\OsintNeoAi\DEEP_OSINT_VECTOR_AUDIT_REPORT.json"
            with open(output_file, "w", encoding="utf-8") as out:
                json.dump({"summary": summary, "details": results}, out, indent=2)
            print(f"[+] Full audit package written to: {output_file}")

if __name__ == "__main__":
    search_deep_osint_vectors()
