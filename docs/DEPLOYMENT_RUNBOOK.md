# OSINT Neo AI - Master Deployment Runbook

This document outlines the strict execution sequence required to bridge the Web3 Smart Contracts (Blockchain) with the Web2 Ingestion Engine (Azure/Python). 

**CRITICAL PREREQUISITES:**
1. A funded Web3 Wallet (MetaMask) containing testnet ETH (e.g., Sepolia).
2. An active RPC URL from an infrastructure provider (e.g., Alchemy or Infura).
3. `core/web3/.env` fully populated with the `PRIVATE_KEY` and `SEPOLIA_RPC_URL`.

---

## Phase 1: Web3 Infrastructure Deployment

Execute this sequence to deploy the utility tokens, the Staking Gate, and the Multi-Pool Escrow to the blockchain.

```bash
# 1. Navigate to the Web3 directory
cd core/web3

# 2. Install required Node.js dependencies
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox @openzeppelin/contracts dotenv

# 3. Compile the Solidity Smart Contracts
npx hardhat compile

# 4. Deploy the infrastructure to the Sepolia Testnet
npx hardhat run scripts/deploy_infrastructure.js --network sepolia
```

### ⚠️ THE CRITICAL HANDOFF (Address Mapping)

When Step 4 finishes, the terminal will output five live contract addresses. **Do not clear your terminal.** You must immediately map these addresses to bridge the Web2 and Web3 ecosystems:

1. **Client-Side:** Open `public/workspace_chat.html` and replace the placeholder on line 10 with the printed `STAKING_GATE_ADDRESS`.
2. **Server-Side Oracle:** Open `core/web3/.env` (and your Azure Environment Variables) and paste all five addresses (`STAKING_GATE_ADDRESS`, `MULTI_POOL_ESCROW_ADDRESS`, `OSINT_TOKEN_ADDRESS`, `TFT_TOKEN_ADDRESS`, `USDC_ADDRESS`). The Python backend requires these to sign Oracle validation transactions.

---

## Phase 2: Etherscan Verification

*Wait exactly 60 seconds after Phase 1 completes* to ensure the blockchain has fully indexed the contract bytecode. Then, publish the source code for public auditing:

```bash
# Verify the contracts on Etherscan
npx hardhat run scripts/verify_contracts.js --network sepolia
```

*Note: Ensure your `ETHERSCAN_API_KEY` is present in the `.env` file before running.*

---

## Phase 3: Web2 Backend Ignition

With the blockchain waiting and the Oracle addresses patched, start the Python Azure ingestion API:

```bash
# Return to the project root
cd ../..

# Start the FastAPI backend
uvicorn api.main:app --reload --port 8000
```

### System Verification

Once the Uvicorn server is live at `http://localhost:8000`:

1. Open `public/workspace_chat.html` in a web browser.
2. Click to connect your MetaMask wallet.
3. Upload a test document or image to trigger the ingestion pipeline.
4. Confirm MetaMask prompts for the staking transaction, and verify the Azure console logs the BigQuery V1 Append and the Background Worker V2 Extraction.
