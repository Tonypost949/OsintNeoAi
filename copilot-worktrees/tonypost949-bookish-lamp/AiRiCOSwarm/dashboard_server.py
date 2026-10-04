"""AiRiCOSwarm Cockpit API & Dashboard Server."""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from AiRiCOSwarm.swarm.orchestrator import ChiefInvestigatorAgent
from AiRiCOSwarm.main import DEFAULT_BATCH_TARGETS

app = FastAPI(title="AiRiCOSwarm Cockpit API", version="1.0.0")

orchestrator = ChiefInvestigatorAgent()
DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "dashboard")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

class RunRequest(BaseModel):
    target: str
    mode: Optional[str] = "cycle"

@app.get("/")
async def serve_index():
    index_path = os.path.join(DASHBOARD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "error", "message": "Dashboard UI not found."}

@app.post("/api/swarm/run")
async def run_cycle(req: RunRequest):
    try:
        result = orchestrator.run_investigation_cycle(req.target)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/swarm/batch")
async def run_batch():
    try:
        results = orchestrator.run_batch_sweep(DEFAULT_BATCH_TARGETS)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/swarm/reports")
async def list_reports():
    if not os.path.exists(REPORTS_DIR):
        return {"reports": []}
    files = []
    for f in os.listdir(REPORTS_DIR):
        if f.endswith(".md"):
            path = os.path.join(REPORTS_DIR, f)
            stat = os.stat(path)
            files.append({
                "filename": f,
                "size": stat.st_size,
                "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
    files.sort(key=lambda x: x["date"], reverse=True)
    return {"reports": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8050)
