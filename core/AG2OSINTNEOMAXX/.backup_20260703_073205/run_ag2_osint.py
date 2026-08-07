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

INITIAL_PROMPT = f"""PHASE 7 — PPP + PROPERTY DEEP TRACE

Focus only on the 32 organizations that:

1. Received PPP loans
2. Own property

For each organization return:

- Organization name
- PPP amount
- PPP forgiveness amount
- Property APN
- Property address
- Mailing address
- State associated with PPP loan
- Number of connected organizations sharing the mailing address

Calculate:

- Total PPP dollars across all 32 organizations
- Top 10 highest PPP recipients
- Top 10 addresses with the most PPP-linked organizations
- Top 10 mailing addresses acting as hub locations

Flag organizations where:

- PPP > $100,000
- Shared address with 5+ organizations
- Multiple properties linked
- Multiple PPP loans linked

Output:

HIGH
MEDIUM
LOW

network-interest score.

STOP AFTER REPORTING RESULTS.
DO NOT BUILD DASHBOARDS.
DO NOT BUILD VISUALIZATIONS.
DO NOT CREATE NEW AGENTS.
Reply TERMINATE when complete."""

user_proxy.initiate_chat(osint_agent, message=INITIAL_PROMPT)
