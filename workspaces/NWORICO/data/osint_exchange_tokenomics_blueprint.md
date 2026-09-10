# Dual-Ledger OSINT and Tax-Funded Token Architecture

## Core Concept
A multi-ledger blockchain ecosystem where "mining" is replaced by "data ingestion". Users submit verified open-source intelligence, public records, and FOIA requests to mint utility tokens.

## The Ledgers
1. **OSINT Coin (Ledger A):** For general intelligence, corporate fraud, and open-source data.
2. **Tax-Funded Token (Ledger B):** Strictly for data involving taxpayer money (government, non-profits, municipal grants).
3. **Future Extensibility (e.g., Med Coin):** The system uses a Master Indexing Layer so a single piece of evidence can be tagged (e.g., `[TAX, MED]`) and exist simultaneously on multiple ledgers without data duplication.

## Technical Mandates for the Backend
*   **UTXO Data Lineage:** Evidence must act like Bitcoin UTXOs. Every new submission hashes to its parent. This creates an immutable chain of custody (Catalyst -> Corroborator -> Closer).
*   **BigQuery Schema:** Use nested and repeated fields for multi-ledger tagging. Store `domain_tags` as `ARRAY<STRING>`. This allows instant querying (`UNNEST(domain_tags)`) when new token ledgers are added on day 300.
*   **Bounty Split Smart Contracts:** If a case yields a Real-World Asset (RWA) bounty, the smart contract reads the UTXO lineage graph in BigQuery and algorithmically splits the payout among the specific contributors.

## Compliance
*   Keep as a strict utility/RWA token.
*   Defer any options, futures, or derivatives until institutional scale is reached.
*   Payouts and escrow sit in transparent, multi-signature smart contracts utilizing stablecoins (USDC) for external fiat bridges.
