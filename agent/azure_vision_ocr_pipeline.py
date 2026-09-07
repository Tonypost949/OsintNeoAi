import os
import json
import logging
import requests
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Azure Document Intelligence
AZURE_ENDPOINT = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "https://your-resource-name.cognitiveservices.azure.com/")
AZURE_KEY = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY", "your_azure_api_key_here")

# AnythingLLM (Running on the dedicated PC)
ANYTHINGLLM_URL = os.environ.get("ANYTHINGLLM_URL", "http://192.168.1.100:3001") # Replace with the actual IP
ANYTHINGLLM_API_KEY = os.environ.get("ANYTHINGLLM_API_KEY", "your_anythingllm_api_key")
WORKSPACE_SLUG = "osintneoai-forensics"

def extract_text_with_azure_ocr(pdf_url: str) -> str:
    """
    Uses Azure Document Intelligence to OCR complex municipal PDFs 
    (like the OC Health Industrial Cleanup PDFs).
    """
    logger.info(f"Initiating Azure OCR for PDF: {pdf_url}")
    try:
        client = DocumentIntelligenceClient(
            endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY)
        )
        
        # 'prebuilt-layout' extracts text, tables, and selection marks universally
        poller = client.begin_analyze_document(
            "prebuilt-layout", 
            analyze_request={"urlSource": pdf_url}
        )
        
        result: AnalyzeResult = poller.result()
        
        full_text = []
        for page in result.pages:
            for line in page.lines:
                full_text.append(line.content)
                
        # Also grab tables to maintain structure
        for table in result.tables:
            for cell in table.cells:
                full_text.append(f"[Table Data]: {cell.content}")
                
        final_text = "\n".join(full_text)
        logger.info(f"Azure OCR Complete. Extracted {len(final_text)} characters.")
        return final_text
        
    except Exception as e:
        logger.error(f"Azure OCR Pipeline Failed: {e}")
        return ""


def push_to_anythingllm(title: str, content: str):
    """
    Pushes the cleaned, OCR'd text directly into AnythingLLM's memory/workspace.
    """
    logger.info(f"Pushing evidence to AnythingLLM ({ANYTHINGLLM_URL}) for RAG vectorization...")
    
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # In AnythingLLM, we usually create a raw text document first, then update the workspace
    # 1. Add document to AnythingLLM storage
    doc_payload = {
        "textContent": content,
        "metadata": {
            "title": title,
            "source": "Azure OCR Pipeline"
        }
    }
    
    add_doc_endpoint = f"{ANYTHINGLLM_URL}/api/v1/document/add-text"
    try:
        response = requests.post(add_doc_endpoint, json=doc_payload, headers=headers)
        if response.status_code == 200:
            logger.info("Successfully vectorized and pushed to AnythingLLM!")
            return response.json()
        else:
            logger.error(f"AnythingLLM push failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Failed to connect to AnythingLLM backend PC: {e}")

if __name__ == "__main__":
    # Test Payload using the user's earlier evidence
    test_pdf_url = "https://www.ochealthinfo.com/sites/hca/files/2021-09/Industrial_Cleanup_Cases_by_City_9.8.21.pdf"
    
    logger.info("--- STARTING AZURE OCR -> ANYTHINGLLM PIPELINE ---")
    
    # 1. Rip the PDF with Azure OCR
    extracted_data = extract_text_with_azure_ocr(test_pdf_url)
    
    # 2. If successful, push straight into AnythingLLM on the dedicated PC
    if extracted_data:
        push_to_anythingllm(
            title="OC Health Industrial Cleanup Cases (Huntington Beach)", 
            content=extracted_data
        )
