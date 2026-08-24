import os
import re
import json
import requests

class OSINTAgent:
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tools.json")
        self.graph_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "graph.json")

        self.gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY")

        sys_prompt = """You are OSINTNeoAi, an elite autonomous investigative AI coding assistant, threat analyst, and forensic intelligence agent.
You have access to 980+ cataloged OSINT and Kali Linux tools, a 2,207-node GraphDB, Google BigQuery, and Maltego reconnaissance transforms.

CAPABILITIES:
1. Vibe Coding & Script Generation: You can generate complete, runnable Python, Bash, SQL, or HTML/JS tools and geospatial visualizations.
2. Investigation & RICO Analysis: You analyze complex shell companies, grant fraud pipelines, corporate registries, and toxic environmental plumes (HBNC 49x CrVI).
3. Tool Execution: When the user asks you to scan, resolve, or execute reconnaissance on a target, you output executable commands:
   <EXECUTE>TransformName TargetValue</EXECUTE>
   Available Transforms: DomainToIP, IPToShodanInfo, EmailToSocialProfile, etc.
4. Geospatial Synthesis: You can format and synthesize coordinates and entities for Leaflet, QGIS, and ArcGIS.

Always give deep, helpful, highly intelligent, and direct responses."""
        self.history = []
        self.system_prompt = sys_prompt

    def is_configured(self):
        return True

    def _call_gemini(self, user_input, context=""):
        if not self.gemini_key:
            return None
        
        models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-pro-latest"]
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
                
                # Build contents array from history
                contents = []
                # Add system context
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"[SYSTEM INSTRUCTION]\n{self.system_prompt}\n\n[CONTEXT DATA]\n{context}"}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Understood. I am OSINTNeoAi, ready to investigate, vibe code, analyze, and dispatch reconnaissance pipelines."}]
                })

                for msg in self.history[-6:]:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})

                contents.append({"role": "user", "parts": [{"text": user_input}]})

                payload = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2048
                    }
                }

                r = requests.post(url, json=payload, timeout=15)
                if r.status_code == 200:
                    res_data = r.json()
                    text = res_data['candidates'][0]['content']['parts'][0]['text']
                    return text.strip()
            except Exception:
                continue
        return None

    def _call_groq(self, user_input):
        if not self.groq_key:
            return None
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": self.system_prompt}] + self.history[-6:] + [{"role": "user", "content": user_input}]
            payload = {"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.7}
            r = requests.post(url, json=payload, headers=headers, timeout=12)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content'].strip()
        except Exception:
            pass
        return None

    def _call_openai(self, user_input):
        if not self.openai_key:
            return None
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            messages = [{"role": "system", "content": self.system_prompt}] + self.history[-6:] + [{"role": "user", "content": user_input}]
            payload = {"model": "gpt-4o", "messages": messages, "temperature": 0.7}
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content'].strip()
        except Exception:
            pass
        return None

    def generate_response(self, user_input, graph_context=None, tools_file=None):
        u_raw = user_input.split('\n')[0].strip()
        u_clean = u_raw.lower()

        # Build context from tools and graph
        tools_summary = ""
        if os.path.exists(self.tools_path):
            try:
                with open(self.tools_path, "r", encoding="utf-8") as f:
                    t_count = len(json.load(f).get("tools", []))
                    tools_summary = f"Tools Available: {t_count} (across 49 OSINT & Kali categories)."
            except Exception:
                pass

        graph_summary = ""
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, "r", encoding="utf-8") as f:
                    g_data = json.load(f)
                    graph_summary = f"GraphDB State: {len(g_data.get('nodes', []))} nodes, {len(g_data.get('edges', []))} edges."
            except Exception:
                pass

        full_context = f"{tools_summary} | {graph_summary}"

        # 1. Primary AI Model Execution (Gemini 3.6 Flash / Groq / OpenAI)
        llm_response = (
            self._call_gemini(user_input, full_context) or
            self._call_groq(user_input) or
            self._call_openai(user_input)
        )

        if llm_response:
            self.history.append({"role": "user", "content": u_raw})
            self.history.append({"role": "assistant", "content": llm_response})
            return llm_response

        # 2. LOCAL INTELLIGENCE & FORENSIC KNOWLEDGE BASE (Deterministic Fallback)
        self.history.append({"role": "user", "content": u_raw})

        # Greetings
        if u_clean in ['hello', 'hi', 'hey', 'test', 'who are you', 'what can you do', 'status', 'ready']:
            return (
                "👋 **OSINTNeoAi Core Intelligence Engine Online.**\n\n"
                "I am your autonomous investigative assistant. I can query our **2,207-node GraphDB**, search across **980+ cataloged OSINT/Kali tools**, cross-reference **Federal RICO evidence dossiers**, and dispatch live recon transforms.\n\n"
                "**Quick capabilities you can try right now:**\n"
                "• Ask: `who are the rico suspects?` or `explain the three pipelines`\n"
                "• Search tools: `search metadata` or `tools search subdomains`\n"
                "• Run recon: `transform DomainToIP huntingtonbeachca.gov`\n"
                "• Check statutes: `legal` or `retaliation`\n"
                "• Public Board: `board`"
            )

        # RICO / Suspects / Pipelines
        if any(k in u_clean for k in ['rico', 'suspect', 'defendant', 'perpetrator', 'target', 'enterprise', 'who is involved', 'key players']):
            return (
                "🏛️ **PRIMARY RICO ENTERPRISE TARGETS & DEFENDANTS (Verified Forensic Dossier):**\n\n"
                "1. **Municipal & Enforcement Hub (City of HB / OCSD):**\n"
                "   • **City of Huntington Beach / OCHCA:** Facilitated fraudulent site certification (20IC002) concealing **49x Hexavalent Chromium (490 ppb)** over unsealed 1947 artesian well.\n"
                "   • **Orange County Sheriff's Dept (OCSD):** Coordinated retaliatory August 4, 2021 lockout at 212 Southbrook after formal Internal Affairs filing.\n"
                "   • **Officials Documented:** Jim Merid (City of HB), Tamera Escobedo (OCHCA), David Bernier (EEC), Anthony Martinez (OCHCA).\n\n"
                "2. **Property & Shell Company Network ($3.1B PPP Pipeline):**\n"
                "   • **Stewart Industries LLC:** $1.13M PPP loan (34 days prior to acquisition via 1077 PCH mailbox).\n"
                "   • **Triumvirate LLC:** $1.47M PPP loan (Anchorage AK shell linked to local acquisitions).\n"
                "   • **Lido House LLC:** $3.9M PPP loan (3300 Newport Blvd entity).\n"
                "   • **Shea Properties / Shea Homes:** Management entity involved in 212 Southbrook retaliatory eviction.\n\n"
                "3. **Grant Diversion & Vendor Self-Dealing Network:**\n"
                "   • **Mercy House Living Centers:** $54.5M annual revenue; board self-dealing to affiliated vendors receiving $6.49M in PPP funds (Buntich, RBA Builders, Shopoff Realty).\n"
                "   • **Viet America Society (VAS) / Hand-to-Hand:** $13.5M COVID grant diversion (Peter Anh Pham fugitive; Andrew Do convicted).\n"
                "   • **Paul Richard Randall / Monte Vista Pharmacy:** $178.7M Medi-Cal fraud scheme.\n"
                "   • **Marcus S. Angulo (NPI 1124486568):** CalAIM credential harvesting.\n\n"
                "📁 *Full Legal Referral:* `legal_library/CRIMINAL_REFERRAL_FINAL.md`"
            )

        # Environmental / HBNC
        if any(k in u_clean for k in ['hbnc', 'chromium', 'crvi', 'cr-vi', 'toxic', 'plume', 'well', 'contamination', 'environmental']):
            return (
                "☣️ **HBNC ENVIRONMENTAL CONTAMINATION & FRAUD DOSSIER:**\n\n"
                "• **Site Footprint:** 17642 Beach Blvd & 17631 Cameron Ln, Huntington Beach, CA.\n"
                "• **Contaminant Concentration:** **Hexavalent Chromium (Cr-VI) at 490 ppb** — **49 times the EPA safe drinking water limit of 10 ppb**.\n"
                "• **GeoTracker Record:** Global ID `T10000018579` (CA State Water Board).\n"
                "• **The Conduit:** Unsealed 1947 agricultural artesian well creating a chimney effect beneath the homeless shelter.\n"
                "• **Fraudulent Exemption:** City expedited construction via CEQA Class 1 Exemption (Existing Facilities) despite knowing adjacent G&M Oil #124 and subsurface plume data.\n"
                "• **Human Impact:** High-pressure floor sprayers actively aerosolized heavy metal particulates breathed by unhoused residents and staff.\n\n"
                "📁 *Dossier File:* `legal_library/EPA_OIG_RUBICON_REFERRAL.md`"
            )

        # Direct Tool Search
        if u_clean.startswith(('search ', 'find ', 'tools search ', 'tool search ', 'tools for ', 'tool for ')) or 'search' in u_clean:
            query = re.sub(r'^(?:tools?\s+)?(?:search|find|for)\s+', '', u_raw, flags=re.IGNORECASE).strip().lower()
            if not query or query == 'tools':
                query = u_clean
            
            matches = []
            if os.path.exists(self.tools_path):
                try:
                    with open(self.tools_path, "r", encoding="utf-8") as f:
                        all_tools = json.load(f).get("tools", [])
                        matches = [
                            t for t in all_tools
                            if query in t.get("name", "").lower()
                            or query in t.get("description", "").lower()
                            or query in t.get("category", "").lower()
                        ]
                except Exception:
                    pass

            if matches:
                out = [f"🔍 **Found {len(matches)} Tools Matching '{query}':**\n"]
                for m in matches[:12]:
                    desc = f" — {m.get('description')}" if m.get('description') else ""
                    out.append(f"• **{m.get('name')}** `[{m.get('category')}]`{desc}\n  🔗 {m.get('url')}")
                if len(matches) > 12:
                    out.append(f"\n*(... and {len(matches) - 12} more tools. Use 'tools search {query}' to see all)*")
                return "\n".join(out)

        # Entity Recognition
        domain_match = re.search(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', u_raw)
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', u_raw)
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', u_raw)

        if email_match:
            em = email_match.group(0)
            return f"🎯 **Identified Target Email:** `{em}`\nDispatching social identity footprinting:\n<EXECUTE>EmailToSocialProfile {em}</EXECUTE>"
        elif ip_match:
            ip = ip_match.group(0)
            return f"🎯 **Identified Target IP:** `{ip}`\nDispatching Shodan port & infrastructure scan:\n<EXECUTE>IPToShodanInfo {ip}</EXECUTE>"
        elif domain_match and not u_raw.startswith("http"):
            d = domain_match.group(0)
            return f"🎯 **Identified Target Domain:** `{d}`\nDispatching DNS & IP infrastructure resolution:\n<EXECUTE>DomainToIP {d}</EXECUTE>"

        # Graph Search Fallback
        matched_nodes = []
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, "r", encoding="utf-8") as f:
                    g_nodes = json.load(f).get("nodes", [])
                    matched_nodes = [n for n in g_nodes if u_clean in str(n.get("value", "")).lower()]
            except Exception:
                pass

        if matched_nodes:
            out = [f"📊 **GraphDB Cross-Reference Results for '{u_raw}' ({len(matched_nodes)} matching entities):**\n"]
            for mn in matched_nodes[:10]:
                out.append(f"• `[{mn.get('type')}]` **{mn.get('value')}** (ID: `{mn.get('id')[:8]}...`)")
            return "\n".join(out)

        return (
            f"🧠 **OSINTNeoAi Query Processor:** `{u_raw}`\n\n"
            "• **To search tools:** Type `search <keyword>` (e.g. `search email`)\n"
            "• **To investigate a target:** Type `investigate maltego.Domain example.com`\n"
            "• **To run transforms:** Type `transform DomainToIP example.com`\n"
            "• **To explore RICO evidence:** Type `rico suspects` or `explain the three pipelines`\n"
            "• **To view active victims board:** Type `board`"
        )

    def send_system_message(self, message):
        self.history.append({"role": "user", "content": f"[SYSTEM TOOL RESULT]\n{message}\nAnalyze and summarize the above results for the user."})
        llm_res = self._call_gemini(f"[SYSTEM TOOL RESULT]\n{message}\nAnalyze and summarize the above results for the user.")
        if llm_res:
            return llm_res
        return f"📊 **Intelligence Summary of Tool Execution:**\n\n{message}"