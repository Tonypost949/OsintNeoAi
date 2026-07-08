"""
RICO Network Graph Generator — Gemini Multi-Agent Pipeline
Uses google-genai with Vertex AI (project billing, no API key).
Phases: Entity Extraction → Graph Construction → Intelligence Summary

Usage:  C:\Python314\python.exe ag2_rico_graph.py
"""
import csv
import json
from pathlib import Path
from google import genai
from google.genai import types

# ── Client Config (Vertex AI with ADC) ──────────────────────────
import os
import subprocess

# Auto-detect project ID via gcloud config
try:
    project_id = subprocess.check_output(
        ["gcloud", "config", "get-value", "project"],
        text=True
    ).strip()
except Exception:
    project_id = "project-9c94c2fa-3af4-49f1-a7b"

if not project_id or project_id == "project-743aab84-f9a5-4ec7-954":
    project_id = "project-9c94c2fa-3af4-49f1-a7b"

client = genai.Client(
    vertexai=True,
    project=project_id,
    location="us-central1",
)
print(f"Using Vertex AI client with project: {project_id}")




WORK_DIR = Path(r"C:\Users\HP\OneDrive\Documents\opencode_work")
CSV_FILES = {
    "rico_matrix": WORK_DIR / "rico_evidence_matrix.csv",
    "bq_matches": WORK_DIR / "bq_rico_matches.csv",
    "hb_llcs": WORK_DIR / "HB_Suspicious_LLC_Matrix.csv",
    "out_of_state": WORK_DIR / "HB_OutOfState_LLCs.csv",
    "mercy_crossref": WORK_DIR / "mercy_targeted_crossref.csv",
    "ppp_rico": WORK_DIR / "ppp_rico_rico_matches.csv",
}

MODEL = "gemini-2.5-flash"


# ── CSV Loading ────────────────────────────────────────────────
def load_csv_head(path: Path, max_rows: int = 50) -> str:
    if not path.exists():
        return f"[FILE NOT FOUND: {path.name}]"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        rows = []
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(row)
    lines = [", ".join(headers)]
    for r in rows:
        lines.append(", ".join(r))
    return "\n".join(lines)


def load_csv_summary(path: Path) -> str:
    if not path.exists():
        return f"[FILE NOT FOUND: {path.name}]"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        return f"[EMPTY FILE: {path.name}]"
    cols = list(rows[0].keys())
    return f"File: {path.name}\nRows: {len(rows)}\nColumns: {', '.join(cols)}"


def build_csv_context() -> str:
    parts = ["=== AVAILABLE DATA SOURCES ===\n"]
    for name, path in CSV_FILES.items():
        parts.append(f"[{name}] {load_csv_summary(path)}")
    return "\n".join(parts)


def build_sample_data() -> str:
    parts = []
    for name, path in CSV_FILES.items():
        if path.exists():
            parts.append(f"\n--- SAMPLE: {name} (first 20 rows) ---")
            parts.append(load_csv_head(path, max_rows=20))
    return "\n".join(parts)


# ── Agent System Prompts ───────────────────────────────────────
ENTITY_SYSTEM = """You are a forensic OSINT analyst specializing in financial network analysis.
Extract entities and relationships from CSV data about LLCs, PPP loans, property transactions, and nonprofits.

RULES:
- Identify ALL unique entities: LLCs, individuals, properties, nonprofits, lenders
- Map relationships: ownership, loan disbursement, property transfer, shared addresses, nonprofit board connections
- Flag anomalies: out-of-state LLCs receiving CA PPP loans, circular ownership, shared mail addresses
- Output structured JSON with nodes and edges for graph generation
- Return ONLY valid JSON, no markdown fencing"""

GRAPH_SYSTEM = """You are a graph data architect. Given extracted entities and relationships,
generate a DOT-format graph and a JSON adjacency list.

RULES:
- Nodes: id, label, type (llc/individual/property/nonprofit/lender), metadata
- Edges: source, target, relationship_type, weight (based on financial magnitude)
- Cluster related entities into subgraphs
- Highlight high-value nodes (>$500K PPP loans) with distinct styling
- Include a summary table of top 20 entities by total dollar volume"""

SUMMARY_SYSTEM = """You are a forensic report writer. Write a concise intelligence summary covering:
1. NETWORK TOPOLOGY: clusters, key hubs, total entities
2. FINANCIAL FLOWS: total PPP dollars mapped, concentration patterns
3. ANOMALIES: circular ownership, shell patterns, state mismatches
4. KEY ENTITIES: top 10 nodes by connectivity and dollar volume
5. RECOMMENDATIONS: entities warranting deeper investigation
Keep under 2000 words. Use bullet points. Be specific with dollar amounts and dates."""


# ── Agent Runner ───────────────────────────────────────────────
def run_agent(system_prompt: str, user_prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=8192,
        ),
    )
    return response.text


# ── Main Pipeline ──────────────────────────────────────────────
def main():
    print("=" * 60)
    print("RICO NETWORK GRAPH GENERATOR")
    print(f"Model: {MODEL} via Vertex AI")
    print(f"Project: project-743aab84-f9a5-4ec7-954")
    print("=" * 60)

    csv_context = build_csv_context()
    sample_data = build_sample_data()

    # ── PHASE 1: Entity Extraction ─────────────────────────────
    print("\n[PHASE 1] Entity Extraction...")
    extraction_prompt = f"""Analyze the following CSV data and extract all entities and relationships.

{csv_context}

{sample_data}

Output a structured JSON object with:
- "entities": list of {{id, type, name, metadata}}
- "relationships": list of {{source_id, target_id, type, weight, details}}

Focus on:
1. LLC-to-person ownership links
2. LLC-to-PPP-loan disbursements
3. Property address clustering (multiple LLCs at same address)
4. Shared mail addresses across entities
5. Nonprofit connections to LLCs
6. Out-of-state patterns

Return ONLY valid JSON, no markdown fencing."""

    entity_text = run_agent(ENTITY_SYSTEM, extraction_prompt)
    print(f"  Done: {len(entity_text)} chars")

    # ── PHASE 2: Graph Construction ────────────────────────────
    print("\n[PHASE 2] Graph Construction...")
    graph_prompt = f"""Given the following extracted entity data, generate a network graph.

{entity_text}

Output:
1. A DOT-format graph definition
2. A JSON adjacency list
3. A table of the top 20 entities ranked by total connected dollar volume

Make the graph readable: group LLCs by property address, color-code by entity type."""

    graph_text = run_agent(GRAPH_SYSTEM, graph_prompt)
    print(f"  Done: {len(graph_text)} chars")

    # ── PHASE 3: Intelligence Summary ──────────────────────────
    print("\n[PHASE 3] Intelligence Summary...")
    summary_prompt = f"""Write a forensic intelligence summary of this RICO network analysis.

EXTRACTED DATA:
{entity_text}

GRAPH OUTPUT:
{graph_text}

Cover: network topology, financial flows, anomalies, key entities, recommendations."""

    summary_text = run_agent(SUMMARY_SYSTEM, summary_prompt)
    print(f"  Done: {len(summary_text)} chars")

    # ── Save Outputs ───────────────────────────────────────────
    out_dir = WORK_DIR / "ag2_output"
    out_dir.mkdir(exist_ok=True)

    (out_dir / "entities.json").write_text(entity_text, encoding="utf-8")
    (out_dir / "graph_output.txt").write_text(graph_text, encoding="utf-8")
    (out_dir / "intelligence_summary.txt").write_text(summary_text, encoding="utf-8")

    print(f"\n[OUTPUTS SAVED] {out_dir}/")
    print(f"  - entities.json ({len(entity_text)} chars)")
    print(f"  - graph_output.txt ({len(graph_text)} chars)")
    print(f"  - intelligence_summary.txt ({len(summary_text)} chars)")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
