# Implementation Plan: National CoC Graph Mapping Expansion

This plan outlines the process of expanding our unified graph network by programmatically parsing the nationwide HUD Continuum of Care (CoC) registry from `us_coc_forensic_pattern_master.md` and converting every CoC record into standardized nodes and edges (`nodes.json` and `edges.json`).

## User Review Required

> [!IMPORTANT]
> This expansion will enrich our graph network with several hundred new CoC (`ORGANIZATION`) and `STATE` nodes and their corresponding relationships (`LOCATED_IN`). Each CoC node will store critical forensic attributes including its environmental justice (EJ) flag, policing model, Mercy House presence, and forensic/operational notes.

## Proposed Changes

We will modify or extend the existing `extract_graph.py` to:
1. Parse the markdown table from `C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\us_coc_forensic_pattern_master.md` programmatically.
2. Standardize fields such as `policing_status`, `environmental_justice_flag`, `mercy_house_presence`, and `operational_notes`.
3. Add a new extraction method `extract_from_us_coc_pattern_master(self, filepath)` to standardise and ingest all table rows.
4. Regenerate and output the consolidated `nodes.json` and `edges.json`.

---

### Component: Graph Ingestion Engine

#### [MODIFY] [extract_graph.py](file:///c:/Users/HP/OneDrive/Documents/AG2OSINTNEOMAXX/extract_graph.py)
- Incorporate programmatic parsing of markdown tables to extract and map every CoC entry.
- Map columns to properties:
  - State Code -> `STATE` node (ID is State Code)
  - CoC Name -> `ORGANIZATION` node (ID is clean CoC Name)
  - CoC Number, Counties Covered, Policing Status, Environmental Justice Flag, Mercy House Presence, Operational Notes -> Node properties of the CoC node.
- Establish `LOCATED_IN` relationship from the CoC node to the `STATE` node.

---

## Verification Plan

### Automated Tests
- Execute `extract_graph.py`.
- Run validation checks to ensure no duplicate nodes/edges, verify total counts, and confirm the attributes are properly mapped.
- Verify that `nodes.json` and `edges.json` contain the newly added CoC data.

### Manual Verification
- Display a sample of the newly added CoCs and their properties from `nodes.json`.
- Verify the relationship structure for a state-specific CoC network.
