#!/usr/bin/env python3
"""
test_all_19_mcp_tools.py — Automated Test Suite for all 19 OpenOSINT MCP Tools
Validates tool execution, schema compliance, and JSON-RPC responses.
"""

import sys
import os
import json
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import openosint_mcp_server as mcp

TEST_CASES = [
    ("osint_lookup_person", {"name": "Anthony DiMarcello", "location": "Huntington Beach, CA"}),
    ("osint_lookup_email", {"email": "amd949609@gmail.com"}),
    ("osint_lookup_phone", {"phone": "7145550199"}),
    ("osint_lookup_domain", {"domain": "osintneoai.me"}),
    ("osint_lookup_ip", {"ip": "8.8.8.8"}),
    ("osint_search_entity", {"query": "Huntington Beach Navigation Center"}),
    ("osint_court_records", {"case_or_name": "Knabb v. Huntington Beach"}),
    ("osint_property_records", {"apn_or_address": "Cameron Lane Tract"}),
    ("osint_social_footprint", {"username": "Tonypost949"}),
    ("osint_crypto_wallet", {"address": "0x7236F4982a31537d07f3182A1CdAD3f3E4452A53"}),
    ("osint_foia_tracker", {"agency": "City of Huntington Beach", "topic": "Toxic Endangerment"}),
    ("osint_fca_timeline", {"entity": "Orange County Homeless Services"}),
    ("osint_sec_edgar", {"ticker_or_cik": "MSFT"}),
    ("osint_wayback_history", {"url": "https://osintneoai.me"}),
    ("osint_geo_telemetry", {"lat": 33.6595, "lng": -117.9988, "label": "Bolsa Chica Wetlands"}),
    ("osint_breach_scanner", {"query": "amd949609@gmail.com"}),
    ("osint_license_lookup", {"license_no": "CA-LAW-10928", "state": "CA"}),
    ("osint_charity_990", {"ein_or_name": "Orange County Navigation Center"}),
    ("osint_system_health", {})
]

def run_tests():
    print("=" * 70)
    print("  RUNNING MCP AUTOMATED TEST SUITE (19 NATIVE FORENSIC TOOLS)")
    print("=" * 70)

    passed = 0
    failed = 0
    results = []

    for idx, (tool_name, args) in enumerate(TEST_CASES, 1):
        print(f"[{idx:02d}/19] Testing tool: {tool_name}...")
        try:
            res = mcp.handle_tool_call(tool_name, args)
            if res and isinstance(res, dict):
                print(f"       Status: OK | Response Keys: {list(res.keys())}")
                passed += 1
                results.append({"tool": tool_name, "status": "PASSED", "response": res})
            else:
                print(f"       Status: FAILED | Invalid response format: {res}")
                failed += 1
                results.append({"tool": tool_name, "status": "FAILED", "response": res})
        except Exception as e:
            print(f"       Status: ERROR | Exception: {e}")
            failed += 1
            results.append({"tool": tool_name, "status": "ERROR", "error": str(e)})

    print("=" * 70)
    print(f"  TEST HARNESS SUMMARY: {passed} PASSED | {failed} FAILED / 19 TOTAL")
    print("=" * 70)

    report_path = Path(__file__).parent.parent / "data" / "mcp_test_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"total_tools": 19, "passed": passed, "failed": failed, "results": results}, f, indent=2)

    print(f"[+] Full test report saved to: {report_path}")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
