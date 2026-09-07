import os
import json
import logging
import uuid
import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Smart Contract Addresses from deployed infrastructure
TFT_CONTRACT = os.environ.get("TFT_TOKEN_ADDRESS", "0x0977909b254EC33C4D1039135F351B1d3Fb27F14")
OSINT_CONTRACT = os.environ.get("OSINT_TOKEN_ADDRESS", "0xA74B3fAfd838fC273f7c6e201B6210AC2b3A0296")
BRIDGE_CONTRACT = os.environ.get("MULTI_POOL_ESCROW_ADDRESS", "0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B")

class DualAuditTokenBridge:
    """
    Finalized Bridge architecture for the OSINT Exchange.
    Hooks directly into the Task System:
    When a user completes a Suggestive Work or FOIA task, they are rewarded with OSINT Tokens.
    OSINT Tokens can be bridged to TaxFunded Tokens (TFT) for monetary/grant rewards.
    """
    def __init__(self, ledger_path="crypto_ledger_tracker.json"):
        self.ledger_path = ledger_path
        self._load_ledger()

    def _load_ledger(self):
        try:
            with open(self.ledger_path, "r") as f:
                self.ledger = json.load(f)
            if "metrics" not in self.ledger:
                self.ledger["metrics"] = {}
            if "total_osint_minted" not in self.ledger["metrics"]:
                self.ledger["metrics"]["total_osint_minted"] = 0
            if "total_tft_bridged" not in self.ledger["metrics"]:
                self.ledger["metrics"]["total_tft_bridged"] = 0
        except Exception:
            self.ledger = {"ledger_blocks": [], "metrics": {"total_osint_minted": 0, "total_tft_bridged": 0}}

    def _save_ledger(self):
        with open(self.ledger_path, "w") as f:
            json.dump(self.ledger, f, indent=2)

    def reward_task_completion(self, task_id, task_title, user_wallet):
        """
        Triggered when a task in TASKS.md is marked as DONE.
        Mints 100 OSINT Tokens as forensic proof-of-work.
        """
        reward_amount = 100
        logger.info(f"Task {task_id} completed. Minting {reward_amount} OSINT Tokens to {user_wallet}...")
        
        block = {
            "tx_id": f"0x{uuid.uuid4().hex}",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "type": "MINT",
            "token_symbol": "OSINT",
            "amount": reward_amount,
            "to_wallet": user_wallet,
            "description": f"Forensic Proof-of-Work Reward for Task: {task_id} ({task_title})",
            "contract": OSINT_CONTRACT
        }
        
        self.ledger["ledger_blocks"].insert(0, block)
        self.ledger["metrics"]["total_osint_minted"] += reward_amount
        self.save_state()
        return block

    def bridge_osint_to_tft(self, user_wallet, osint_amount):
        """
        Allows users to bridge their earned OSINT Tokens into TaxFunded Tokens (TFT).
        Bridge exchange rate: 10 OSINT = 1 TFT (representing actionable grant/bounty value).
        """
        tft_amount = osint_amount / 10.0
        logger.info(f"Bridging {osint_amount} OSINT -> {tft_amount} TFT for wallet {user_wallet}...")
        
        block = {
            "tx_id": f"0x{uuid.uuid4().hex}",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "type": "BRIDGE_SWAP",
            "token_symbol": "TFT",
            "amount_in": f"{osint_amount} OSINT",
            "amount_out": f"{tft_amount} TFT",
            "to_wallet": user_wallet,
            "description": "DualAuditTokenBridge Swap Execution",
            "contract": BRIDGE_CONTRACT
        }
        
        self.ledger["ledger_blocks"].insert(0, block)
        self.ledger["metrics"]["total_tft_bridged"] += tft_amount
        self.save_state()
        return block

    def save_state(self):
        self._save_ledger()
        logger.info("[+] Dual-Ledger state synchronized and saved.")

if __name__ == "__main__":
    # Test the final pipeline
    bridge = DualAuditTokenBridge()
    bridge.reward_task_completion("TASK-SUGGEST-003", "Deep OCR Scan on 17642 Beach Blvd", "0xUserWallet123")
    bridge.bridge_osint_to_tft("0xUserWallet123", 100)
    print("OSINT Exchange Crypto Pipeline executed successfully.")
