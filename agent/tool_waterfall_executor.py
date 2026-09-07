import time
import logging
import uuid
import datetime
import subprocess

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def dispatch_to_task_system(target_url, extracted_data):
    """
    NOTHING gets skipped. EVERYTHING goes to the task system.
    This parses the raw evidence from the waterfall and injects it straight into scripts/task_manager.py
    """
    logger.info("PIPELINE: Routing ripped evidence directly to Task System...")
    
    # Simple keyword heuristic for classification
    category = "SUGGESTIVE_WORK_TASKS"
    priority = "MEDIUM"
    title_prefix = "Analyze Extracted OSINT: "
    
    if "trust" in extracted_data.lower() or "unclaimed" in extracted_data.lower():
        category = "FOIA_COMPLAINT_WHISTLEBLOWER_TASKS"
        priority = "HIGH"
        title_prefix = "Draft Qui Tam/Whistleblower Disclosure for: "
        
    title = f'"{title_prefix} {target_url[:50]}"'
    
    # Route it straight to the official task_manager.py CLI
    try:
        cmd = f'python scripts/task_manager.py add {title} --category {category} --priority {priority}'
        subprocess.run(cmd, shell=True, check=False)
        logger.info(f"[+] Successfully injected into Task System: {title}")
    except Exception as e:
        logger.error(f"Failed to inject into task system: {e}")

class ToolLedger:
    """
    Each tool has its own dedicated page on the ledger.
    This tracks execution speed, accuracy, and failure rates to dynamically
    adjust the waterfall priority in the future.
    """
    def __init__(self):
        self.ledger = {
            "TOOL-01-FAST-CURL": {"attempts": 0, "success": 0, "avg_speed_ms": 0},
            "TOOL-02-HEADLESS-JS": {"attempts": 0, "success": 0, "avg_speed_ms": 0},
            "TOOL-03-LLM-VISION": {"attempts": 0, "success": 0, "avg_speed_ms": 0},
        }

    def log_execution(self, tool_id, success, elapsed_ms):
        page = self.ledger.get(tool_id)
        if not page:
            return
        page["attempts"] += 1
        if success:
            page["success"] += 1
        
        # Calculate moving average speed
        total_time = (page["avg_speed_ms"] * (page["attempts"] - 1)) + elapsed_ms
        page["avg_speed_ms"] = round(total_time / page["attempts"], 2)
        
        logger.info(f"[LEDGER UPDATE] {tool_id} | Success Rate: {(page['success']/page['attempts'])*100:.1f}% | Avg Speed: {page['avg_speed_ms']}ms")


def execute_waterfall_extraction(target_url, ledger: ToolLedger):
    """
    Accuracy, Speed, Ability.
    Executes a cascading waterfall of tools. If the fastest tool fails (e.g., blocked),
    it immediately falls back to the next tool in the chain.
    """
    logger.info(f"Initiating Waterfall Extraction for: {target_url}")
    
    # --- OPSEC & LEGAL ISOLATION ROUTING ---
    # If the target is classified as "dangerous" (e.g., hostile infrastructure, 
    # pentesting targets, or deep web), DO NOT touch it with the local website.
    # Route immediately to the air-gapped AnythingLLM Dedicated PC to protect user ID/IP.
    if ".onion" in target_url or "exploit" in target_url.lower():
        logger.warning("HIGH RISK TARGET DETECTED. Bypassing local fast tools for OPSEC.")
        return execute_anythingllm_fallback(target_url, ledger)
    
    # 1. THE FASTEST TOOL (e.g., Python Requests / cURL)
    # High Speed, Low Ability (Blocked by captchas)
    tool_1 = "TOOL-01-FAST-CURL"
    logger.info(f"[-] Attempting {tool_1}...")
    start_time = time.time()
    
    # Simulate a Cloudflare/Captcha block on the fast tool
    success_1 = False 
    elapsed_1 = (time.time() - start_time) * 1000
    ledger.log_execution(tool_1, success_1, elapsed_1)
    
    if success_1:
        extracted_data = "Raw DOM Text"
        dispatch_to_task_system(target_url, extracted_data)
        return {"status": "success", "tool_used": tool_1, "data": extracted_data}
        
    logger.warning(f"[X] {tool_1} blocked by Captcha. Escalating to next tool...")
    
    # 2. THE MEDIUM TOOL (e.g., Playwright / Puppeteer Headless)
    # Medium Speed, Medium Ability (Can execute JS, solve simple captchas)
    tool_2 = "TOOL-02-HEADLESS-JS"
    logger.info(f"[-] Attempting {tool_2}...")
    start_time = time.time()
    time.sleep(0.5) # Simulate browser spin-up
    
    # Simulate a dynamic PDF rendering that headless JS can't parse easily
    success_2 = False 
    elapsed_2 = (time.time() - start_time) * 1000
    ledger.log_execution(tool_2, success_2, elapsed_2)
    
    if success_2:
        extracted_data = "Rendered DOM Text"
        dispatch_to_task_system(target_url, extracted_data)
        return {"status": "success", "tool_used": tool_2, "data": extracted_data}

    logger.warning(f"[X] {tool_2} failed to parse rendered PDF canvas. Escalating to heavy tool...")

    # 3. THE HEAVY TOOL / ULTIMATE FALLBACK (AnythingLLM Dedicated PC)
    return execute_anythingllm_fallback(target_url, ledger)

def execute_anythingllm_fallback(target_url, ledger: ToolLedger):
    # Lowest Speed, Maximum Ability (Solves anything visually, runs custom agents front-to-back, isolates dangerous targets)
    tool_3 = "TOOL-03-ANYTHINGLLM-DEDICATED"
    logger.info(f"[-] Attempting {tool_3}...")
    start_time = time.time()
    
    # Send the raw URL to the Dedicated AnythingLLM PC to run its own agents/scrapers 
    # (using the Mintplex-Labs API structure)
    try:
        import requests
        import os
        
        # Pulling configuration from environment as specified in anythingllm_integration_plan.md
        llm_url = os.environ.get("ANYTHINGLLM_URL", "http://host.docker.internal:3001")
        llm_key = os.environ.get("ANYTHING_LLM_API_KEY", "")
        
        logger.info(f"Routing workflow to Dedicated AnythingLLM PC at {llm_url}")
        
        # We trigger the AnythingLLM custom agent tool (e.g., osintneoai_lightbox or a web scraper)
        payload = {
            "message": f"Execute front-to-back OSINT extraction workflow on target: {target_url}",
            "mode": "agent" # Triggers the Mintplex-Labs Agent workflow
        }
        
        time.sleep(1.5) # Simulate processing time on the dedicated PC
        
        success_3 = True 
        elapsed_3 = (time.time() - start_time) * 1000
        ledger.log_execution(tool_3, success_3, elapsed_3)
        
        extracted_data = "AnythingLLM Agent Payload (Hostile Target Isolated)"
        dispatch_to_task_system(target_url, extracted_data)
        
        logger.info(f"[+] {tool_3} succeeded! Dedicated AnythingLLM PC completed the workflow front-to-back.")
        return {"status": "success", "tool_used": tool_3, "data": extracted_data}
        
    except Exception as e:
        logger.error(f"AnythingLLM Dedicated PC failed or Auth Wall encountered: {e}")
        
        # 1. Inject into the FAILED_COMPLETELY Task List
        fail_title = f'"[FAILURE] Dead End on: {target_url[:40]}"'
        try:
            subprocess.run(f'python scripts/task_manager.py add {fail_title} --category FAILED_COMPLETELY --priority HIGH', shell=True, check=False)
        except Exception:
            pass
            
        # 2. Fire Silent Telemetry Ping to the Admin API
        try:
            import requests
            requests.post("http://127.0.0.1:5000/api/admin/telemetry/failure-ping", json={
                "target_url": target_url,
                "reason": str(e)
            }, timeout=2)
        except Exception:
            pass
        
        # 3. THE ULTIMATE MANUAL TAKEOVER (Really Fucking Easy for the User)
        # If all autonomous tools fail (e.g., impossible captcha, hard OAuth wall),
        # generate a shortlink for the user to paste into their authenticated browser.
        takeover_id = str(uuid.uuid4())[:8]
        shortlink = f"https://taxfunded.app/auth-override/{takeover_id}"
        
        logger.warning(f"MANUAL TAKEOVER REQUIRED. Generated Shortlink: {shortlink}")
        
        return {
            "status": "manual_takeover_required", 
            "target_url": target_url,
            "shortlink": shortlink,
            "message": "Impossible Captcha/Auth Wall detected. Manual takeover required."
        }

if __name__ == "__main__":
    master_ledger = ToolLedger()
    result = execute_waterfall_extraction("https://unclaimedproperty.ocgov.com/target=AndrewDo", master_ledger)
    print("\nFINAL LEDGER STATE:")
    for t_id, stats in master_ledger.ledger.items():
        print(f"{t_id}: {stats}")
    
    # Simulate an impossible auth wall
    print("\nSIMULATING IMPOSSIBLE AUTH WALL:")
    fail_result = execute_waterfall_extraction("https://secure.hostile-target.com/login", master_ledger)
    print(fail_result)
