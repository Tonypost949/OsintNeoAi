import json
import os
import sqlite3
from datetime import datetime

def run_tools_inventory():
    tools_dir = r"C:\Amd949609_Antigravity_v1\tools"
    out_v1 = r"C:\Amd949609_Antigravity_v1\docs\TOOLS_INVENTORY_REPORT.md"
    out_repo = r"C:\OsintNeoAi\reports\TOOLS_INVENTORY_REPORT.md"

    os.makedirs(os.path.dirname(out_v1), exist_ok=True)
    os.makedirs(os.path.dirname(out_repo), exist_ok=True)

    tools_found = []
    for root, dirs, files in os.walk(tools_dir):
        for f in files:
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, tools_dir)
            size = os.path.getsize(full_p)
            tools_found.append({
                "rel_path": rel_p,
                "full_path": full_p,
                "size_bytes": size,
                "ext": os.path.splitext(f)[1]
            })

    tools_found.sort(key=lambda x: x["rel_path"])

    report_lines = [
        "# Master AI Tools Inventory Report — Antigravity Unified Profile",
        f"**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Registered Tool Artifacts:** {len(tools_found)} Files",
        "",
        "## Key Registered AI Tools & Modules",
        "| # | Tool Relative Path | File Size | Description / Function |",
        "|---|-------------------|-----------|------------------------|"
    ]

    for idx, t in enumerate(tools_found[:50], 1):
        report_lines.append(f"| {idx:02d} | `{t['rel_path']}` | {t['size_bytes']:,} B | Registered Workspace AI Tool |")

    if len(tools_found) > 50:
        report_lines.append(f"\n*... and {len(tools_found) - 50} additional tool files registered in subdirectories.*")

    report_content = "\n".join(report_lines)

    with open(out_v1, "w", encoding="utf-8") as f:
        f.write(report_content)

    with open(out_repo, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Inventory scan complete. Total tool files: {len(tools_found)}. Saved report to:\n- {out_v1}\n- {out_repo}")

if __name__ == "__main__":
    run_tools_inventory()
