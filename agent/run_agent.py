import sys
import asyncio
sys.stdout.reconfigure(encoding='utf-8')
from agent import root_agent

async def process_evidence(document_text):
    print("========================================")
    print("INITIALIZING OSINTNeoAi DATA ENGINE...")
    print("========================================\n")
    
    # Construct the forensic prompt
    prompt = f"""
    [NEW EVIDENCE ACQUIRED]
    Please analyze the following contract data regarding Mercy House Living Shelters.
    Cross-reference this data against the California State Audit Report 2023-102.1 parameters 
    and identify any unaccounted fund deltas or architectural anomalies in the funding footprint.

    --- RAW EVIDENCE DATA ---
    {document_text}
    -------------------------
    
    Provide your forensic assessment below:
    """
    
    print(">> Feeding raw evidence into the analytical matrix...\n")
    try:
        from google.adk.runners import Runner
        from google.adk.sessions.in_memory_session_service import InMemorySessionService
        from google.genai import types
        
        runner = Runner(
            app_name="osint_agent",
            agent=root_agent,
            session_service=InMemorySessionService(),
            auto_create_session=True
        )
        
        new_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        async for event in runner.run_async(user_id="user1", session_id="sess1", new_message=new_msg):
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="")
            elif hasattr(event, 'output') and event.output:
                print(event.output, end="")
        
        print("\n========================================")
        print("FORENSIC ANALYSIS COMPLETE")
        print("========================================\n")
            
    except Exception as e:
        print(f"\n[!] Error running agent: {e}")

if __name__ == "__main__":
    # If the user passed a filename as an argument, read it
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                evidence = f.read()
        except FileNotFoundError:
            print(f"[!] Error: Could not find file '{file_path}'")
            sys.exit(1)
    else:
        # Default placeholder data if no file is provided
        evidence = (
            "Document: Mercy House Living Shelters - 2022-07-01 (4)\n"
            "Award Date: 7/1/2022\n"
            "Category Description: Federal Agreements\n"
            "Category ID: 600.15\n"
            "Contract Date: 7/1/2022\n"
            "Pages: 48\n"
            "(Pending full document OCR/text extraction from the Huntington Beach WebLink portal...)"
        )

    # Run the async loop
    asyncio.run(process_evidence(evidence))
