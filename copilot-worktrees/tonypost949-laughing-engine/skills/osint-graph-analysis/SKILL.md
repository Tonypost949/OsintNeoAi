# OSINT Graph Analysis

This skill helps with intelligence network analysis using graph structures, link visualization, and path discovery. It is tailored for OSINT workflows that analyze relationships between people, organizations, events, and digital artifacts.

## When to use this skill

- You need to analyze or visualize connection graphs from OSINT data.
- You want to derive insights from network structure, clustering, or link strength.
- You are working with graph UI scripts or generating nodes/edges for visualization.
- You want to enrich the analysis with inferred links or entity resolution.

## Key workflow

1. Gather graph data sources.
   - Identify structured CSV/JSON outputs with entities and relationships.
   - Use `inferred_links.csv`, `public_records.csv`, `fraud_alerts.csv`, or similar datasets.
2. Construct node and edge models.
   - Define node types: person, organization, document, location, incident.
   - Define edge properties: relationship type, evidence count, confidence.
3. Analyze graph properties.
   - Find clusters, central nodes, and paths.
   - Use metrics like degree, betweenness, and connected components.
4. Visualize and interpret.
   - Use existing dashboard pages like `graph_ui.html` or `graph_view.html`.
   - Highlight suspicious hubs, recurring patterns, and bridging entities.
5. Iterate with new data.
   - Add inferred links from heuristics or AI enrichment.
   - Refresh visualizations and summaries.

## Recommended techniques and tools

- `networkx` for graph analytics in Python
- `pyvis` or `D3.js` for interactive visualization
- `neo4j` / graph databases for advanced queries
- `pandas` for graph table preparation
- `matplotlib` / `plotly` for visual analytics

## Practical OSINT examples

- Build a graph from contact lists, company ownership, and event affiliations.
- Detect community structure in fraud or corruption networks.
- Trace data flows between cloud assets, emails, and leaked documents.
- Use inferred links to surface hidden intermediaries or repeated patterns.

## Quality criteria

- Keep edges weighted and typed to preserve evidence strength.
- Validate graph connectivity and avoid duplicate nodes.
- Use visual annotations for confidence and source provenance.
- Prefer interactive analysis when exploring complex networks.

## Prompt examples

- "Generate a Python graph analysis workflow for OSINT entity link analysis."
- "How do I visualize a fraud network using NetworkX and PyVis?"
- "Suggest a method to infer hidden relationships in my intelligence graph."
- "Help me improve my existing `graph_ui.html` dashboard for link analysis."
