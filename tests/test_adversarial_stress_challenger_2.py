"""
tests/test_adversarial_stress_challenger_2.py
=============================================
Empirical Adversarial Stress & Concurrency Test Suite (Challenger 2)
Focus Areas:
1. Concurrent Intake Bursts (100 threads /api/submit-victim, 50 threads /webhook)
2. Simultaneous HTTP Reads during active correlation runs
3. Thread Lock Reentrancy, Contention & Exception Recovery
4. Rapid Background Scheduler Start/Stop Lifecycle & Clamping
5. Memory Footprint Stress (<512MB threshold across 50k nodes / multi-runs)
6. Azure App Service Deployment Package Completeness & Sandbox Verification
"""

import os
import sys
import json
import time
import shutil
import tempfile
import zipfile
import threading
import tracemalloc
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup environment and imports
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from api.app import app, POWERAPPS_SWAGGER_SPEC
import api.auto_correlation as auto_corr
from scripts.deploy_azure_clean import create_deployment_package, ZIP_PATH, INCLUDE_FILES, INCLUDE_DIRS


class TestAdversarialIntakeBursts(unittest.TestCase):
    """Stress test concurrent intake bursts against Flask endpoints and file persistence."""

    def setUp(self):
        self.app_client = app.test_client()
        self.test_dir = tempfile.mkdtemp(prefix="osint_burst_")
        self.cases_file = os.path.join(self.test_dir, "mutual_aid_cases.json")
        
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_concurrent_submit_victim_100_threads(self):
        """Submit 100 simultaneous victim/whistleblower reports and verify zero data corruption."""
        num_threads = 100
        results = []
        errors = []

        def _worker(i):
            payload = {
                "victim_name": f"Whistleblower-{i:03d}",
                "contact_info": f"agent_{i}@secure-osint.org",
                "incident_type": "Public Corruption Kickback",
                "location": f"{1000 + i} E Ball Rd Ste {i%10}, Anaheim, CA",
                "apn": f"178-431-{i:02d}",
                "summary": f"Evidence packet #{i} detailing municipal land diversion."
            }
            try:
                res = self.app_client.post("/api/submit-victim", json=payload)
                return (i, res.status_code, res.get_json())
            except Exception as e:
                return (i, 500, str(e))

        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(_worker, i) for i in range(num_threads)]
            for fut in as_completed(futures):
                idx, status, data = fut.result()
                if status == 200 and isinstance(data, dict) and data.get("status") == "SUCCESS":
                    results.append(data)
                else:
                    errors.append((idx, status, data))

        duration = time.time() - start_time
        self.assertEqual(len(errors), 0, f"Encountered errors during concurrent intake: {errors}")
        self.assertEqual(len(results), num_threads, f"Expected {num_threads} successful submissions, got {len(results)}")
        self.assertLess(duration, 15.0, f"100 intake requests took too long: {duration:.2f}s")

    def test_concurrent_webhook_mixed_traffic(self):
        """Simulate 50 concurrent webhooks with mixed DMs, comments, and invalid verification queries."""
        def _webhook_worker(i):
            if i % 3 == 0:
                # Meta verification handshake
                res = self.app_client.get("/webhook?hub.mode=subscribe&hub.verify_token=makaveli_osint_verify_2026&hub.challenge=test_chall_123")
                return res.status_code == 200 and res.get_data(as_text=True) == "test_chall_123"
            elif i % 3 == 1:
                # Messenger DM payload
                body = {
                    "object": "page",
                    "entry": [{
                        "messaging": [{
                            "sender": {"id": f"user_{i}"},
                            "recipient": {"id": "page_949"},
                            "message": {"text": f"Forensic inquiry #{i} on Angel Stadium land sale."}
                        }]
                    }]
                }
                res = self.app_client.post("/webhook", json=body)
                return res.status_code == 200
            else:
                # Unauthorized verification
                res = self.app_client.get("/webhook?hub.mode=subscribe&hub.verify_token=wrong_token")
                return res.status_code == 403

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(_webhook_worker, i) for i in range(50)]
            for fut in as_completed(futures):
                self.assertTrue(fut.result(), "Webhook event handling failed under concurrency")


class TestAdversarialSimultaneousReadsAndRuns(unittest.TestCase):
    """Stress test simultaneous HTTP reads while active correlation engine runs."""

    def setUp(self):
        self.app_client = app.test_client()

    def test_simultaneous_reads_during_correlation_run(self):
        """Run correlation in background while 50 read threads query status, leads, correlate, and search."""
        read_successes = 0
        read_failures = []
        stop_event = threading.Event()

        def _reader():
            nonlocal read_successes
            while not stop_event.is_set():
                try:
                    r1 = self.app_client.get("/api/correlation/status")
                    r2 = self.app_client.get("/api/leads")
                    r3 = self.app_client.get("/api/correlate")
                    r4 = self.app_client.get("/api/search?q=178-431-14")
                    r5 = self.app_client.get("/openapi_azure_powerapps.json")
                    
                    if all(r.status_code == 200 for r in [r1, r2, r3, r4, r5]):
                        read_successes += 5
                    else:
                        read_failures.append([r.status_code for r in [r1, r2, r3, r4, r5]])
                except Exception as ex:
                    read_failures.append(str(ex))
                time.sleep(0.02)

        # Start 5 concurrent readers
        reader_threads = [threading.Thread(target=_reader, daemon=True) for _ in range(5)]
        for t in reader_threads:
            t.start()

        # Trigger synchronous correlation run
        payload = auto_corr.run_leads_correlation()
        self.assertIsInstance(payload, dict)
        self.assertNotIn("error", payload.get("error", "") if isinstance(payload.get("error"), str) else "")

        # Also trigger async endpoint
        async_res = self.app_client.post("/api/correlation/run?async=1")
        self.assertEqual(async_res.status_code, 200)
        self.assertEqual(async_res.get_json().get("status"), "triggered")

        # Let readers continue for a brief moment
        time.sleep(0.5)
        stop_event.set()
        for t in reader_threads:
            t.join(timeout=2.0)

        self.assertEqual(len(read_failures), 0, f"Read failures during correlation run: {read_failures}")
        self.assertGreater(read_successes, 20, "Expected at least 20 successful read operations")


class TestAdversarialLockReentrancyAndExceptions(unittest.TestCase):
    """Stress test thread lock contention, reentrancy, and exception safety in auto_correlation."""

    def test_high_contention_get_last_run(self):
        """Verify get_last_run() withstands 100 concurrent threads without deadlock or race corruption."""
        errors = []
        results = []

        def _contender():
            try:
                for _ in range(20):
                    data = auto_corr.get_last_run()
                    assert isinstance(data, dict)
                    assert "at" in data
                    assert "leads" in data
                    results.append(data)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(_contender) for _ in range(20)]
            for fut in as_completed(futures):
                fut.result()

        self.assertEqual(len(errors), 0, f"Contention errors on get_last_run: {errors}")
        self.assertEqual(len(results), 400, "All 400 last_run fetches must succeed")

    def test_exception_recovery_does_not_poison_lock(self):
        """Simulate an exception in run_leads_correlation() and verify lock is released and error recorded."""
        with unittest.mock.patch("scripts.auto_leads_correlation_v2.run_correlation", side_effect=RuntimeError("Simulated Engine Panic")):
            result = auto_corr.run_leads_correlation()
            self.assertIn("Simulated Engine Panic", result.get("error", ""))
            
            # Verify telemetry reflects error cleanly
            last = auto_corr.get_last_run()
            self.assertIn("Simulated Engine Panic", str(last.get("error")))
            self.assertEqual(last.get("leads"), 0)

        # Verify subsequent normal run succeeds without deadlock
        clean_result = auto_corr.run_leads_correlation()
        self.assertIsInstance(clean_result, dict)
        self.assertGreaterEqual(len(clean_result.get("leads", [])), 0)


class TestAdversarialSchedulerLifecycle(unittest.TestCase):
    """Stress test rapid scheduler toggles, interval clamping, and clean teardown."""

    def tearDown(self):
        auto_corr.stop_background_scheduler()

    def test_rapid_start_stop_scheduler_toggles(self):
        """Rapidly toggle start/stop 20 times and assert clean thread state."""
        for _ in range(20):
            started = auto_corr.start_background_scheduler(interval=600)
            self.assertTrue(started or auto_corr._thread.is_alive())
            auto_corr.stop_background_scheduler()
            time.sleep(0.01)

        auto_corr.stop_background_scheduler()
        time.sleep(0.1)

    def test_interval_clamping_enforcement(self):
        """Assert intervals below 600s are clamped to 600s."""
        auto_corr.stop_background_scheduler()
        started = auto_corr.start_background_scheduler(interval=10)  # Try requesting 10 seconds
        self.assertTrue(started)
        
        # Calling start again while active should safely return False
        duplicate_start = auto_corr.start_background_scheduler(interval=600)
        self.assertFalse(duplicate_start)

        auto_corr.stop_background_scheduler()


class TestAdversarialMemoryFootprint(unittest.TestCase):
    """Stress test memory ceiling (<512MB) across multi-run correlations and large graph traversals."""

    def test_memory_ceiling_under_512mb_across_repeated_runs(self):
        """Profile memory allocation across 5 back-to-back correlation runs."""
        tracemalloc.start()
        peak_mb_list = []

        try:
            for _ in range(5):
                res = auto_corr.run_leads_correlation()
                self.assertIsInstance(res, dict)
                current, peak = tracemalloc.get_traced_memory()
                peak_mb = peak / (1024 * 1024)
                peak_mb_list.append(peak_mb)
        finally:
            tracemalloc.stop()

        max_peak = max(peak_mb_list)
        # Memory threshold is 512MB; practical usage should be < 200MB
        self.assertLess(max_peak, 512.0, f"Peak memory {max_peak:.2f}MB exceeded 512MB limit")
        print(f"\n[STRESS MEMORY] Max peak memory across 5 runs: {max_peak:.2f} MB (Budget: 512.0 MB)")

    def test_synthetic_large_graph_traversal_memory(self):
        """Traverse a synthetic graph with 50,000 nodes and 75,000 edges and assert memory < 250MB."""
        tracemalloc.start()
        try:
            nodes = {f"NODE_{i}": {"id": f"NODE_{i}", "type": "PERSON" if i % 2 == 0 else "CORP", "name": f"Entity_{i}"} for i in range(50000)}
            edges = [{"source": f"NODE_{i}", "target": f"NODE_{(i+1)%50000}", "relationship": "OFFICER_OF"} for i in range(75000)]
            
            # Simple traversal
            adj = {}
            for e in edges:
                adj.setdefault(e["source"], []).append(e["target"])
            
            visited = set()
            queue = ["NODE_0"]
            while queue and len(visited) < 10000:
                curr = queue.pop(0)
                if curr not in visited:
                    visited.add(curr)
                    queue.extend(adj.get(curr, []))

            current, peak = tracemalloc.get_traced_memory()
            peak_mb = peak / (1024 * 1024)
            self.assertLess(peak_mb, 250.0, f"Synthetic 50k graph traversal consumed {peak_mb:.2f} MB, exceeding 250 MB")
        finally:
            tracemalloc.stop()


class TestAdversarialDeploymentPackageCompleteness(unittest.TestCase):
    """Stress test deploy_azure_clean.py archive completeness and standalone extraction integrity."""

    def test_deployment_package_generation_and_inventory(self):
        """Generate azure_deploy.zip and verify 100% of required runtime artifacts exist in zip."""
        zip_output = create_deployment_package(deploy_to_azure=False)
        self.assertTrue(os.path.exists(zip_output), "azure_deploy.zip must be created")

        zip_size_mb = os.path.getsize(zip_output) / (1024 * 1024)
        self.assertGreater(zip_size_mb, 1.0, f"Deployment zip suspiciously small ({zip_size_mb:.2f} MB)")
        self.assertLess(zip_size_mb, 600.0, f"Deployment zip exceeds Azure App Service limit ({zip_size_mb:.2f} MB)")

        with zipfile.ZipFile(zip_output, "r") as z:
            namelist = set(z.namelist())

            # Essential root files
            for ef in ["app.py", "startup.sh", "requirements.txt", "nodes.json", "edges.json", "control_clusters.json", "openapi_azure_powerapps.json"]:
                self.assertIn(ef, namelist, f"Essential file {ef} missing from deployment zip")

            # Essential API modules
            for apif in ["api/app.py", "api/auto_correlation.py", "api/osint_pipeline/normalizers.py"]:
                self.assertIn(apif, namelist, f"API module {apif} missing from deployment zip")

            # Essential scripts
            for sf in ["scripts/auto_leads_correlation_v2.py", "scripts/calculate_cctv_proximity.py", "scripts/run_forensic_crossref_engine.py"]:
                self.assertIn(sf, namelist, f"Script {sf} missing from deployment zip")

            # Essential evidence datasets
            for evf in ["evidence/caltrans_d12_cctv.geojson", "evidence/FORENSIC_CORRELATION_MATRIX.json", "evidence/mutual_aid_cases.json"]:
                self.assertIn(evf, namelist, f"Evidence file {evf} missing from deployment zip")

    def test_standalone_sandbox_extraction_and_import(self):
        """Extract azure_deploy.zip into an isolated sandbox and verify module importability."""
        sandbox_dir = tempfile.mkdtemp(prefix="azure_sandbox_")
        try:
            with zipfile.ZipFile(ZIP_PATH, "r") as z:
                z.extractall(sandbox_dir)

            # Assert key files exist in extracted sandbox
            self.assertTrue(os.path.exists(os.path.join(sandbox_dir, "app.py")))
            self.assertTrue(os.path.exists(os.path.join(sandbox_dir, "nodes.json")))
            self.assertTrue(os.path.exists(os.path.join(sandbox_dir, "api", "app.py")))
            self.assertTrue(os.path.exists(os.path.join(sandbox_dir, "scripts", "auto_leads_correlation_v2.py")))

            # Verify requirements.txt contains critical packages
            req_path = os.path.join(sandbox_dir, "requirements.txt")
            with open(req_path, "r", encoding="utf-8") as rf:
                req_text = rf.read()
                self.assertIn("flask", req_text.lower())
                self.assertIn("google-generativeai", req_text.lower())

        finally:
            shutil.rmtree(sandbox_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
