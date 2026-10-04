import os
import json
from autogen import AssistantAgent, UserProxyAgent
from ag2_config import llm_config

WORKSPACE = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"

osint_agent = AssistantAgent(
    name="OSINT_Compiler",
    system_message="""You are an elite OSINT forensic analyst. You have code execution access.
    Use it to read CSV files, parse data, extract entities, build knowledge graphs, and generate correlation maps.
    You output structured JSON for nodes and edges.
    Entity types: PERSON, ORGANIZATION, PROPERTY, ADDRESS, PHONE, EMAIL, VEHICLE, FINANCIAL_ACCOUNT.
    Relationship types: OWNS, LOCATED_IN, OFFICER_OF, DIRECTOR_OF, RECEIVED_PPP, LITIGANT_IN, REPRESENTED_BY, CONNECTED_TO.
    When asked to read files, use code_execution to open and parse them.""",
    llm_config=llm_config,
    human_input_mode="NEVER",
    code_execution_config={"work_dir": WORKSPACE, "use_docker": False}
)

user_proxy = UserProxyAgent(
    name="Admin",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": WORKSPACE, "use_docker": False}
)

def load_existing_graph():
    nodes_path = os.path.join(WORKSPACE, "nodes.json")
    edges_path = os.path.join(WORKSPACE, "edges.json")
    nodes = []
    edges = []
    if os.path.exists(nodes_path):
        with open(nodes_path, "r", encoding="utf-8") as f:
            nodes = json.load(f)
    if os.path.exists(edges_path):
        with open(edges_path, "r", encoding="utf-8") as f:
            edges = json.load(f)
    return nodes, edges

nodes, edges = load_existing_graph()
print(f"Loaded {len(nodes)} nodes, {len(edges)} edges")

INITIAL_PROMPT = f"""MISSION: GRAPH COMPLETENESS AUTOPILOT

STOP BUILDING NEW FRAMEWORKS.
STOP BUILDING NEW AGENTS.
STOP BUILDING NEW REPOSITORIES.
STOP BUILDING DASHBOARDS.

The graph exists.
The problem is missing relationships.

OBJECTIVE:
Fill the graph until every possible entity contains:
- officers
- managers
- members
- registered agents
- addresses
- state links
- property links
- PPP links
- CoC links
- nonprofit links

PHASE 1
Audit current graph.
Analyze: nodes.json, edges.json
Generate: graph_gap_report.json
Report:
- organizations missing officers
- organizations missing managers
- organizations missing registered agents
- organizations missing addresses
- organizations missing state links
- organizations missing property links
- organizations missing PPP links
Rank largest gaps first.

PHASE 2
Prioritize enrichment targets.
Priority:
1. CoC organizations
2. Nonprofits
3. PPP recipients
4. Property owners
5. LLC clusters
6. Shared-address clusters
Return counts for each category.

PHASE 3
Find and ingest missing people.
Create PERSON nodes for:
- officers
- managers
- members
- registered agents
- trustees
Create relationships:
- OFFICER_OF
- MANAGER_OF
- MEMBER_OF
- REGISTERED_AGENT_FOR
- TRUSTEE_OF
Do not create placeholder people.
Do not create synthetic names.
Only use actual recorded names.

PHASE 4
Find control clusters.
Definition: A control cluster exists when:
- same person controls multiple entities OR
- same registered agent controls multiple entities OR
- same manager controls multiple entities OR
- same member controls multiple entities
Output: control_clusters.json
Include: cluster id, entities, people, addresses, properties, PPP amounts

PHASE 5
Rank findings.
Produce: top_100_control_clusters.json
For each cluster include: entity count, person count, property count, PPP amount, address count, network score

PHASE 6
Generate completion report.
Output: graph_gap_report.json, control_clusters.json, top_100_control_clusters.json
Show: nodes added, edges added, remaining graph gaps

CRITICAL RULES
1. Use existing datasets first.
2. Use existing repositories first.
3. Do not create sample data.
4. Do not create placeholder data.
5. Do not create fake people.
6. Do not auto-approve changes.
7. Show findings before major modifications.

MISSION SUCCESS:
The graph becomes more complete.
The graph contains more real people.
The graph contains more real relationships.
The graph identifies real control clusters.
Reply TERMINATE when complete."""

user_proxy.initiate_chat(osint_agent, message=INITIAL_PROMPT)
