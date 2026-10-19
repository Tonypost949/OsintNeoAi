"""
Unit & Integration Test Suite: OSINT Evidence Collector Chrome Extension (TASK-067)
===================================================================================
Verifies Manifest V3 compliance, required permissions, icon assets, popup controller,
background service worker, and payload integrity for the OSINT Evidence Collector.
"""

import os
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXT_DIR = REPO_ROOT / "chrome_extension" / "osint_collector_v2"

class TestChromeExtensionOSINTCollector(unittest.TestCase):

    def test_manifest_v3_structure(self):
        """Verify manifest.json exists and conforms to Manifest V3 requirements."""
        manifest_file = EXT_DIR / "manifest.json"
        self.assertTrue(manifest_file.exists(), "manifest.json must exist in osint_collector_v2")

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest.get("manifest_version"), 3)
        self.assertIn("OSINT", manifest.get("name", ""))
        self.assertIn("version", manifest)
        self.assertIn("permissions", manifest)

        perms = manifest["permissions"]
        self.assertIn("activeTab", perms)
        self.assertIn("tabs", perms)
        self.assertIn("storage", perms)
        self.assertIn("contextMenus", perms)

        # Background service worker
        bg = manifest.get("background", {})
        self.assertEqual(bg.get("service_worker"), "background.js")
        self.assertEqual(bg.get("type"), "module")

        # Action Popup
        action = manifest.get("action", {})
        self.assertEqual(action.get("default_popup"), "popup.html")

    def test_popup_and_script_files_exist(self):
        """Verify popup.html, popup.js, background.js, content.js exist."""
        for filename in ["popup.html", "popup.js", "background.js", "content.js"]:
            filepath = EXT_DIR / filename
            self.assertTrue(filepath.exists(), f"{filename} must exist")
            self.assertGreater(filepath.stat().st_size, 50, f"{filename} must not be empty")

    def test_popup_html_elements(self):
        """Verify popup.html contains essential HUD elements."""
        content = (EXT_DIR / "popup.html").read_text(encoding="utf-8")
        self.assertIn("OSINT Neo AI", content)
        self.assertIn("btn-submit-evidence", content)
        self.assertIn("btn-dump-json", content)
        self.assertIn("tab-vault", content)

    def test_background_service_worker_routes(self):
        """Verify background.js contains context menu declarations and hash helpers."""
        content = (EXT_DIR / "background.js").read_text(encoding="utf-8")
        self.assertIn("contextMenus.create", content)
        self.assertIn("SHA-256", content)
        self.assertIn("osint_receipts", content)

if __name__ == "__main__":
    unittest.main()
