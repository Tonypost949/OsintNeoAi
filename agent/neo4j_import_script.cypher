// Cypher Import Scripts for Fraud Intelligence Graph
// Place the exported CSVs (neo4j_nodes_org.csv, neo4j_edges_indicator.csv, neo4j_edges_high_risk.csv) 
// into your Neo4j import directory, or reference them via an accessible URL.

// 1. Load Organization Nodes
LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes_org.csv' AS row
MERGE (o:Organization {id: row.id})
SET o.name = row.name, o.label = row.label;

// 2. Load Indicators and HAS_INDICATOR Edges
LOAD CSV WITH HEADERS FROM 'file:///neo4j_edges_indicator.csv' AS row
MATCH (o:Organization {id: row.source})
MERGE (i:Indicator {name: row.target})
MERGE (o)-[:HAS_INDICATOR]->(i);

// 3. Load High Risk Fraud Scores and HIGH_RISK Edges
LOAD CSV WITH HEADERS FROM 'file:///neo4j_edges_high_risk.csv' AS row
MATCH (o:Organization {id: row.source}) // Note: source here is transaction_id linked to the org
// For simplicity assuming the source points back to the org node, if not we need an intermediate node or direct match on fact table
MERGE (r:RiskLevel {name: row.target})
MERGE (o)-[:FLAGGED_AS {fraud_distance: toFloat(row.fraud_distance)}]->(r);

// --- Advanced Graph Analytics Queries ---

// A. Force-Directed Network Graph: Reveal Hidden Clusters
// Visual Encoding recommendation: Node size by betweenness centrality
MATCH path = (o:Organization)-[:HAS_INDICATOR]->(i:Indicator)
RETURN path LIMIT 100;

// B. Find Central Entities (Degree Centrality)
MATCH (o:Organization)-[r]-()
RETURN o.name, count(r) AS degree
ORDER BY degree DESC
LIMIT 10;

// C. Find Offshore Sink Nodes
MATCH (o:Organization)-[:HAS_INDICATOR]->(i:Indicator)
WHERE i.name IN ['international', 'overseas', 'philippines', 'manila']
RETURN o, i;

// D. Detect Circular Flow or Synthetic Remittance Loops
// (Requires transaction edges imported separately from fact_transactions)
MATCH path=(a:Organization)-[:TRANSFERS_TO*2..5]->(a)
RETURN path LIMIT 5;
