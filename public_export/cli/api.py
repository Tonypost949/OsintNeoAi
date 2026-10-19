from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from core.entities import Entity, Domain, Email
from core.transforms import AVAILABLE_TRANSFORMS

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OSINTNeoAiCLI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated in-memory database of found entities
GLOBAL_GRAPH: List[Entity] = []

class InvestigateRequest(BaseModel):
    type: str
    value: str

class TransformRequest(BaseModel):
    transform_name: str
    target_type: str
    target_value: str

class LearnRequest(BaseModel):
    source: str

import json
import os

@app.get("/api/tools")
def get_tools():
    tools_path = "data/tools.json"
    if os.path.exists(tools_path):
        with open(tools_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tools": []}

@app.post("/api/learn")
def learn_material(req: LearnRequest):
    import requests
    import hashlib
    
    content = ""
    if req.source.startswith("http://") or req.source.startswith("https://"):
        try:
            response = requests.get(req.source)
            response.raise_for_status()
            content = response.text
            if "claude.ai/public/artifacts/" in req.source:
                import re
                import json
                pattern = re.compile(r"\{cat:'(.*?)',name:'(.*?)',desc:'(.*?)',url:'(.*?)',tags:\[(.*?)\](?:.*?)\}")
                matches = pattern.findall(content)
                if matches:
                    tools_file = "data/tools.json"
                    existing_tools = {"tools": []}
                    if os.path.exists(tools_file):
                        try:
                            with open(tools_file, "r", encoding="utf-8") as f:
                                existing_tools = json.load(f)
                        except Exception:
                            pass
                    
                    existing_names = {t.get("name", "").lower() for t in existing_tools.get("tools", [])}
                    added = 0
                    for m in matches:
                        name = m[1]
                        if name.lower() not in existing_names:
                            existing_tools["tools"].append({
                                "name": name,
                                "category": m[0],
                                "description": m[2].replace("\\'", "'"),
                                "url": m[3]
                            })
                            existing_names.add(name.lower())
                            added += 1
                    
                    if added > 0:
                        with open(tools_file, "w", encoding="utf-8") as f:
                            json.dump(existing_tools, f, indent=2)
                    content = f"Imported {len(matches)} OSINT tools from Claude Artifact: {req.source}"
            elif "text/html" in response.headers.get("Content-Type", ""):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(separator='\n', strip=True)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch from URL: {e}")
    else:
        if os.path.exists(req.source):
            try:
                with open(req.source, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
        else:
            raise HTTPException(status_code=400, detail="Source is not a valid URL or local file path")
            
    knowledge_dir = "data/knowledge"
    os.makedirs(knowledge_dir, exist_ok=True)
    
    source_hash = hashlib.md5(req.source.encode('utf-8')).hexdigest()[:8]
    filename = f"learned_{source_hash}.txt"
    filepath = os.path.join(knowledge_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Source: {req.source}\n")
        f.write("-" * 40 + "\n")
        f.write(content)
        
    return {"message": f"Successfully ingested knowledge from {req.source}", "filepath": filepath}

@app.post("/api/investigate", response_model=Entity)
def investigate(req: InvestigateRequest):
    entity = None
    if req.type.lower() == "domain":
        entity = Domain(value=req.value)
    elif req.type.lower() == "email":
        entity = Email(value=req.value)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: {req.type}")

    GLOBAL_GRAPH.append(entity)
    return entity

@app.post("/api/transform", response_model=List[Entity])
def run_transform(req: TransformRequest):
    t_name = req.transform_name.lower()
    if t_name not in AVAILABLE_TRANSFORMS:
        raise HTTPException(status_code=404, detail=f"Transform {req.transform_name} not found")

    transform = AVAILABLE_TRANSFORMS[t_name]
    
    if req.target_type.lower() == "domain":
        target_entity = Domain(value=req.target_value)
    elif req.target_type.lower() == "email":
        target_entity = Email(value=req.target_value)
    else:
        target_entity = Entity(type=req.target_type, value=req.target_value)

    results = transform.run(target_entity)
    
    for r in results:
        GLOBAL_GRAPH.append(r)
        
    return results

@app.get("/api/graph", response_model=List[Entity])
def get_graph():
    return GLOBAL_GRAPH
