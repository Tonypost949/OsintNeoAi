"""
Meta Model API Client for OsintNeoAi & Makaveli Agent
Reference: https://dev.meta.ai/docs/api-reference/
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class MetaModelClient:
    """Client for Meta Model API (dev.meta.ai)."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.meta.ai/v1"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("META_API_KEY")
        if not self.api_key:
            # Fallback: check muse auth.json
            home = os.environ.get("HOME") or os.environ.get("USERPROFILE", "")
            auth_path = os.path.join(home, ".config", "muse", "auth.json")
            if os.path.exists(auth_path):
                try:
                    with open(auth_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.api_key = data.get("providers", {}).get("meta", {}).get("access_token")
                except Exception:
                    pass

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "OsintNeoAi-Makaveli/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        req_data = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=req_data, headers=self._headers(), method=method)
        
        try:
            with urllib.request.urlopen(req) as resp:
                res_body = resp.read().decode("utf-8")
                return json.loads(res_body) if res_body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return {"error": {"code": e.code, "message": str(e), "details": err_body}}
        except Exception as e:
            return {"error": {"message": str(e)}}

    def list_models(self) -> Dict[str, Any]:
        """GET /models — List available Meta foundation models."""
        return self._request("/models", method="GET")

    def get_status(self) -> Dict[str, Any]:
        """GET /status — Retrieve API status and rate limits."""
        return self._request("/status", method="GET")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-instruct",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """POST /chat/completions — OpenAI-compatible chat completion."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        return self._request("/chat/completions", method="POST", data=payload)

    def makaveli_query(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Execute a zero-noise forensic query using the Makaveli Protocol."""
        sys_instructions = system_prompt or (
            "You are Makaveli — Lead OSINT Agent of OsintNeoAi. "
            "Zero-noise forensic correlation. No synthetic hedging. Direct, tactical, evidentiary output."
        )
        messages = [
            {"role": "system", "content": sys_instructions},
            {"role": "user", "content": prompt}
        ]
        return self.chat_completion(messages=messages)

if __name__ == "__main__":
    client = MetaModelClient()
    print("[INIT] MetaModelClient loaded.")
    print(f"[STATUS] Target Base URL: {client.base_url}")
    print(f"[AUTH] Key Present: {bool(client.api_key)}")
