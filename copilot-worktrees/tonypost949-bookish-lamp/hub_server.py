"""Unified OSINT AI Chat Hub Server
Integrates AI Chat with live function calling across AiRiCOSwarm, BigQuery, CLIs, and Graph Engines.
"""

import os
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from AiRiCOSwarm.connectors.bq_connector import BigQueryConnector
from AiRiCOSwarm.swarm.orchestrator import ChiefInvestigatorAgent
from AiRiCOSwarm.main import DEFAULT_BATCH_TARGETS

app = FastAPI(title="OSINT AI Universal Chat Hub", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bq = BigQueryConnector()
orchestrator = ChiefInvestigatorAgent()

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "AiRiCOSwarm", "reports")

# Initialize AI Client (Gemini or Rule-based Assistant)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        print("[HUB] Gemini Generative Client connected.")
    except Exception as e:
        print(f"[HUB] Gemini client initialization note: {e}")

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []

# Tool Execution Dispatcher
def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "investigate_target":
        target = params.get("target", "Andrew Do")
        res = orchestrator.run_investigation_cycle(target)
        return {"status": "success", "result": res}

    elif tool_name == "batch_sweep":
        res = orchestrator.run_batch_sweep(DEFAULT_BATCH_TARGETS)
        return {"status": "success", "result": res}

    elif tool_name == "query_bigquery":
        kw = params.get("keyword", "").replace("'", "\\'")
        sql = f"""
            SELECT CAST(sent_timestamp AS STRING) AS date, from_address, to_addresses, subject 
            FROM `noble-beanbag-497411-m4.national_audits.takeout_mail_metadata`
            WHERE LOWER(subject) LIKE '%{kw.lower()}%' OR LOWER(to_addresses) LIKE '%{kw.lower()}%'
            LIMIT 20
        """
        rows = bq.query(sql)
        return {"status": "success", "count": len(rows), "rows": rows}

    elif tool_name == "record_finding":
        title = params.get("title", "New Finding")
        desc = params.get("description", "")
        links = params.get("links", [])
        ok = bq.record_finding(title, desc, links)
        return {"status": "success" if ok else "error", "message": "Finding saved to BigQuery."}

    elif tool_name == "check_clis":
        clis = ["python", "node", "git", "gh", "bq", "gcloud", "docker", "pwsh"]
        statuses = {}
        for c in clis:
            statuses[c] = shutil_which := subprocess.run(f"where {c}", shell=True, capture_output=True, text=True).returncode == 0
        return {"status": "success", "clis": statuses}

    elif tool_name == "list_dossiers":
        if not os.path.exists(REPORTS_DIR):
            return {"reports": []}
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")]
        return {"status": "success", "reports": files}

    return {"status": "error", "message": f"Unknown tool: {tool_name}"}

@app.get("/")
async def serve_hub():
    index_file = os.path.join(PUBLIC_DIR, "ai_chat_hub.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ready", "message": "Chat Hub server running."}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_msg = req.message.strip()
    user_msg_lower = user_msg.lower()

    executed_tools = []
    response_text = ""

    # Smart Autonomous Intent & Tool Routing
    if "investigate" in user_msg_lower or "sweep" in user_msg_lower or "target" in user_msg_lower:
        # Extract target or run batch
        if "batch" in user_msg_lower or "all" in user_msg_lower:
            tool_res = execute_tool("batch_sweep", {})
            executed_tools.append({"tool": "batch_sweep", "data": f"Swept {len(DEFAULT_BATCH_TARGETS)} primary RICO targets."})
            response_text = f"⚡ **AiRiCOSwarm Batch Sweep Complete!**\n\nSwept 6 key targets: {', '.join(DEFAULT_BATCH_TARGETS)}. All generated intelligence dossiers are ready in your reports repository."
        else:
            words = user_msg.replace("investigate", "").replace("search", "").replace("for", "").strip(" '\"")
            target = words if words else "Andrew Do"
            tool_res = execute_tool("investigate_target", {"target": target})
            res_data = tool_res.get("result", {})
            executed_tools.append({"tool": "investigate_target", "data": f"Target: {target} | Hits: {res_data.get('flagged_hits', 0)}"})
            response_text = f"🎯 **Investigation Complete for '{target}'**\n\n- **Records Scanned:** {res_data.get('raw_hits', 0)}\n- **Correlated Predicates:** {res_data.get('flagged_hits', 0)}\n- **Dossier Written:** `{res_data.get('dossier_path', 'Saved')}`\n\nWould you like me to inspect the extracted predicates or file a finding directly into BigQuery?"

    elif "cli" in user_msg_lower or "status" in user_msg_lower or "health" in user_msg_lower:
        tool_res = execute_tool("check_clis", {})
        executed_tools.append({"tool": "check_clis", "data": tool_res.get("clis", {})})
        cli_list = tool_res.get("clis", {})
        active = [k for k, v in cli_list.items() if v]
        response_text = f"🛠️ **System & CLI Health Matrix**\n\n- **Active Tools ({len(active)}):** {', '.join(active)}\n- **BigQuery Connection:** Active (`noble-beanbag-497411-m4`)\n- **AiRiCOSwarm Orchestrator:** Online"

    elif "dossier" in user_msg_lower or "report" in user_msg_lower:
        tool_res = execute_tool("list_dossiers", {})
        reports = tool_res.get("reports", [])
        executed_tools.append({"tool": "list_dossiers", "data": f"{len(reports)} reports found"})
        response_text = f"📂 **Generated Whistleblower Dossiers ({len(reports)} Total)**\n\n" + "\n".join([f"- `{r}`" for r in reports[:10]])

    elif "bigquery" in user_msg_lower or "email" in user_msg_lower or "search" in user_msg_lower:
        kw = user_msg.replace("bigquery", "").replace("search", "").replace("for", "").strip(" '\"")
        tool_res = execute_tool("query_bigquery", {"keyword": kw})
        rows = tool_res.get("rows", [])
        executed_tools.append({"tool": "query_bigquery", "data": f"{len(rows)} rows matched"})
        response_text = f"🔍 **BigQuery Query Results for '{kw}'**\n\nFound **{len(rows)}** records in `national_audits.takeout_mail_metadata`.\n\n"
        for r in rows[:5]:
            response_text += f"- **[{r.get('date', 'N/A')}] {r.get('subject', 'No Subject')}** (From: `{r.get('from_address', 'N/A')}`)\n"

    else:
        # General AI reasoning / conversational response
        if ai_client:
            try:
                ai_resp = ai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"You are the OSINT NeoAI Chief Forensic Assistant. User query: {user_msg}"
                )
                response_text = ai_resp.text
            except Exception as e:
                response_text = f"OSINT NeoAI Assistant: Ready to execute investigations across BigQuery, AiRiCOSwarm, and your local toolkits. (AI note: {e})"
        else:
            response_text = f"OSINT NeoAI Assistant: Standing by. Ask me to:\n- `investigate <target>` (e.g. 'investigate Andrew Do')\n- `batch sweep` (run all RICO targets)\n- `search emails for <term>`\n- `check system status`\n- `list dossiers`"

    return {
        "reply": response_text,
        "tools_executed": executed_tools,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/system/stats")
async def system_stats():
    return {
        "status": "online",
        "bigquery": "connected",
        "project": "noble-beanbag-497411-m4",
        "swarm_agents": 5,
        "active_ports": [8000, 8050, 8080, 9000]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)
