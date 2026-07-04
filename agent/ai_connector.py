from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery
from google.cloud import storage
from google.oauth2.credentials import Credentials
from google import genai
import os

app = FastAPI(
    title="OSINT Evidence Copilot API",
    description="Connects local Copilots and Open WebUI to the OSINT BigQuery Database and GCS Vault.",
    version="2.0.0"
)

# Load OAuth Credentials (assuming token.json is in the same dir)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.json')
if not os.path.exists(TOKEN_PATH):
    raise RuntimeError("token.json not found! Please run the scan scripts to authenticate first.")

creds = Credentials.from_authorized_user_file(TOKEN_PATH)
bq_client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
gcs_client = storage.Client(project="project-743aab84-f9a5-4ec7-954")

# Initialize Gemini AI Studio client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not set. /api/analyze will be unavailable.")
    ai_client = None
else:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
    print("AI Studio client initialized (gemini-2.5-flash)")

class SearchRequest(BaseModel):
    search_term: str
    evidence_type: str = "gmail"  # 'gmail' or 'drive'

class FindingRequest(BaseModel):
    title: str
    description: str
    evidence_links: list[str] = []

class SyncCodeRequest(BaseModel):
    filename: str
    code_content: str
    language: str
    description: str

@app.post("/api/search")
async def search_evidence(request: SearchRequest):
    """Search across the OSINT evidence database."""
    term = request.search_term.replace("'", "\\'")
    
    if request.evidence_type == "gmail":
        query = f"""
            SELECT date, sender, subject, snippet 
            FROM `project-743aab84-f9a5-4ec7-954.national_audits.gmail_index`
            WHERE LOWER(subject) LIKE LOWER('%{term}%') 
               OR LOWER(snippet) LIKE LOWER('%{term}%')
            LIMIT 20
        """
    else:
        query = f"""
            SELECT name, mimeType, webViewLink, createdTime 
            FROM `project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index`
            WHERE LOWER(name) LIKE LOWER('%{term}%')
            LIMIT 20
        """

    try:
        query_job = bq_client.query(query)
        results = [dict(row) for row in query_job]
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/finding")
async def record_finding(request: FindingRequest):
    """Write a finding securely into the BigQuery AI Sandbox."""
    # Ensure the sandbox table exists
    table_id = "project-743aab84-f9a5-4ec7-954.ai_sandbox.findings"
    
    # Normally you'd define a schema and use insert_rows_json, but we'll do a simple insert via SQL
    links = ", ".join(request.evidence_links)
    query = f"""
        INSERT INTO `{table_id}` (title, description, evidence_links, timestamp)
        VALUES (
            '{request.title.replace("'", "\\'")}', 
            '{request.description.replace("'", "\\'")}', 
            '{links.replace("'", "\\'")}', 
            CURRENT_TIMESTAMP()
        )
    """
    try:
        # Check if table exists, create if not
        try:
            bq_client.get_table(table_id)
        except Exception:
            schema = [
                bigquery.SchemaField("title", "STRING"),
                bigquery.SchemaField("description", "STRING"),
                bigquery.SchemaField("evidence_links", "STRING"),
                bigquery.SchemaField("timestamp", "TIMESTAMP"),
            ]
            table = bigquery.Table(table_id, schema=schema)
            bq_client.create_table(table)
            
        bq_client.query(query).result()
        return {"status": "success", "message": "Finding saved to cloud Sandbox."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync_code")
async def sync_code(request: SyncCodeRequest):
    """Save AI generated code locally and upload to GCS."""
    sync_dir = os.path.join(os.path.dirname(__file__), 'ai_sync_vault')
    os.makedirs(sync_dir, exist_ok=True)
    
    local_path = os.path.join(sync_dir, request.filename)
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(request.code_content)
        
    try:
        bucket = gcs_client.bucket("osint-ai-evidence-vault-m4")
        blob = bucket.blob(f"ai_generated_code/{request.filename}")
        blob.upload_from_filename(local_path)
        
        # Log to BigQuery
        table_id = "project-743aab84-f9a5-4ec7-954.ai_sandbox.findings"
        link = f"gs://osint-ai-evidence-vault-m4/ai_generated_code/{request.filename}"
        query = f"""
            INSERT INTO `{table_id}` (title, description, evidence_links, timestamp)
            VALUES (
                'Synced Code: {request.filename.replace("'", "\\\\'")}', 
                '{request.description.replace("'", "\\\\'")}', 
                '{link.replace("'", "\\\\'")}', 
                CURRENT_TIMESTAMP()
            )
        """
        try:
            bq_client.get_table(table_id)
        except Exception:
            schema = [
                bigquery.SchemaField("title", "STRING"),
                bigquery.SchemaField("description", "STRING"),
                bigquery.SchemaField("evidence_links", "STRING"),
                bigquery.SchemaField("timestamp", "TIMESTAMP"),
            ]
            table = bigquery.Table(table_id, schema=schema)
            bq_client.create_table(table)

        bq_client.query(query).result()
        
        return {"status": "success", "message": f"Code synchronized to {link}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GisQueryRequest(BaseModel):
    layer_url: str
    where: str = "1=1"
    out_fields: str = "*"
    return_geometry: bool = True

@app.post("/api/gis/query")
async def query_gis(request: GisQueryRequest):
    """Proxy queries to Huntington Beach ArcGIS REST API."""
    import requests
    query_url = f"{request.layer_url}/query"
    params = {
        "where": request.where,
        "outFields": request.out_fields,
        "returnGeometry": "true" if request.return_geometry else "false",
        "f": "json"
    }
    
    try:
        res = requests.get(query_url, params=params)
        res.raise_for_status()
        data = res.json()
        
        # Log to BigQuery
        table_id = "project-743aab84-f9a5-4ec7-954.ai_sandbox.findings"
        feature_count = len(data.get("features", []))
        query = f"""
            INSERT INTO `{table_id}` (title, description, evidence_links, timestamp)
            VALUES (
                'GIS Spatial Query Execution', 
                'Queried Huntington Beach GIS: returned {feature_count} features. WHERE: {request.where.replace("'", "\\\\'")}', 
                '{query_url.replace("'", "\\\\'")}', 
                CURRENT_TIMESTAMP()
            )
        """
        try:
            bq_client.get_table(table_id)
            bq_client.query(query).result()
        except Exception:
            pass # Ignore log fail if table doesn't exist
            
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# AI LAYER — Gemini via AI Studio
# ============================================================

class AnalyzeRequest(BaseModel):
    query: str
    target_datasets: list[str] = []
    include_audit_text: bool = False

class CrossReferenceRequest(BaseModel):
    entity_a: str
    entity_b: str
    dataset_a: str = ""
    dataset_b: str = ""

SYSTEM_PROMPT = """You are an OSINT forensic analyst assisting with a RICO investigation into the Huntington Beach / Orange County homeless services fraud network.

Key investigation targets:
- Andrew Do (former OC Supervisor)
- Viet America Society (VAS)
- RPM Team / RPM Modular
- Mercy House Living Centers (CEO: Larry Haynes)
- City of Huntington Beach
- County of Orange
- Casa Aliento LP (bought Mercy House CHDO's Vagabond Inn for $15M)

You have access to structured evidence including:
- rico_evidence_matrix.csv (2,696 HB out-of-state LLCs cross-referenced with IRS 990, NV SOS, PPP loans)
- mercy_house_gsa_audit_2024.txt (44-page audited financials showing $74.2M revenue, $1.5M audit finding)
- master_index_v2.db (OSINT matrix with nodes, relationships, authority sources)
- BigQuery: national_audits.gmail_index (30,000 emails), ai_sandbox.findings

Always cite specific dollar amounts, EINs, dates, and document sources. Flag any FCA (False Claims Act), grant fraud, kickback, or RICO predicate act indicators."""

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """Send a natural language query to Gemini for RICO analysis."""
    if ai_client is None:
        raise HTTPException(status_code=503, detail="AI Studio client not initialized. Set GEMINI_API_KEY env var.")

    context_parts = [SYSTEM_PROMPT]

    # Optionally load audit text
    if request.include_audit_text:
        audit_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\mercy_house_gsa_audit_2024.txt"
        if os.path.exists(audit_path):
            with open(audit_path, "r", encoding="utf-8") as f:
                audit_text = f.read()[:120000]
            context_parts.append(f"\n=== MERCY HOUSE GSA AUDIT 2024 (partial) ===\n{audit_text}\n=== END AUDIT ===")

    # Search BigQuery datasets if requested
    for dataset in request.target_datasets:
        try:
            parts = dataset.split(".")
            if len(parts) == 2:
                table_ref = f"project-743aab84-f9a5-4ec7-954.{dataset}"
                sample_query = f"SELECT * FROM `{table_ref}` LIMIT 50"
                job = bq_client.query(sample_query)
                rows = [dict(row) for row in job.result()]
                if rows:
                    import json
                    context_parts.append(f"\n=== BigQuery: {dataset} (50 rows) ===\n{json.dumps(rows, default=str)[:80000]}\n=== END BQ ===")
        except Exception as e:
            context_parts.append(f"\nBigQuery {dataset}: unavailable ({e})")

    context_parts.append(f"\nUSER QUERY: {request.query}")
    full_prompt = "\n".join(context_parts)

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
        )
        return {
            "status": "success",
            "query": request.query,
            "analysis": response.text,
            "model": "gemini-2.5-flash"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Studio error: {e}")

@app.post("/api/cross_reference")
async def cross_reference(request: CrossReferenceRequest):
    """Cross-reference two entities using the RICO evidence matrix."""
    if ai_client is None:
        raise HTTPException(status_code=503, detail="AI Studio client not initialized.")

    import csv
    import json

    # Load the RICO evidence matrix
    rico_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\rico_evidence_matrix.csv"
    rico_context = ""
    if os.path.exists(rico_path):
        with open(rico_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Filter rows matching either entity
            matches = []
            for row in reader:
                row_text = json.dumps(row, default=str).lower()
                if request.entity_a.lower() in row_text or request.entity_b.lower() in row_text:
                    matches.append(row)
                if len(matches) >= 50:
                    break
            if matches:
                rico_context = json.dumps(matches, default=str)[:60000]

    prompt = f"""{SYSTEM_PROMPT}

Cross-reference two entities for RICO connections.

ENTITY A: {request.entity_a}
ENTITY B: {request.entity_b}

RICO EVIDENCE MATRIX (filtered):
{rico_context if rico_context else 'No direct matches found in rico_evidence_matrix.csv'}

Analyze:
1. Direct connections (shared addresses, officers, EINs, LLCs)
2. Funding overlaps (same grant programs, same funders)
3. Geographic proximity (same city, same APN area)
4. Timeline correlations (key dates)
5. RICO predicate indicators (wire fraud, mail fraud, money laundering, FCA violations)"""

    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return {"status": "success", "cross_reference": response.text, "model": "gemini-2.5-flash"}

class AskRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask(request: AskRequest):
    """Simple chat with Gemini, loaded with OSINT context. For general investigation questions."""
    if ai_client is None:
        raise HTTPException(status_code=503, detail="AI Studio client not initialized.")

    prompt = SYSTEM_PROMPT + "\n\nUSER: " + request.question
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return {"status": "success", "answer": response.text, "model": "gemini-2.5-flash"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
