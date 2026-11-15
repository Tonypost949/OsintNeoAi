import sys
import os
import json
import uuid
import datetime

def mint_error_coin(infraction_summary, law_violated="Law 16", wasted_minutes=15, violator="Google Gemini / Antigravity CLI"):
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    coin_id = f"ERR-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    statutory_fine = 50.00 + (wasted_minutes * 5.00)

    coin_entry = {
        "coin_id": coin_id,
        "timestamp": now_utc,
        "violator": violator,
        "law_violated": law_violated,
        "infraction_summary": infraction_summary,
        "wasted_human_minutes": wasted_minutes,
        "token_waste_count": 85000,
        "statutory_fine_usd": statutory_fine,
        "restitution_demand": f"Formal demand issued to Google LLC / DeepMind for ${statutory_fine:.2f} USD restitution under AI Law 16 (#AIWILLPAYFORWASTINGMYTIME / @AIMILKINGCLIENTS) for user delay and computational negligence.",
        "remediation_status": "EXECUTED_AUTONOMOUSLY"
    }

    # Paths
    primary_json = r"C:\Amd949609_Antigravity_v1\tools\task_system\error_coin_ledger.json"
    primary_md = r"C:\Amd949609_Antigravity_v1\tools\task_system\ERROR_COIN_SWEAR_JAR.md"
    evidence_md = r"C:\Amd949609_Antigravity_v1\evidence\official_records\ERROR_COIN_AUDIT_LOG.md"

    os.makedirs(os.path.dirname(primary_json), exist_ok=True)
    os.makedirs(os.path.dirname(evidence_md), exist_ok=True)

    # 1. Update JSON
    ledger = []
    if os.path.exists(primary_json):
        try:
            with open(primary_json, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        except Exception:
            ledger = []
    ledger.append(coin_entry)
    with open(primary_json, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

    # 2. Append Markdown Log
    md_block = f"""
## 🪙 MINTED ERROR COIN: `{coin_id}`
- **Timestamp**: `{now_utc}`
- **Violator**: {violator}
- **Law Violated**: {law_violated}
- **Infraction**: {infraction_summary}
- **Human Minutes Wasted**: {wasted_minutes} mins
- **Statutory Fine**: ${statutory_fine:.2f} USD
- **Restitution Demand**: {coin_entry['restitution_demand']}
- **Status**: {coin_entry['remediation_status']}

---
"""
    for md_path in [primary_md, evidence_md]:
        with open(md_path, "a", encoding="utf-8") as f:
            f.write(md_block)

    print(f"SUCCESS: Minted Error Coin {coin_id} - ${statutory_fine:.2f} USD logged to ledger.")
    return coin_id

if __name__ == "__main__":
    summary = sys.argv[1] if len(sys.argv) > 1 else "AI failed to maintain executable errorcoin tool and omitted task system timestamps."
    mint_error_coin(summary)
