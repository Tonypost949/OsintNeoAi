"""RICOCorrelationAgent: Deep semantic reasoning with Gemini AI and rule-based predicate detection."""

import os
import re
import json
from typing import List, Dict, Any, Optional
from AiRiCOSwarm.config.swarm_config import RICO_PREDICATE_KEYWORDS

class RICOCorrelationAgent:
    def __init__(self):
        self.keywords = [kw.lower() for kw in RICO_PREDICATE_KEYWORDS]
        self.ai_client = None
        self._init_ai()

    def _init_ai(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                self.ai_client = genai.Client(api_key=api_key)
                print("[CORRELATION] Gemini AI Generative Client enabled.")
            except Exception as e:
                print(f"[CORRELATION] AI init fallback to rule-based: {e}")
        else:
            print("[CORRELATION] Running in deterministic rule-based predicate mode.")

    def scan_for_predicates(self, text: str) -> List[str]:
        findings = []
        lower_text = text.lower()
        for kw in self.keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower_text):
                findings.append(kw)
        return list(set(findings))

    def synthesize_findings_with_ai(self, target_name: str, findings: List[Dict[str, Any]]) -> str:
        if not self.ai_client or not findings:
            return f"Deterministic Summary: Detected {len(findings)} predicate-linked evidence records for target {target_name}."

        sample_context = json.dumps(findings[:25], default=str)
        prompt = (
            f"You are a Senior RICO & False Claims Act Forensic Analyst.\n"
            f"Analyze the following evidence records for Target: '{target_name}'.\n"
            f"Identify potential predicate patterns (e.g. wire fraud, grant diversion, shell entity manipulation, kickbacks).\n"
            f"Provide a concise, 3-paragraph executive intelligence analysis with specific risk indicators.\n\n"
            f"Evidence Records:\n{sample_context}"
        )
        try:
            response = self.ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Deterministic Summary: {len(findings)} records flagged. (AI synthesis error: {e})"
