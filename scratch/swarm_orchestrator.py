#!/usr/bin/env python3
"""
LOCAL SWARM ORCHESTRATOR
Spawns parallel worker processes against evidence repository.
No API quota consumed. Pure local compute.
"""
import subprocess, sys, os, json, time
from pathlib import Path

ROOT = Path(r"C:\OsintNeoAi")
SCRATCH = ROOT / "scratch" / "swarm_output"
SCRATCH.mkdir(parents=True, exist_ok=True)

WORKERS = [
    {"id": "worker_legal",       "script": "worker_legal.py"},
    {"id": "worker_env",         "script": "worker_env.py"},
    {"id": "worker_cyber",       "script": "worker_fin_cyber.py"},
    {"id": "worker_timeline",    "script": "worker_timeline.py"},
    {"id": "worker_docs",        "script": "worker_docs.py"},
]

print("[SWARM] Initiating local swarm protocol...")
print(f"[SWARM] Spawning {len(WORKERS)} parallel workers")
print(f"[SWARM] Output dir: {SCRATCH}")
print()

procs = []
for w in WORKERS:
    script_path = ROOT / "scratch" / w["script"]
    print(f"[SWARM] Launching {w['id']}...")
    p = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=open(SCRATCH / f"{w['id']}.log", "w"),
        stderr=subprocess.STDOUT,
        cwd=str(ROOT)
    )
    procs.append({"id": w["id"], "proc": p})
    time.sleep(0.2)

print(f"\n[SWARM] All {len(procs)} workers launched. Monitoring...")

# Wait for all to complete
for pw in procs:
    pw["proc"].wait()
    rc = pw["proc"].returncode
    status = "✓ DONE" if rc == 0 else f"✗ ERROR (rc={rc})"
    print(f"[SWARM] {pw['id']}: {status}")

print("\n[SWARM] All workers complete. Results in scratch/swarm_output/")
