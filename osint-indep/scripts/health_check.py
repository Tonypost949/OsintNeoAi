#!/usr/bin/env python3
# health_check.py - System health verification

import sys
import os
import sqlite3
import subprocess
from pathlib import Path

def check_python_imports():
    """Verify all core modules can be imported"""
    try:
        from src.core import config, database, models
        from src.collectors import base, web, dns, whois
        from src.analyzers import correlation, graph, timeline
        return True, "All imports OK"
    except ImportError as e:
        return False, f"Import failed: {e}"

def check_database():
    """Verify database connectivity and schema"""
    try:
        from src.core.database import init_database, get_database
        init_database()
        db = get_database()
        with db.session() as session:
            session.execute("SELECT 1")
        return True, "Database OK"
    except Exception as e:
        return False, f"Database error: {e}"

def check_config():
    """Verify configuration loads"""
    try:
        from src.core.config import get_config
        cfg = get_config()
        return True, f"Config loaded (DB: {cfg.database.type})"
    except Exception as e:
        return False, f"Config error: {e}"

def check_collectors():
    """Verify collector registry"""
    try:
        from src.collectors.base import CollectorRegistry
        collectors = CollectorRegistry.list_collectors()
        return True, f"Collectors: {len(collectors)} registered ({', '.join(collectors)})"
    except Exception as e:
        return False, f"Collector registry error: {e}"

def check_assets():
    """Verify vendor assets exist"""
    vendor_dir = Path("vendor")
    required = [
        "leaflet-1.9.4/leaflet.js",
        "leaflet-1.9.4/leaflet.css",
        "chartjs-4.4.0/chart.umd.min.js",
        "bootstrap-5.3.0/css/bootstrap.min.css",
        "bootstrap-5.3.0/js/bootstrap.bundle.min.js",
        "fontawesome-6.4.0/css/all.min.css"
    ]
    missing = []
    for asset in required:
        if not (vendor_dir / asset).exists():
            missing.append(asset)
    
    if missing:
        return False, f"Missing assets: {', '.join(missing)}"
    return True, "All vendor assets present"

def check_models():
    """Verify model directory structure"""
    models_dir = Path("models")
    if not models_dir.exists():
        return True, "No models directory (OK if using remote)"
    
    model_files = list(models_dir.rglob("*.pt")) + list(models_dir.rglob("*.bin")) + \
                  list(models_dir.rglob("*.onnx")) + list(models_dir.rglob("*.pkl"))
    if model_files:
        return True, f"Models: {len(model_files)} files"
    return True, "Models directory exists but empty"

def check_build_tools():
    """Verify build tools directory"""
    build_dir = Path("build-tools")
    if not build_dir.exists():
        return True, "No build-tools directory (OK if not needed)"
    
    tools = list(build_dir.iterdir())
    return True, f"Build tools: {len(tools)} directories"

def check_git_status():
    """Check git repo health"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Git status failed"
        dirty = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
        return True, f"Git clean ({dirty} uncommitted files)" if dirty == 0 else f"Git: {dirty} uncommitted"
    except Exception as e:
        return False, f"Git check failed: {e}"

def main():
    checks = [
        ("Python Imports", check_python_imports),
        ("Database", check_database),
        ("Configuration", check_config),
        ("Collectors", check_collectors),
        ("Vendor Assets", check_assets),
        ("Models", check_models),
        ("Build Tools", check_build_tools),
        ("Git Status", check_git_status),
    ]
    
    print("=== OSINT Independent Platform Health Check ===\n")
    
    all_passed = True
    for name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status} | {name}: {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"  ✗ ERROR | {name}: {e}")
            all_passed = False
    
    print()
    if all_passed:
        print("=== ALL HEALTH CHECKS PASSED ===")
        return 0
    else:
        print("=== SOME CHECKS FAILED ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())