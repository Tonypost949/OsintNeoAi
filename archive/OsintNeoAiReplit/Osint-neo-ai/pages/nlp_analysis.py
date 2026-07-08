import streamlit as st
import pandas as pd
import re
from datetime import datetime
from utils.database import add_entity, add_event
from utils.api_clients import google_nlp_analyze

# Simple rule-based NLP (no heavy model needed)
ENTITY_PATTERNS = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE": r"(\+?1?\s?)?(\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})",
    "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "URL": r"https?://[^\s<>\"]+|www\.[^\s<>\"]+",
    "DATE": r"\b(?:\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
    "MONEY": r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "ZIP_CODE": r"\b\d{5}(?:-\d{4})?\b",
    "CASE_NUMBER": r"\b(?:case|docket|filing)[\s#:]+[\w\-]+\b",
}

KEYWORD_CATEGORIES = {
    "PERSON": ["mr.", "mrs.", "ms.", "dr.", "prof.", "sir", "ma'am"],
    "LEGAL": ["court", "judge", "attorney", "defendant", "plaintiff", "verdict", "sentence", "arrest", "warrant", "indictment"],
    "FINANCIAL": ["bank", "account", "wire", "transfer", "loan", "debt", "bankruptcy", "lien", "credit", "fraud"],
    "THREAT": ["threat", "weapon", "attack", "breach", "hack", "exploit", "malware", "ransomware", "phishing"],
    "LOCATION_KEYWORDS": ["street", "ave", "blvd", "drive", "road", "lane", "city", "county", "state"],
}

def extract_entities(text):
    found = []
    for etype, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            val = match if isinstance(match, str) else match[0]
            if val.strip():
                found.append({"Type": etype, "Value": val.strip(), "Confidence": "High"})

    # Keyword-based detection
    text_lower = text.lower()
    for category, keywords in KEYWORD_CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                found.append({"Type": category, "Value": kw.title(), "Confidence": "Medium"})

    # Simple capitalized word detection (potential proper nouns)
    words = text.split()
    for i, word in enumerate(words):
        clean = re.sub(r"[^\w]", "", word)
        if clean and clean[0].isupper() and len(clean) > 2 and not clean.isupper():
            if i > 0 and not words[i-1].endswith("."):
                found.append({"Type": "PROPER_NOUN", "Value": clean, "Confidence": "Low"})

    # Deduplicate
    seen = set()
    unique = []
    for item in found:
        key = (item["Type"], item["Value"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique

def render():
    st.markdown("## 🧠 NLP Intelligence Analysis")
    st.markdown("Extract entities, patterns, and intelligence from unstructured text in 40+ languages.")

    col_input, col_opts = st.columns([2, 1])
    with col_input:
        text_input = st.text_area(
            "Enter unstructured text for analysis",
            height=250,
            placeholder="Paste any text: court documents, social media posts, emails, reports, etc.\n\nExample:\nJohn Smith (DOB: 03/15/1985) was arrested on 2023-11-13 in Orange, CA.\nContact: john.smith@email.com | Phone: (555) 123-4567\nCase #: CR-2023-4892 | Federal Tax Lien #156608 filed 2016-03-31"
        )

    with col_opts:
        st.markdown("#### Analysis Options")
        detect_emails = st.checkbox("Detect Emails", value=True)
        detect_phones = st.checkbox("Detect Phones", value=True)
        detect_ips = st.checkbox("Detect IPs/URLs", value=True)
        detect_dates = st.checkbox("Detect Dates", value=True)
        detect_money = st.checkbox("Detect Financial", value=True)
        save_to_db = st.checkbox("Save findings to master", value=True)

    if st.button("🔍 Analyze Text", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Running entity extraction..."):
                entities = extract_entities(text_input)

                # Try Google NLP if key available
                google_result = google_nlp_analyze(text_input)
                if google_result and "error" not in google_result and "entities" in google_result:
                    for g in google_result["entities"]:
                        entities.append({
                            "Type": f"GOOGLE_{g['type']}",
                            "Value": g["name"],
                            "Confidence": f"{round(g.get('salience', 0) * 100)}%",
                            "source": "google_nlp",
                        })
                    st.info(f"Google NLP detected {len(google_result['entities'])} additional entities")

                # Filter based on options
                filtered = []
                for ent in entities:
                    if not detect_emails and ent["Type"] == "EMAIL":
                        continue
                    if not detect_phones and ent["Type"] == "PHONE":
                        continue
                    if not detect_ips and ent["Type"] in ["IP_ADDRESS", "URL"]:
                        continue
                    if not detect_dates and ent["Type"] == "DATE":
                        continue
                    if not detect_money and ent["Type"] == "MONEY":
                        continue
                    filtered.append(ent)

            st.success(f"✅ Found {len(filtered)} entities in the text")

            # Stats
            if filtered:
                col1, col2, col3 = st.columns(3)
                df = pd.DataFrame(filtered)
                high = len(df[df["Confidence"] == "High"])
                med = len(df[df["Confidence"] == "Medium"])
                col1.metric("High Confidence", high)
                col2.metric("Medium Confidence", med)
                col3.metric("Total Entity Types", df["Type"].nunique())

                st.divider()
                col_table, col_types = st.columns([2, 1])
                with col_table:
                    st.markdown("#### 🔷 Extracted Entities")

                    def color_conf(val):
                        if val == "High":
                            return "background-color: #1E8449; color: white"
                        elif val == "Medium":
                            return "background-color: #D68910; color: white"
                        return ""

                    styled = df.style.applymap(color_conf, subset=["Confidence"])
                    st.dataframe(styled, use_container_width=True, hide_index=True)

                with col_types:
                    st.markdown("#### 📊 By Type")
                    type_counts = df["Type"].value_counts().reset_index()
                    type_counts.columns = ["Type", "Count"]
                    st.dataframe(type_counts, use_container_width=True, hide_index=True)

                # Highlighted text
                st.divider()
                st.markdown("#### 📝 Text with Highlights")
                highlighted = text_input
                for _, row in df.iterrows():
                    if row["Confidence"] == "High":
                        highlighted = highlighted.replace(
                            row["Value"],
                            f"**:blue[{row['Value']}]**"
                        )
                st.markdown(highlighted)

                if save_to_db:
                    ts = int(datetime.now().timestamp())
                    for i, row in df.iterrows():
                        if row["Confidence"] == "High":
                            eid = f"ENT-NLP-{ts}-{i}"
                            add_entity(eid, row["Type"], row["Value"], "NLP Extract", "", "Unknown", "NLP Analysis", f"Confidence: {row['Confidence']}")
                    add_event(
                        f"EV-NLP-{ts}", datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "NLP Analysis", "Unknown", f"{high} high-confidence entities", "NLP Analysis"
                    )
                    st.success(f"💾 Saved {high} high-confidence entities to master database!")
            else:
                st.info("No entities detected. Try more specific text with names, dates, or contact info.")

    # Language reference
    with st.expander("ℹ️ Supported Entity Types & Languages"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            **Detected Entity Types:**
            - EMAIL — email addresses
            - PHONE — phone numbers
            - IP_ADDRESS — IPv4 addresses
            - URL — web addresses
            - DATE — dates and timestamps
            - MONEY — financial amounts
            - SSN — Social Security Numbers
            - ZIP_CODE — postal codes
            - CASE_NUMBER — legal case references
            - PROPER_NOUN — capitalized names/places
            - LEGAL — legal terminology
            - FINANCIAL — financial terms
            - THREAT — cybersecurity/threat terms
            """)
        with col_b:
            st.markdown("""
            **Language Support:**
            Pattern-based extraction works across all Latin-script languages.

            For full multilingual NLP (Arabic, Chinese, Russian, etc.) integrate:
            - **spaCy** with `xx_ent_wiki_sm` model
            - **Hugging Face** multilingual NER
            - **Google NLP API**
            - **AWS Comprehend**

            These can be enabled in Settings with an API key.
            """)
