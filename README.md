# OSINT Neo AI - Master Architecture

**OSINT Neo AI** is a decentralized, hybrid-cloud open-source intelligence platform. It bridges Web2 ingestion pipelines (Azure/Google Cloud/BigQuery) with Web3 smart contracts (Ethereum/Sepolia) to create a zero-trust, append-only ecosystem for digital forensics and verifiable investigative bounties.

---

## 🔗 Live Sepolia Testnet Architecture

The core financial and security logic is fully deployed and verified on the Sepolia Testnet.

| Contract | Address | Etherscan |
|----------|---------|-----------|
| **USDC (Settlement)** | `0x7236F4982a31537d07f3182A1CdAD3f3E4452A53` | [View on Etherscan](https://sepolia.etherscan.io/address/0x7236F4982a31537d07f3182A1CdAD3f3E4452A53#code) |
| **OSINT (Utility)** | `0xA74B3fAfd838fC273f7c6e201B6210AC2b3A0296` | [View on Etherscan](https://sepolia.etherscan.io/address/0xA74B3fAfd838fC273f7c6e201B6210AC2b3A0296#code) |
| **TFT (Tax-Funded)** | `0x0977909b254EC33C4D1039135F351B1d3Fb27F14` | [View on Etherscan](https://sepolia.etherscan.io/address/0x0977909b254EC33C4D1039135F351B1d3Fb27F14#code) |
| **StakingGate** | `0xdA7655b7007a1C7F8191066Bb9A69E4D8987E725` | [View on Etherscan](https://sepolia.etherscan.io/address/0xdA7655b7007a1C7F8191066Bb9A69E4D8987E725#code) ✅ |
| **MultiPoolEscrow** | `0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B` | [View on Etherscan](https://sepolia.etherscan.io/address/0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B#code) ✅ |

---

## ⚙️ The E2E Data Ingestion Pipeline

### 1. The Workspace UI (Frontend)
The user interface (`workspace_chat.html`) acts as a frictionless chat environment resembling standard LLM interfaces.
- **Multimodal Capture:** Users can upload documents, take physical pictures via WebRTC HTML5 canvas, or record audio memos via `MediaRecorder`.
- **Sybil Defense (Staking Gate):** Before payload submission, the client computes a local SHA-256 hash and prompts MetaMask to execute `stakeAndSubmit(hash)` on the `StakingGate` contract. Users must stake 100 OSINT to deter bot spam.

### 2. Evasive Azure Proxy (API Router)
The frontend sends the raw `FormData` to the FastAPI backend (`workspace_api.py`).
- **File Decoding:** Standard text/PDF files are decoded. Binary media is flagged for downstream Vision processing.
- **BigQuery V1 (Raw Append):** The payload is immediately logged to the BigQuery Master Ledger as `version_id = 1` using Workload Identity Federation (WIF) credentials (eliminating static key vulnerabilities).

### 3. Background AI Consumer
The heavy lifting is pushed to the background queue (`background_consumer.py`) to prevent API timeouts.
- **Gemini Extraction:** A Gemini-1.5-Pro micro-worker deeply parses the text, extracts specific entities (e.g., FOIA headers, legal citations, names), and tags the domain (e.g., `[OSINT]`, `[Tax-Funded]`).
- **BigQuery V2 (Enriched Append):** The structured metadata is appended to BigQuery as `version_id = 2`. The original file remains untouched.

### 4. The Web3 Oracle Bridge
Once the AI validates the data is not spam, the Python backend signs an Oracle transaction natively using `web3.py`.
- **Lifting Quarantine:** The Oracle calls `reviewSubmission(hash, true)` on the `StakingGate`, refunding the user's OSINT stake and granting +10 Reputation points.
- **Registering Lineage:** The Oracle maps the data's ancestry onto the blockchain via `registerDataBlock(assetHash, parentHash, minerAddress, domainTags)` on the `MultiPoolEscrow`.

### 5. Automated Multi-Pool Payouts
When a case is solved and an organization deposits fiat-backed USDC into the `MultiPoolEscrow`:
- **The UTXO Provenance Graph:** The contract traverses the `parentHash` pointers to determine exactly who contributed to the case.
- **The 40/30/30 Split:** The funds are deterministically distributed across the lineage tree (40% to the Catalyst, 30% to the Corroborator, 30% to the Closer).
- **Domain Minting:** Based on the `domainTags` array, the system dynamically mints secondary utility rewards (OSINT or TFT) to the contributors.

---

## 🔒 Security Design (The 5 Vulnerabilities Sealed)
1. **Pointer Corruption:** Eliminated by strict `parentHash` cryptographic linking (UTXO style).
2. **File Forgery:** Prevented by SHA-256 hashing at the point of upload and append-only database schemas.
3. **Sybil Attacks:** Mitigated by the Web3 Staking Gate requiring collateralized submissions.
4. **Compute Bottlenecks:** Solved by offloading heavy extraction to the asynchronous `background_consumer`.
5. **Rate-Limit Guillotine:** Bypassed using off-peak cron caching (`bulk_caching_queue.py`) instead of live API queries.
