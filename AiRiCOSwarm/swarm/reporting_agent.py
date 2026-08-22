"""WhistleblowerReportingAgent: Compiles court-admissible dossiers and False Claims Act reports."""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class WhistleblowerReportingAgent:
    def __init__(self, output_dir: str = "AiRiCOSwarm/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_dossier(self, target_name: str, findings: List[Dict[str, Any]], ai_synthesis: Optional[str] = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = target_name.upper().replace(' ', '_').replace('/', '_')
        filename = f"RICO_DOSSIER_{safe_name}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)

        lines = [
            f"# 🛡️ CONFIDENTIAL RICO & FCA INTELLIGENCE DOSSIER",
            f"**Target Vector:** {target_name}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Classification:** LAW ENFORCEMENT & QUI TAM REFERRAL EVIDENCE",
            "",
            f"## I. EXECUTIVE FORENSIC SYNTHESIS ({len(findings)} Predicate Hits Detected)",
            "",
            ai_synthesis if ai_synthesis else f"Analyzed {len(findings)} correlated records across BigQuery and local caches.",
            "",
            "## II. ITEMIZED EVIDENCE & PREDICATE LOG",
            ""
        ]
        if not findings:
            lines.append("*No direct predicate matches identified for this query vector.*")
        else:
            for f in findings:
                preds = ", ".join(f.get("predicates", []))
                lines.append(f"### 📍 {f.get('title', 'Record')}")
                lines.append(f"- **Date / Source:** `{f.get('date', 'N/A')}`")
                lines.append(f"- **Sender / Path:** `{f.get('sender', 'N/A')}`")
                lines.append(f"- **Flagged Predicates:** `{preds}`")
                lines.append(f"- **Evidence Excerpt:**\n> {f.get('description', '')[:500]}")
                lines.append("")

        with open(filepath, "w", encoding="utf-8") as out:
            out.write("\n".join(lines))
        return filepath
