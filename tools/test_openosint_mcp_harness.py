#!/usr/bin/env python3
"""
test_openosint_mcp_harness.py — Automated Test Harness for 19 Native OpenOSINT MCP Tools
Governance: AI Law 1 (Repeated processes become AI Tools), AI Law 2 (Strict Verification Output)

Executes test calls across all 19 tools defined in openosint_mcp_server.py and logs results.
"""

import sys
import os
import json

sys.path.append(r"C:\OsintNeoAi\tools")
import openosint_mcp_server

TEST_CALLS = [
    ("osint_lookup_person", {"name": "Andrew Do", "location": "Orange County, CA"}),
    ("osint_lookup_email", {"email": "anthony.dimarcello@students.post.edu"}),
    ("osint_lookup_phone", {"phone": "+17145550199"}),
    ("osint_lookup_domain", {"domain": "osintneoai.me"}),
    ("osint_lookup_ip", {"ip": "8.8.8.8"}),
    ("osint_search_entity", {"query": "Viet America Society"}),
    ("osint_court_records", {"case_number": "30-2024-01389012"}),
    ("osint_property_records", {"apn": "142-073-33"}),
    ("osint_social_footprint", {"handle": "Tonypost949"}),
    ("osint_crypto_wallet", {"address": "0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B"}),
    ("osint_foia_tracker", {"tracking_id": "FOIA-2026-OC-0091"}),
    ("osint_fca_timeline", {"entity": "Andrew Do"}),
    ("osint_sec_edgar", {"cik": "0000320193"}),
    ("osint_wayback_history", {"url": "https://osintneoai.me"}),
    ("osint_geo_telemetry", {"lat": 33.7025, "lng": -118.0053}),
    ("osint_breach_scanner", {"query": "amd949609@gmail.com"}),
    ("osint_license_lookup", {"license_num": "CA-LAW-99120"}),
    ("osint_charity_990", {"ein": "95-1234567"}),
    ("osint_system_health", {})
]

def run_harness():
    print("=" * 70)
    print("⚡ OPENOSINT NATIVE MCP SERVER — 19 TOOL AUTOMATED TEST HARNESS")
    print("=" * 70)

    passed = 0
    failed = 0
    results = []

    for idx, (name, args) in enumerate(TEST_CALLS, 1):
        try:
            res = openosint_mcp_server.handle_tool_call(name, args)
            res_str = json.dumps(res) if isinstance(res, dict) else str(res)
            status = "PASSED" if res and "error" not in res_str.lower() else "WARNING"
            if status == "PASSED":
                passed += 1
            else:
                failed += 1
            print(f"  [{idx:02d}/19] {name:<25} -> ✅ {status}")
            results.append({"tool": name, "status": status, "output_len": len(res_str)})
        except Exception as e:
            failed += 1
            print(f"  [{idx:02d}/19] {name:<25} -> ❌ FAILED ({e})")
            results.append({"tool": name, "status": "FAILED", "error": str(e)})

    print("=" * 70)
    print(f"HARNESS SUMMARY: {passed} PASSED | {failed} WARN/FAIL | TOTAL: {len(TEST_CALLS)}")
    print("=" * 70)

    # Save output to data directory
    output_path = r"C:\OsintNeoAi\data\openosint_mcp_test_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"summary": {"passed": passed, "failed": failed}, "results": results}, f, indent=2)
    print(f"Test Harness Report saved to: {output_path}")

if __name__ == "__main__":
    run_harness()
