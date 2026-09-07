"""
OsintNeoAi — Open-Source Free AI Gateway
All user input processed through free open-source AI models.
No local GPU required — all inference is cloud-hosted.

Provider priority:
  1. Groq  (free tier — Mixtral-8x7b, LLaMA3-70b)
  2. Together.ai (free tier)
  3. Ollama cloud instance (self-hosted)
  4. Gemini Flash (paid fallback)

Usage:
  python agent/opensource_ai_gateway.py --port 11434

Environment:
  GROQ_API_KEY        Groq free tier
  TOGETHER_API_KEY    Together.ai free tier
  OLLAMA_BASE_URL     Self-hosted Ollama endpoint
  GEMINI_API_KEY      Gemini fallback (optional)
"""

import os
import json
import logging
import time
import hashlib
import urllib.request
from typing import Generator
from flask import Flask, request, jsonify, Response, stream_with_context

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

OSINT_SYSTEM_CONTEXT = (
    "You are OsintNeoAi — a forensic intelligence assistant. "
    "Help users conduct OSINT investigations, analyze public records, identify corruption "
    "patterns, cross-reference evidence, and compile whistleblower dossiers. "
    "Always cite sources. Be precise and factual. Never fabricate records."
)

PROVIDERS = [
    {
        "name":    "groq",
        "url":     "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "models":  ["mixtral-8x7b-32768", "llama3-70b-8192"],
        "free":    True,
    },
    {
        "name":    "together",
        "url":     "https://api.together.xyz/v1/chat/completions",
        "key_env": "TOGETHER_API_KEY",
        "models":  ["togethercomputer/llama-2-70b-chat"],
        "free":    True,
    },
    {
        "name":    "ollama",
        "url":     None,  # built dynamically from OLLAMA_BASE_URL
        "key_env": None,
        "models":  ["deepseek-r1:8b", "mistral:7b"],
        "free":    True,
    },
    {
        "name":    "gemini",
        "url":     None,  # built dynamically
        "key_env": "GEMINI_API_KEY",
        "models":  ["gemini-2.0-flash"],
        "free":    False,
    },
]


def _get_active_providers():
    active = []
    for p in PROVIDERS:
        if p["key_env"] is None or os.environ.get(p["key_env"]):
            active.append(p)
    return active


def _openai_call(url, api_key, messages, model, timeout=30):
    payload = json.dumps({"model": model, "messages": messages, "max_tokens": 4096, "temperature": 0.7}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Authorization": "Bearer {}".format(api_key), "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _ollama_call(messages, model):
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    prompt = "\n".join("{}: {}".format("User" if m["role"] == "user" else "Assistant", m["content"]) for m in messages)
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request("{}/api/generate".format(base_url), data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read())
        return {"choices": [{"message": {"content": r.get("response", "")}}]}


def _gemini_call(messages, model, api_key):
    contents = [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages]
    payload = json.dumps({"contents": contents}).encode()
    url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(model, api_key)
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.loads(resp.read())
        text = r["candidates"][0]["content"]["parts"][0]["text"]
        return {"choices": [{"message": {"content": text}}]}


def route_query(messages, preferred_model=None):
    providers = _get_active_providers()
    if not providers:
        return {"choices": [{"message": {"content": "No AI provider configured. Set GROQ_API_KEY or OLLAMA_BASE_URL."}}]}
    last_error = None
    for p in providers:
        model = preferred_model or p["models"][0]
        try:
            logger.info("Trying %s / %s", p["name"], model)
            if p["name"] in ("groq", "together"):
                result = _openai_call(p["url"], os.environ[p["key_env"]], messages, model)
            elif p["name"] == "ollama":
                result = _ollama_call(messages, model)
            elif p["name"] == "gemini":
                key = os.environ.get(p["key_env"], "")
                if not key:
                    continue
                result = _gemini_call(messages, model, key)
            else:
                continue
            result["_provider"] = p["name"]
            result["_model"] = model
            logger.info("Response from %s/%s", p["name"], model)
            return result
        except Exception as e:
            logger.warning("Provider %s failed: %s", p["name"], e)
            last_error = e
            time.sleep(0.3)
    return {"choices": [{"message": {"content": "All providers failed. Last: {}".format(last_error)}}]}


def _chunk_text(text, size=20):
    for i in range(0, len(text), size):
        yield text[i:i + size]


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages", [])
    model    = data.get("model", None)
    stream   = data.get("stream", False)
    if not messages:
        return jsonify({"error": "messages array is required"}), 400
    if not any(m.get("role") == "system" for m in messages):
        messages = [{"role": "system", "content": OSINT_SYSTEM_CONTEXT}] + messages
    result = route_query(messages, preferred_model=model)
    if stream:
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        def gen():
            for chunk in _chunk_text(content):
                yield "data: {}\n\n".format(json.dumps({"choices": [{"delta": {"content": chunk}}]}))
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(gen()), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})
    return jsonify({
        "id":       "chatcmpl-{}".format(hashlib.md5(str(time.time()).encode()).hexdigest()[:12]),
        "object":   "chat.completion",
        "created":  int(time.time()),
        "model":    result.get("_model", "unknown"),
        "provider": result.get("_provider", "unknown"),
        "choices":  result.get("choices", []),
    })


@app.route("/v1/models", methods=["GET"])
def list_models():
    models = []
    for p in _get_active_providers():
        for m in p["models"]:
            models.append({"id": m, "object": "model", "provider": p["name"], "free": p["free"]})
    return jsonify({"object": "list", "data": models})


@app.route("/health", methods=["GET"])
def health():
    providers = _get_active_providers()
    return jsonify({"status": "ok", "active_providers": [p["name"] for p in providers], "cloud_only": True, "free_inference": True})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service":    "OsintNeoAi Open-Source AI Gateway",
        "version":    "1.0.0",
        "endpoints":  {"chat": "POST /v1/chat/completions", "models": "GET /v1/models", "health": "GET /health"},
        "anythingllm": {"provider": "custom", "base_url": "http://<this-server>/v1", "api_key": "not-required"},
    })


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("GATEWAY_PORT", 11434)))
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    providers = _get_active_providers()
    logger.info("Starting gateway on %s:%s", args.host, args.port)
    logger.info("Active providers: %s", [p["name"] for p in providers])
    app.run(host=args.host, port=args.port, debug=False)
