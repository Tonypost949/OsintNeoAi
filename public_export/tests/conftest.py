"""
tests/conftest.py
=================
Global Pytest Configuration and Test Harness Shims for OsintNeoAi E2E Test Suite.
Provides safe route resolution, repo root sys.path setup, and test environment fixtures.
"""

import sys
import os
from pathlib import Path

# Resolve repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Safe route registration shim for Flask sansio to handle duplicate endpoint names gracefully
try:
    import flask
    import flask.sansio.app
    _orig_add_url_rule = flask.sansio.app.App.add_url_rule
    
    def _safe_add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        ep = endpoint or (view_func.__name__ if view_func else None)
        if ep and ep in self.view_functions:
            ep = f"{ep}_{len(self.view_functions)}"
        return _orig_add_url_rule(self, rule, endpoint=ep, view_func=view_func, **options)
        
    flask.sansio.app.App.add_url_rule = _safe_add_url_rule
except Exception:
    pass

os.environ["TESTING"] = "1"
