"""
Test: HTTP 429 exponential backoff in core.transforms (never sleeps in tests).

Run:  cd cli && python test_backoff_429.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core.transforms as T


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code, headers=None, payload=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_backoff_then_success():
    """Two 429s (Retry-After: 1) then 200 → succeeds after 2 retries."""
    script = [
        FakeResponse(429, headers={"Retry-After": "1"}),
        FakeResponse(429, headers={"Retry-After": "2"}),
        FakeResponse(200, payload={"data": {"attributes": {}}}),
    ]
    calls = {"n": 0, "sleeps": []}
    original_request = T.requests.request
    original_sleep = T.time.sleep

    def fake_request(method, url, **kwargs):
        idx = min(calls["n"], len(script) - 1)
        calls["n"] += 1
        return script[idx]

    def fake_sleep(seconds):
        calls["sleeps"].append(seconds)

    T.requests.request = fake_request
    T.time.sleep = fake_sleep
    try:
        r = T.http_request("GET", "https://example.com/api")
    finally:
        T.requests.request = original_request
        T.time.sleep = original_sleep

    assert r.status_code == 200, f"expected 200, got {r.status_code}"
    assert calls["n"] == 3, f"expected 3 attempts, got {calls['n']}"
    assert calls["sleeps"] == [1.0, 2.0], f"sleeps: {calls['sleeps']}"
    print("  [PASS] 429 x2 (Retry-After) then 200 → recovered after 2 backoffs")


def test_exhausted_retries():
    """Persistent 429 → returns the last 429 after max_retries+1 attempts."""
    script = [FakeResponse(429)]
    calls = {"n": 0, "sleeps": []}
    original_request = T.requests.request
    original_sleep = T.time.sleep

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        return script[0]

    def fake_sleep(seconds):
        calls["sleeps"].append(seconds)

    T.requests.request = fake_request
    T.time.sleep = fake_sleep
    try:
        r = T.http_request("GET", "https://example.com/api", max_retries=3, base_delay=1.0)
    finally:
        T.requests.request = original_request
        T.time.sleep = original_sleep

    assert r.status_code == 429, f"expected final 429, got {r.status_code}"
    assert calls["n"] == 4, f"expected 4 attempts (1+3 retries), got {calls['n']}"
    # exponential: 1, 2, 4 (±25% jitter) — verify growth within tolerance
    assert len(calls["sleeps"]) == 3, f"expected 3 sleeps, got {calls['sleeps']}"
    for i, s in enumerate(calls["sleeps"]):
        nominal = 2 ** i
        assert nominal * 0.75 <= s <= nominal * 1.25 + 1e-9, f"sleep[{i}]={s} not near {nominal}"
    print(f"  [PASS] persistent 429 → {calls['n']} attempts, "
          f"exponential sleeps {[round(s, 2) for s in calls['sleeps']]} then final 429")


def test_backoff_delay_growth_and_cap():
    delays = [T._backoff_delay(a) for a in range(10)]
    nominal = [min(1.0 * (2 ** a), T.MAX_BACKOFF_DELAY) for a in range(10)]
    for d, n in zip(delays, nominal):
        assert n * 0.75 <= d <= max(n * 1.25, T.MAX_BACKOFF_DELAY), f"{d} vs {n}"
    assert delays[-1] <= T.MAX_BACKOFF_DELAY * 1.25
    print("  [PASS] _backoff_delay grows exponentially and is capped at 60s")


def test_non_retryable_passthrough():
    """200 and 404 are returned on the first attempt (no needless retries)."""
    calls = {"n": 0}
    original_request = T.requests.request

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        return FakeResponse(404)

    T.requests.request = fake_request
    try:
        r = T.http_request("GET", "https://example.com/missing")
    finally:
        T.requests.request = original_request

    assert r.status_code == 404 and calls["n"] == 1, f"{r.status_code} after {calls['n']} calls"
    print("  [PASS] non-retryable status (404) returned immediately")


def test_transform_end_to_end_on_429():
    """DomainToVirusTotal recovers when VT rate-limits twice then answers."""
    os.environ["VT_API_KEY"] = "dummy-key-for-test"
    payload = {"data": {"attributes": {"last_analysis_stats": {"malicious": 3, "harmless": 86}}}}
    script = [
        FakeResponse(429),
        FakeResponse(429),
        FakeResponse(200, payload=payload),
    ]
    calls = {"n": 0, "sleeps": []}
    original_request = T.requests.request
    original_sleep = T.time.sleep

    def fake_request(method, url, **kwargs):
        idx = min(calls["n"], len(script) - 1)
        calls["n"] += 1
        return script[idx]

    def fake_sleep(seconds):
        calls["sleeps"].append(seconds)

    T.requests.request = fake_request
    T.time.sleep = fake_sleep
    try:
        results = T.DomainToVirusTotal().run(T.Domain(value="example.com"))
    finally:
        T.requests.request = original_request
        T.time.sleep = original_sleep
        os.environ.pop("VT_API_KEY", None)

    assert results, "transform returned no results"
    assert "VT Score: 3/89" in results[0].value, results[0].value
    assert calls["n"] == 3, f"expected 3 HTTP attempts, got {calls['n']}"
    print(f"  [PASS] DomainToVirusTotal recovered from 429 → {results[0].value!r}")


if __name__ == "__main__":
    print("[*] HTTP 429 exponential backoff tests")
    test_backoff_then_success()
    test_exhausted_retries()
    test_backoff_delay_growth_and_cap()
    test_non_retryable_passthrough()
    test_transform_end_to_end_on_429()
    print("[OK] all backoff tests passed")
