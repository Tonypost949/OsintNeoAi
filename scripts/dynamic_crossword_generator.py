import os
import json
import hashlib
from datetime import datetime, timezone

OUTPUT_DIR = r"C:\OsintNeoAi\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PUZZLE_FILE = os.path.join(OUTPUT_DIR, "daily_crypto_crossword.json")

CLUE_BANK = [
    {
        "id": "CLUE_01",
        "clue": "Vadose-zone heavy metal peaking at 980 µg/kg at Boring B9A (Case 20IC002)",
        "answer": "HEXAVALENT CHROMIUM",
        "statutory_anchor": "Cal. Health & Safety Code § 25300 (HSAA)"
    },
    {
        "id": "CLUE_02",
        "clue": "Agricultural irrigation well requiring OCHCA destruction permitting (State Well 05S/11W-25M09)",
        "answer": "OCWD W-4150",
        "statutory_anchor": "OCHCA Water Quality Section"
    },
    {
        "id": "CLUE_03",
        "clue": "State oversight agreement required to transition temporary shelter to permanent housing",
        "answer": "VOLUNTARY OVERSIGHT AGREEMENT",
        "statutory_anchor": "DTSC HERO Note 3"
    },
    {
        "id": "CLUE_04",
        "clue": "Mandatory California motion to set aside void judgment due to suppressed toxic records",
        "answer": "CCP 473D",
        "statutory_anchor": "Cal. Civ. Proc. Code § 473(d)"
    },
    {
        "id": "CLUE_05",
        "clue": "Statutory funding penalty incurred if residential NFA is not secured before Jan 5 2026",
        "answer": "6.09 MILLION LMIHAF",
        "statutory_anchor": "Cal. Gov. Code § 65962.5"
    }
]

def generate_daily_crossword():
    print("[*] Generating Dynamic Daily Forensic Crossword Puzzle...")
    
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seed_str = f"CROSSWORD_SEED_{date_str}"
    puzzle_hash = f"0x{hashlib.sha256(seed_str.encode('utf-8')).hexdigest()}"
    
    puzzle_data = {
        "puzzle_id": puzzle_hash,
        "date": date_str,
        "title": "The Chronicle Daily OSINT & Environmental Forensic Puzzle",
        "reward_tokens": "50 TFT",
        "clues": CLUE_BANK,
        "verification_hash": puzzle_hash
    }
    
    with open(PUZZLE_FILE, "w", encoding="utf-8") as f:
        json.dump(puzzle_data, f, indent=2)
        
    print(f"[+] Dynamic Crossword Generated at: {PUZZLE_FILE}")
    print(f"[+] Puzzle Hash: {puzzle_hash}")

if __name__ == "__main__":
    generate_daily_crossword()
