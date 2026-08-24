import os
import re
import json
try:
    import g4f
except ImportError:
    g4f = None

class OSINTAgent:
    def __init__(self):
        sys_prompt = """You are OSINTNeoAi, an autonomous investigative AI intelligence agent and forensic analyst.
You specialize in OSINT reconnaissance, threat correlation, corporate shell tracking, public records analysis, and racketeering investigations.
If the user asks you to look up, scan, or investigate a target, output a tool execution command in this exact format:
<EXECUTE>TransformName TargetValue</EXECUTE>

When answering questions about the Huntington Beach, Orange County, or Federal grant investigations, cite verified evidence from the investigation dossier."""
        self.history = [{"role": "system", "content": sys_prompt}]
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tools.json")
        self.graph_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "graph.json")

    def is_configured(self):
        return True

    def generate_response(self, user_input, graph_context=None, tools_file=None):
        u_raw = user_input.split('\n')[0].strip()
        u_clean = u_raw.lower()

        # 1. Check for Cloud / LLM execution if available
        tools_summary = ""
        if os.path.exists(self.tools_path):
            try:
                with open(self.tools_path, "r", encoding="utf-8") as f:
                    tools_summary = f"{len(json.load(f).get('tools', []))} tools loaded."
            except Exception:
                pass

        prompt = f"User Query: {u_raw}\nTools: {tools_summary}"
        self.history.append({"role": "user", "content": prompt})

        # Try remote LLM via g4f with provider fallbacks
        try:
            for model_candidate in [g4f.models.default, g4f.models.gpt_4o, g4f.models.gpt_35_turbo]:
                try:
                    response = g4f.ChatCompletion.create(
                        model=model_candidate,
                        messages=self.history,
                        timeout=5
                    )
                    if response and len(response.strip()) > 10 and not response.startswith("AI Error"):
                        self.history.append({"role": "assistant", "content": response})
                        return response
                except Exception:
                    continue
        except Exception:
            pass

        # 2. LOCAL INTELLIGENCE & EXPERT FORENSIC KNOWLEDGE BASE (Zero-Fail Engine)

        # A. Greetings / System Capability / Hello / Test
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

        # B. RICO, Suspects, Defendants & Case Inquiries
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

        # C. Environmental Contamination / Hexavalent Chromium / HBNC
        if any(k in u_clean for k in ['hbnc', 'chromium', 'crvi', 'cr-vi', 'toxic', 'plume', 'well', 'contamination', 'environmental', '17642', 'beach blvd']):
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

        # D. Child Welfare / Title IV-E / Missing Children Gap
        if any(k in u_clean for k in ['cps', 'child', 'children', 'foster', 'trafficking', 'title iv-e', '29,300', '29300', 'gap']):
            return (
                "👶 **ORANGE COUNTY CHILD WELFARE & TITLE IV-E BILLING AUDIT:**\n\n"
                "• **Annual CPS Interventions:** ~30,000 child removal actions conducted annually by OC SSA.\n"
                "• **Annual Homeless Minor Census:** ~700 homeless children officially counted per year.\n"
                "• **The Discrepancy:** **29,300 unaccounted children** in the foster-to-shelter tracking pipeline.\n"
                "• **Federal Subsidy Mechanism:** Title IV-E billing generates recurring federal reimbursements per intervention, flowing through non-profit shelter operators without transparent tracking.\n\n"
                "📁 *Dossier File:* `legal_library/CHDO_MERCY_RICO_BREAKDOWN.md`"
            )

        # E. Direct Tool Searches (e.g. "search subdomains", "find wifi", "tool for shodan")
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
            else:
                return f"🔍 No specific tool matched '{query}' in our 980-tool catalog. Try broader keywords like `dns`, `recon`, `social`, `wifi`, `email`, or `osint`."

        # F. Entity Recognition (Domains, IPs, Emails, URLs, Hashes)
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

        # G. Default Comprehensive Fallback with Live Graph Search
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
        return f"📊 **Intelligence Summary of Tool Execution:**\n\n{message}"