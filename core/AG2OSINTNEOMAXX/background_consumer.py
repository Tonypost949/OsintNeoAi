import logging
import json
import os
from typing import Dict, Any
from web3 import Web3
from core.AG2OSINTNEOMAXX.ai_worker_router import AIWorkerRouter
from core.AG2OSINTNEOMAXX.ledger_service import MasterLedgerService

logger = logging.getLogger("BackgroundConsumer")
logging.basicConfig(level=logging.INFO)

class DeepExtractionConsumer:
    def __init__(self, project_id: str):
        self.router = AIWorkerRouter(project_id=project_id)
        self.ledger = MasterLedgerService(project_id=project_id)
        
        # Web3 Oracle Configuration
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))
        self.admin_account = self.w3.eth.account.from_key(os.getenv("ADMIN_PRIVATE_KEY"))
        
        # Minimal ABIs to interact with the contracts
        self.staking_gate_address = os.getenv("STAKING_GATE_ADDRESS")
        self.escrow_address = os.getenv("MULTI_POOL_ESCROW_ADDRESS")
        
        self.staking_abi = [{"inputs": [{"internalType": "bytes32","name": "_assetHash","type": "bytes32"},{"internalType": "bool","name": "_isValid","type": "bool"}],"name": "reviewSubmission","outputs": [],"stateMutability": "nonpayable","type": "function"}]
        self.escrow_abi = [{"inputs": [{"internalType": "bytes32","name": "_assetHash","type": "bytes32"},{"internalType": "bytes32","name": "_parentHash","type": "bytes32"},{"internalType": "address","name": "_miner","type": "address"},{"internalType": "string[]","name": "_domainTags","type": "string[]"}],"name": "registerDataBlock","outputs": [],"stateMutability": "nonpayable","type": "function"}]
        
        self.staking_contract = self.w3.eth.contract(address=self.staking_gate_address, abi=self.staking_abi)
        self.escrow_contract = self.w3.eth.contract(address=self.escrow_address, abi=self.escrow_abi)

    def _send_oracle_transaction(self, contract_function) -> str:
        """Helper method to securely sign and broadcast Oracle transactions."""
        tx = contract_function.build_transaction({
            'from': self.admin_account.address,
            'nonce': self.w3.eth.get_transaction_count(self.admin_account.address),
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.admin_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.w3.to_hex(tx_hash)

    def process_queue_payload(self, queue_payload: Dict[str, Any]) -> None:
        asset_hash = queue_payload["asset_hash"]
        full_text = queue_payload["full_text"]
        miner_signature = queue_payload["miner_signature"]
        domain_tags = queue_payload["domain_tags"]
        parent_hash = queue_payload.get("parent_hash")
        
        logger.info(f"Starting heavy extraction for asset: {asset_hash}")

        # 1. Execute Heavy AI Parsing
        deep_meta = self.router.process_deep_extraction(full_text=full_text, asset_hash=asset_hash)
        is_valid_data = not deep_meta.get("is_spam", False)

        # 2. Append Event Sourced Version 2 to BigQuery
        enriched_description = json.dumps({"legal_citations": deep_meta.get("legal_citations", [])})
        self.ledger.record_asset(
            file_bytes=full_text.encode('utf-8'),
            miner_signature=miner_signature,
            title=f"Enriched: {queue_payload.get('title', 'Evidence')}",
            domain_tags=domain_tags,
            description=enriched_description,
            parent_hash=asset_hash,
            version_id=2
        )
        
        # 3. WEB3 ORACLE BRIDGE: Push validation to the blockchain
        bytes32_asset = Web3.to_bytes(hexstr=asset_hash) if asset_hash.startswith("0x") else Web3.keccak(text=asset_hash)
        bytes32_parent = Web3.to_bytes(hexstr=parent_hash) if parent_hash and parent_hash.startswith("0x") else bytes(32) # Default empty bytes32 if no parent

        try:
            # Lift Quarantine / Refund Stake or Slash [TASK-081]
            logger.info("Oracle broadcasting reviewSubmission to StakingGate...")
            tx_gate = self._send_oracle_transaction(
                self.staking_contract.functions.reviewSubmission(bytes32_asset, is_valid_data)
            )
            
            # Map UTXO Lineage for Payout Escrow
            if is_valid_data:
                logger.info("Oracle broadcasting registerDataBlock to MultiPoolEscrow...")
                tx_escrow = self._send_oracle_transaction(
                    self.escrow_contract.functions.registerDataBlock(bytes32_asset, bytes32_parent, Web3.to_checksum_address(miner_signature), domain_tags)
                )
            
            logger.info(f"Oracle Sync Complete. Gate TX: {tx_gate}")
        except Exception as e:
            logger.error(f"Web3 Oracle Bridge failed: {e}")
