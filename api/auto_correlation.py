"""
api/auto_correlation.py
=======================
Azure App Service in-process Auto-Correlation Orchestrator
- Exposes run_leads_correlation() callable for HTTP triggers
- Provides start_background_scheduler() for 24/7 autonomous cloud loops
- Safe: catches all exceptions, logs to stdout (visible in az webapp log tail)

Env:
  ENABLE_AUTO_CORRELATION=1   -> auto-start background thread on import
  AUTO_CORRELATION_INTERVAL=7200  -> seconds between runs (default 2h)
"""
import os
import sys
import threading
import time
import traceback
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_PATH = REPO_ROOT / "scripts" / "auto_leads_correlation_v2.py"

_last_run = {"at": None, "leads": 0, "elapsed": 0, "error": None, "summary": {}}
_lock = threading.Lock()
_thread = None
_stop_event = threading.Event()

def _log(msg):
    print(f"[AUTO_CORRELATION] {datetime.now(timezone.utc).isoformat()} {msg}", flush=True)

def run_leads_correlation():
    """Synchronous single correlation run. Returns payload dict."""
    global _last_run
    try:
        # Import and run engine directly (avoid subprocess for App Service sandbox)
        import importlib.util
        spec = importlib.util.spec_from_file_location("auto_leads_correlation_v2", str(SCRIPTS_PATH))
        mod = importlib.util.module_from_spec(spec)
        # Ensure repo root on sys.path for any relative imports
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        spec.loader.exec_module(mod)
        payload = mod.run_correlation()
        with _lock:
            _last_run = {
                "at": datetime.now(timezone.utc).isoformat(),
                "leads": len(payload.get("leads", [])),
                "elapsed": payload.get("summary", {}).get("elapsed", 0),
                "error": None,
                "summary": payload.get("summary", {}),
                "graph_stats": payload.get("graph_stats", {})
            }
        return payload
    except Exception as e:
        err = f"{e}\n{traceback.format_exc()}"
        _log(f"ERROR run: {err}")
        with _lock:
            _last_run = {"at": datetime.now(timezone.utc).isoformat(), "leads": 0, "elapsed": 0, "error": str(e), "summary": {}}
        return {"error": str(e), "trace": err, "leads": [], "summary": {}}

def get_last_run():
    with _lock:
        return dict(_last_run)

def _loop(interval):
    _log(f"Background scheduler started interval={interval}s")
    # Stagger first run by 30s to let Flask boot
    time.sleep(30)
    while not _stop_event.is_set():
        _log("Scheduler tick -> running correlation")
        try:
            run_leads_correlation()
        except Exception as e:
            _log(f"Scheduler run failed: {e}")
        # Wait with interruptible sleep
        _stop_event.wait(interval)
    _log("Background scheduler stopped")

def start_background_scheduler(interval=None):
    global _thread
    if _thread and _thread.is_alive():
        _log("Scheduler already running")
        return False
    try:
        iv = int(interval or os.getenv("AUTO_CORRELATION_INTERVAL", "7200"))
    except Exception:
        iv = 7200
    # Clamp to minimum 10min to avoid runaway
    if iv < 600:
        iv = 600
    _stop_event.clear()
    _thread = threading.Thread(target=_loop, args=(iv,), daemon=True, name="auto-correlation")
    _thread.start()
    _log(f"Started background correlation every {iv}s")
    return True

def stop_background_scheduler():
    _stop_event.set()
    _log("Stop signal sent")

# Auto-start if env enabled (Azure App Service App Setting)
if os.getenv("ENABLE_AUTO_CORRELATION", "").strip() in ("1", "true", "True", "yes"):
    try:
        start_background_scheduler()
    except Exception as e:
        _log(f"Auto-start failed: {e}")
