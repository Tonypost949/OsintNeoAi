"""
api/auto_correlation.py
=======================
Azure App Service in-process Auto-Correlation Orchestrator
- Exposes run_leads_correlation() callable for HTTP triggers
- Provides start_background_scheduler() for 24/7 autonomous cloud loops
- Safe: catches all exceptions, logs to stdout (visible in az webapp log tail)
- Zero local load: operates 100% in Azure cloud runtime

Env:
  ENABLE_AUTO_CORRELATION=1       -> auto-start background thread on import
  AUTO_CORRELATION_INTERVAL=7200  -> seconds between runs (default 2h, clamped >=600s)
"""
import os
import sys
import threading
import time
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if not (REPO_ROOT / "scripts").exists():
    for cand in [Path("/home/site/wwwroot"), Path("C:/OsintNeoAi"), Path.cwd()]:
        if (cand / "scripts").exists():
            REPO_ROOT = cand
            break

SCRIPTS_PATH = REPO_ROOT / "scripts" / "auto_leads_correlation_v2.py"

_last_run = {"at": None, "leads": 0, "elapsed": 0, "error": None, "summary": {}, "graph_stats": {}}
_lock = threading.Lock()
_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


def _log(msg: str) -> None:
    print(f"[AUTO_CORRELATION] {datetime.now(timezone.utc).isoformat()} {msg}", flush=True)


def run_leads_correlation() -> Dict[str, Any]:
    """Synchronous single correlation run. Returns payload dict."""
    global _last_run
    started = datetime.now(timezone.utc)
    try:
        # Import and run engine directly
        import importlib.util
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        spec = importlib.util.spec_from_file_location("auto_leads_correlation_v2", str(SCRIPTS_PATH))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec from {SCRIPTS_PATH}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        payload = mod.run_correlation()
        
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        with _lock:
            _last_run = {
                "at": datetime.now(timezone.utc).isoformat(),
                "leads": len(payload.get("leads", [])),
                "elapsed": payload.get("summary", {}).get("elapsed", round(elapsed, 2)),
                "error": None,
                "summary": payload.get("summary", {}),
                "graph_stats": payload.get("graph_stats", {})
            }
        return payload
    except Exception as e:
        err = f"{e}\n{traceback.format_exc()}"
        _log(f"ERROR run: {err}")
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        with _lock:
            _last_run = {
                "at": datetime.now(timezone.utc).isoformat(),
                "leads": 0,
                "elapsed": round(elapsed, 2),
                "error": str(e),
                "summary": {},
                "graph_stats": {}
            }
        return {"error": str(e), "trace": err, "leads": [], "summary": {}}


def get_last_run() -> Dict[str, Any]:
    with _lock:
        return dict(_last_run)


def _loop(interval: int) -> None:
    _log(f"Background scheduler started interval={interval}s")
    # Stagger first run by 15s to let Flask HTTP socket bind first
    time.sleep(15)
    while not _stop_event.is_set():
        _log("Scheduler tick -> running correlation")
        try:
            run_leads_correlation()
        except Exception as e:
            _log(f"Scheduler run failed: {e}")
        # Wait with interruptible sleep
        _stop_event.wait(interval)
    _log("Background scheduler stopped")


def start_background_scheduler(interval: Optional[int] = None) -> bool:
    global _thread
    with _lock:
        if _thread and _thread.is_alive():
            _log("Scheduler already running")
            return False
    try:
        iv = int(interval or os.getenv("AUTO_CORRELATION_INTERVAL", "7200"))
    except Exception:
        iv = 7200
    # Clamp to minimum 10min (600s) to avoid runaway
    if iv < 600:
        iv = 600
    _stop_event.clear()
    _thread = threading.Thread(target=_loop, args=(iv,), daemon=True, name="auto-correlation")
    _thread.start()
    _log(f"Started background correlation daemon every {iv}s")
    return True


def stop_background_scheduler() -> None:
    _stop_event.set()
    _log("Stop signal sent")


# Auto-start if env enabled (Azure App Service App Setting)
if os.getenv("ENABLE_AUTO_CORRELATION", "").strip() in ("1", "true", "True", "yes"):
    try:
        start_background_scheduler()
    except Exception as e:
        _log(f"Auto-start failed: {e}")
