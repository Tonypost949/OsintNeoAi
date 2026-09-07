import os
from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import Optional, List
from google import genai
from core.AG2OSINTNEOMAXX.ai_worker_router import AIWorkerRouter

router = APIRouter(prefix="/api/workspace", tags=["WorkspaceChat"])

# Initialize the routers and clients globally using server-side auto-credentials
ai_router = AIWorkerRouter(project_id=os.getenv("GCP_PROJECT_ID", "default-project"))
gemini_client = genai.Client() # Automatically picks up GCP credentials

@router.post("/chat")
async def chat_interaction(
    wallet_address: str = Form(...),
    message: Optional[str] = Form(None),
    files: List[UploadFile] = File(None)
):
    """
    Handles the wide-open AI chat and multimodal ingestion.
    Files are ripped out and sent to the heavy background queue, 
    while text is sent to the wide-open chat model.
    """
    response_data = {}

    # 1. Handle File/Image/Audio Ingestion via Micro-Workers [TASK-082]
    if files:
        for file in files:
            file_bytes = await file.read()
            # Decode if text/pdf, or pass raw bytes to Vision/Audio models
            try:
                full_text = file_bytes.decode('utf-8') 
            except UnicodeDecodeError:
                full_text = "[Binary Media Payload - Requires OCR/Vision Processing]"

            # Route to the background ledger ingestion we built previously
            ingest_result = ai_router.route_incoming_document(
                file_bytes=file_bytes,
                full_text=full_text,
                miner_signature=wallet_address
            )
            response_data["ingestion"] = ingest_result

    # 2. Handle Wide-Open Conversational AI
    if message:
        # This is a standard, ungrounded conversational prompt
        chat_response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message
        )
        response_data["chat_reply"] = chat_response.text
    
    # If a file was uploaded but no message was typed, provide a smart summary
    elif files and "ingestion" in response_data:
        title = response_data["ingestion"].get("title", "Evidence")
        response_data["chat_reply"] = f"I have received your file '{title}'. It has been securely hashed and routed to the background queue for deep entity extraction."

    return response_data
