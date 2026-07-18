# Implementation Plan: OSINT Data Schema Extraction and Graph Creation

This plan outlines the process for reading three specific CSV source files, analyzing their data quality, mapping them to our unified OSINT schema, and building a transformation pipeline to generate `nodes.json` and `edges.json`.

## User Review Required

> [!IMPORTANT]
> The source data contains complex nested lists (such as `hud_pit_list` in state records) and multi-value fields (such as semicolon-separated lists in `ppp_names` and `loan_locations`). Our extraction script will parse these dynamically to form precise nodes and relationships.

## Proposed Mapping Schema

Here is how each source column is mapped to our defined node and relationship types.

### Node Definitions
- **`ORGANIZATION`**: Corporations, LLCs, Trusts, and Continua of Care (CoCs) detected in `owner_name`, `Owner1`, `Owner2`, `LastSeller`, and `hud_pit_list`.
- **`PERSON`**: Non-corporate entities identified as owners or sellers.
- **`PROPERTY`**: Parcels identified by Assessor's Parcel Number (`APN`) and physical site addresses.
- **`ADDRESS`**: Mailing and registered office locations.
- **`PPP_LOAN`**: PPP funding nodes containing total amounts, loan counts, and forgiveness metrics.
- **`STATE`**: Regional entities (e.g., CA, OH, RI).

### Relationship Definitions
- **`OWNS`**: Links `PERSON`/`ORGANIZATION` to a `PROPERTY`.
- **`REGISTERED_AT`**: Links `PERSON`/`ORGANIZATION` to their registered mailing `ADDRESS`.
- **`RECEIVED_PPP`**: Links `ORGANIZATION`/`PERSON` to a `PPP_LOAN`.
- **`LOCATED_IN`**: Links `PROPERTY` or `ADDRESS` to a `STATE`.
- **`CONNECTED_TO`**: Links a seller (`LastSeller`) to the current owner, or other related entity-to-entity networks.

---

### Source File 1: `out_of_state_llc_ppp_network.csv`
- **Path**: `C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv`
- **Mapping Strategy**:
  - `owner_name` -> `ORGANIZATION` / `PERSON` (based on suffix)
  - `property_address` + `apn` -> `PROPERTY` node
  - `property_mail_address` + `property_mail_city` -> `ADDRESS` node
  - `ppp_names`, `ppp_total_amount`, `ppp_total_forgiven` -> `PPP_LOAN` node
  - **Relationships**:
    - `owner_name` - `OWNS` -> `PROPERTY`
    - `owner_name` - `REGISTERED_AT` -> `ADDRESS`
    - `owner_name` - `RECEIVED_PPP` -> `PPP_LOAN`

### Source File 2: `national_audits_all_state_records.csv`
- **Path**: `C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_all_state_records.csv`
- **Mapping Strategy**:
  - `state` -> `STATE` node
  - `hud_pit_list` -> Parse nested JSON objects. Extract CoC as `ORGANIZATION` node.
  - **Relationships**:
    - `ORGANIZATION` (CoC) - `LOCATED_IN` -> `STATE`

### Source File 3: `HB_Suspicious_LLC_Matrix.csv`
- **Path**: `C:\Users\HP\OneDrive\Documents\opencode_work\HB_Suspicious_LLC_Matrix.csv`
- **Mapping Strategy**:
  - `Owner1`, `Owner2` -> `ORGANIZATION` / `PERSON` nodes
  - `SiteAddress` + `APN` -> `PROPERTY` node
  - `MailAddress` + `MailCity` -> `ADDRESS` node
  - `LastSeller` -> `ORGANIZATION` / `PERSON` node
  - **Relationships**:
    - `Owner1` / `Owner2` - `OWNS` -> `PROPERTY`
    - `Owner1` / `Owner2` - `REGISTERED_AT` -> `ADDRESS`
    - `LastSeller` - `CONNECTED_TO` -> `Owner1`/`Owner2` (via transaction connection)

---

## Technical Extraction Script Design

We will build a clean, robust Python script `extract_graph_network.py` that:
1. Deduplicates nodes across all files based on normalized keys (e.g., standardizing company suffixes and lowercase addresses).
2. Generates unique, stable IDs for each node.
3. Outputs structured JSON streams mapping directly to `nodes.json` and `edges.json`.

## Verification Plan

### Automated Tests
- We will execute the Python script and inspect the JSON schema validation.
- Run a statistics validator to print node/edge counts and relationship lists.

### Manual Verification
- Display the first 10 example relationships to verify link accuracy.
