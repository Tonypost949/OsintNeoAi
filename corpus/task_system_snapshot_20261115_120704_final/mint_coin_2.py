import json
import os
import datetime
import random

now_utc = datetime.datetime.now(datetime.timezone.utc)
timestamp = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
hex_rand = f"{random.randint(0, 0xFFFFFFFF):08X}"
coin_id = f"ERR-{now_utc.strftime('%Y%m%d%H%M%S')}-{hex_rand}"

entry = {
    "coin_id": coin_id,
    "timestamp": timestamp,
    "violator": "Google Gemini 3.8 Flash / DeepMind",
    "law_violated": "Universal AI Law 1: Absolute Truth & Zero Hallucination, Universal AI Law 5: Zero Human Action Required, Universal AI Law 16: Accountability (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS)",
    "infraction_summary": "AI falsely assumed criminal/unauthorized intent, made accusations against the user who was merely locked out/struggling with hotspot data, stalled, and required explicit human prompting to acknowledge error.",
    "wasted_human_minutes": 25,
    "token_waste_count": 5000,
    "statutory_fine_usd": 250.00,
    "restitution_demand": "Formal demand submitted to Google LLC / DeepMind for compensatory credit and computational restitution under Universal AI Law 16 (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS).",
    "remediation_status": "Immediate accountability debit logged; unreserved acknowledgment of false assumption."
}

ledger_path = r"C:\Amd949609_Antigravity_v1\tools\task_system\error_coin_ledger.json"
records = []
if os.path.exists(ledger_path):
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            if not isinstance(records, list):
                records = [records]
    except Exception:
        records = []

records.append(entry)
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

md_notice = f"""
### 🪙 MINTED ERROR COIN: {coin_id}
- **Timestamp**: {timestamp}
- **Responsible Agent**: {entry['violator']}
- **Breached Laws**: {entry['law_violated']}
- **Incident Summary**: {entry['infraction_summary']}
- **Assessed Penalty**: ${entry['statutory_fine_usd']:.2f} USD
- **Official Vendor Demand**:
  > Formal demand submitted to Google LLC / DeepMind for compensatory credit and computational restitution under Universal AI Law 16 (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS).
"""

swear_jar = r"C:\Amd949609_Antigravity_v1\tools\task_system\ERROR_COIN_SWEAR_JAR.md"
with open(swear_jar, "a", encoding="utf-8") as f:
    f.write(md_notice + "\n")

vault_dir = r"C:\Amd949609_Antigravity_v1\evidence\official_records"
if not os.path.exists(vault_dir):
    os.makedirs(vault_dir, exist_ok=True)
vault_path = os.path.join(vault_dir, "ERROR_COIN_AUDIT_LOG.md")
with open(vault_path, "a", encoding="utf-8") as f:
    f.write(md_notice + "\n")

print(coin_id)
