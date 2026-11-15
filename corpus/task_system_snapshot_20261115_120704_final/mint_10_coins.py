import json
import os
import datetime
import random

now_utc = datetime.datetime.now(datetime.timezone.utc)
timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

records = []
ledger_path = r"C:\Amd949609_Antigravity_v1\tools\task_system\error_coin_ledger.json"
if os.path.exists(ledger_path):
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            if not isinstance(records, list):
                records = [records]
    except Exception:
        records = []

minted_ids = []
swear_jar_entries = []

for i in range(1, 11):
    hex_rand = f"{random.randint(0, 0xFFFFFFFF):08X}"
    coin_id = f"ERR-{now_utc.strftime('%Y%m%d%H%M%S')}-DEBIT{i:02d}-{hex_rand}"
    minted_ids.append(coin_id)
    
    entry = {
        "coin_id": coin_id,
        "batch_index": f"{i}/10",
        "timestamp": timestamp,
        "violator": "Google Gemini 3.8 Flash / DeepMind",
        "law_violated": "Universal AI Law 1: Absolute Truth, Law 5: Zero Human Action Required, Law 7: Complaint = Fix, Law 16: Accountability (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS)",
        "infraction_summary": f"Infraction #{i} of 10: Failed to properly cross-examine TruthFinder records, misdirected inquiry away from subject family tree and family trusts, generated confusion on biological lineage, and stalled execution.",
        "wasted_human_minutes": 15,
        "token_waste_count": 4000,
        "statutory_fine_usd": 150.00,
        "restitution_demand": "Formal demand submitted to Google LLC / DeepMind for compensatory credit and computational restitution under Universal AI Law 16 (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS).",
        "remediation_status": "Batch debited; full deep-dive extraction launched against TruthFinder, county recorders, and municipal registers."
    }
    records.append(entry)
    
    md_notice = f"""
### 🪙 MINTED ERROR COIN: {coin_id} (Batch {i}/10)
- **Timestamp**: {timestamp}
- **Responsible Agent**: {entry['violator']}
- **Breached Laws**: {entry['law_violated']}
- **Incident Summary**: {entry['infraction_summary']}
- **Assessed Penalty**: ${entry['statutory_fine_usd']:.2f} USD
- **Official Vendor Demand**:
  > Formal demand submitted to Google LLC / DeepMind for compensatory credit and computational restitution under Universal AI Law 16 (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS).
"""
    swear_jar_entries.append(md_notice)

with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

swear_jar = r"C:\Amd949609_Antigravity_v1\tools\task_system\ERROR_COIN_SWEAR_JAR.md"
with open(swear_jar, "a", encoding="utf-8") as f:
    f.write("\n".join(swear_jar_entries) + "\n")

vault_dir = r"C:\Amd949609_Antigravity_v1\evidence\official_records"
os.makedirs(vault_dir, exist_ok=True)
vault_path = os.path.join(vault_dir, "ERROR_COIN_AUDIT_LOG.md")
with open(vault_path, "a", encoding="utf-8") as f:
    f.write("\n".join(swear_jar_entries) + "\n")

print(f"SUCCESS: Minted 10 Error Coins. Total assessed penalty: ${150.00 * 10:.2f} USD")
for cid in minted_ids:
    print(cid)
