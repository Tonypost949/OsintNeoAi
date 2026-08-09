"""
HTML report generator for Sentinel investigations.
Produces standalone HTML files with embedded charts and search.
"""

import json
import os
from datetime import datetime


class HTMLReportGenerator:
    """Generate self-contained HTML investigation reports."""

    TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a0f; color: #e0e0e0; line-height: 1.6; }}
.header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 2rem; border-bottom: 2px solid #0f3460; }}
.header h1 {{ color: #00d4ff; font-size: 1.8rem; }}
.header .meta {{ color: #888; margin-top: 0.5rem; font-size: 0.9rem; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 1rem; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0; }}
.stat-card {{ background: #111; border: 1px solid #333; border-radius: 8px; padding: 1rem; text-align: center; }}
.stat-card .value {{ font-size: 2rem; color: #00d4ff; font-weight: bold; }}
.stat-card .label {{ color: #888; font-size: 0.85rem; margin-top: 0.25rem; }}
.section {{ background: #111; border: 1px solid #333; border-radius: 8px; margin: 1rem 0; padding: 1.5rem; }}
.section h2 {{ color: #00d4ff; margin-bottom: 1rem; font-size: 1.3rem; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid #222; }}
th {{ background: #1a1a2e; color: #00d4ff; }}
tr:hover {{ background: #1a1a2e; }}
.risk-high {{ color: #ff4444; font-weight: bold; }}
.risk-medium {{ color: #ffaa00; }}
.risk-low {{ color: #44ff44; }}
.search {{ width: 100%; padding: 0.8rem; background: #1a1a2e; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 1rem; margin: 1rem 0; }}
.search:focus {{ outline: none; border-color: #00d4ff; }}
.tag {{ display: inline-block; background: #0f3460; color: #00d4ff; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin: 0.1rem; }}
.hidden {{ display: none; }}
footer {{ text-align: center; padding: 2rem; color: #555; font-size: 0.8rem; }}
</style>
</head>
<body>
<div class="header">
    <h1>{title}</h1>
    <div class="meta">Generated: {timestamp} | Sentinel OSINT Engine v1.0</div>
</div>
<div class="container">
    <input type="text" class="search" placeholder="Search entities, relationships..." oninput="filterAll(this.value)">
    {content}
</div>
<footer>Sentinel OSINT Engine - Independent Edition | {timestamp}</footer>
<script>
function filterAll(q) {{
    q = q.toLowerCase();
    document.querySelectorAll('tr[data-search], .entity-row[data-search]').forEach(el => {{
        el.style.display = el.dataset.search.toLowerCase().includes(q) ? '' : 'none';
    }});
}}
</script>
</body>
</html>"""

    def __init__(self):
        self.sections = []

    def add_stats(self, stats: dict):
        cards = ""
        items = [
            (stats.get("total_entities", 0), "Entities"),
            (stats.get("total_relationships", 0), "Relationships"),
            (stats.get("clusters", 0), "Clusters"),
            (stats.get("risk_level", "N/A"), "Risk Level"),
        ]
        for value, label in items:
            cards += f'<div class="stat-card"><div class="value">{value}</div><div class="label">{label}</div></div>\n'
        self.sections.append(f'<div class="stats">{cards}</div>')

    def add_entity_table(self, entities: list[dict]):
        if not entities:
            return
        rows = ""
        for e in entities:
            risk_class = ""
            if e.get("confidence", 0) > 0.8:
                risk_class = "risk-high"
            elif e.get("confidence", 0) > 0.5:
                risk_class = "risk-medium"
            tags = " ".join(f'<span class="tag">{t}</span>' for t in e.get("tags", []))
            search_text = f"{e.get('type', '')} {e.get('value', '')} {e.get('source', '')}"
            rows += f'''<tr class="entity-row" data-search="{search_text}">
                <td>{e.get("type", "")}</td>
                <td>{e.get("value", "")}</td>
                <td class="{risk_class}">{e.get("confidence", 0):.0%}</td>
                <td>{e.get("source", "")}</td>
                <td>{tags}</td></tr>\n'''
        self.sections.append(f'''<div class="section"><h2>Entities</h2>
<table><thead><tr><th>Type</th><th>Value</th><th>Confidence</th><th>Source</th><th>Tags</th></tr></thead>
<tbody>{rows}</tbody></table></div>''')

    def add_relationship_table(self, relationships: list[dict], entity_map: dict = None):
        if not relationships:
            return
        rows = ""
        for r in relationships:
            src = entity_map.get(r.get("source", ""), r.get("source", "")) if entity_map else r.get("source", "")
            tgt = entity_map.get(r.get("target", ""), r.get("target", "")) if entity_map else r.get("target", "")
            search_text = f"{src} {tgt} {r.get('type', '')}"
            rows += f'''<tr data-search="{search_text}">
                <td>{src}</td><td>{r.get("type", "")}</td><td>{tgt}</td><td>{r.get("weight", 1)}</td></tr>\n'''
        self.sections.append(f'''<div class="section"><h2>Relationships</h2>
<table><thead><tr><th>Source</th><th>Type</th><th>Target</th><th>Weight</th></tr></thead>
<tbody>{rows}</tbody></table></div>''')

    def add_risk_findings(self, risk_data: dict):
        if not risk_data:
            return
        level = risk_data.get("risk_level", "UNKNOWN")
        score = risk_data.get("risk_score", 0)
        risk_class = "risk-high" if level in ("CRITICAL", "HIGH") else "risk-medium" if level == "MEDIUM" else "risk-low"
        html = f'<div class="section"><h2>Risk Assessment</h2>'
        html += f'<p class="{risk_class}" style="font-size:1.5rem;margin-bottom:1rem;">{level} ({score:.1f}/10)</p>'
        for level_name in ["high", "medium", "low"]:
            findings = risk_data.get("findings", {}).get(level_name, [])
            if findings:
                html += f'<h3 style="color:{"#ff4444" if level_name == "high" else "#ffaa00" if level_name == "medium" else "#44ff44"}">{level_name.upper()} Indicators</h3><ul>'
                for f in findings:
                    html += f'<li><code>{f["keyword"]}</code> - found {f["count"]} time(s)</li>'
                html += '</ul>'
        patterns = risk_data.get("findings", {}).get("pattern_matches", [])
        if patterns:
            html += '<h3>Pattern Matches</h3><ul>'
            for p in patterns:
                html += f'<li><strong>{p["pattern"]}</strong>: {", ".join(p["indicators"])}</li>'
            html += '</ul>'
        html += '</div>'
        self.sections.append(html)

    def add_custom_section(self, title: str, content: str):
        self.sections.append(f'<div class="section"><h2>{title}</h2>{content}</div>')

    def generate(self, title: str = "Sentinel Investigation Report") -> str:
        content = "\n".join(self.sections)
        return self.TEMPLATE.format(
            title=title,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            content=content,
        )

    def save(self, filepath: str, title: str = "Sentinel Investigation Report"):
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.generate(title))
        return filepath
