import streamlit as st
import socket
import json
import re
from datetime import datetime
from utils.database import save_scan_result, get_all_scans, add_entity, add_event
from utils.api_clients import aggregate_ip_intel, aggregate_domain_intel, aggregate_phone_intel


def is_ip(target):
    try:
        socket.inet_aton(target)
        return True
    except Exception:
        return False

def is_domain(target):
    pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, target))

def is_phone(target):
    cleaned = re.sub(r"[\s\-\(\)\+]", "", target)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15

def scan_ip(ip):
    result = aggregate_ip_intel(ip)
    if result.get("sources"):
        return result
    # Fallback to local DNS
    result["hostname"] = "N/A"
    result["reverse_dns"] = "N/A"
    try:
        result["hostname"] = socket.gethostbyaddr(ip)[0]
        result["reverse_dns"] = result["hostname"]
    except Exception:
        pass
    try:
        result["local_resolve"] = socket.gethostbyname(ip)
    except Exception:
        pass
    return result

def scan_domain(domain):
    result = aggregate_domain_intel(domain)
    if result.get("sources"):
        return result
    return result

def scan_phone(phone):
    result = aggregate_phone_intel(phone)
    if result.get("sources"):
        return result
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    result["cleaned_number"] = cleaned
    result["country_code"] = cleaned[:1] if len(cleaned) >= 10 else "N/A"
    result["area_code"] = cleaned[:3] if len(cleaned) >= 10 else "N/A"
    result["carrier"] = "Unknown"
    result["line_type"] = "Unknown"
    return result

def render():
    st.markdown("## 🎯 Target Enumeration")
    st.markdown("Scan IP addresses, domains, phone numbers, and websites for deep OSINT data.")

    with st.form("scan_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            target_input = st.text_input("Enter Target", placeholder="e.g. 8.8.8.8 | google.com | +1-555-000-1234")
        with col2:
            scan_type = st.selectbox("Scan Type", ["Auto-Detect", "IP Address", "Domain", "Phone Number"])
        col_a, col_b = st.columns([1, 3])
        with col_a:
            save_to_master = st.checkbox("Save to Master Sheet", value=True)
        submitted = st.form_submit_button("🔍 Run Scan", use_container_width=True)

    if submitted and target_input.strip():
        target = target_input.strip()
        st.info(f"⚡ Scanning: **{target}** ...")

        with st.spinner("Enumerating target..."):
            detected = scan_type
            if scan_type == "Auto-Detect":
                if is_ip(target):
                    detected = "IP Address"
                elif is_phone(target):
                    detected = "Phone Number"
                elif is_domain(target):
                    detected = "Domain"
                else:
                    detected = "Unknown"

            st.markdown(f"**Detected as:** `{detected}`")

            if detected == "IP Address":
                result = scan_ip(target)
            elif detected == "Domain":
                result = scan_domain(target)
            elif detected == "Phone Number":
                result = scan_phone(target)
            else:
                result = {"target": target, "type": "Unknown", "note": "Could not auto-detect target type"}

        # Display results
        st.success("✅ Scan complete!")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("### 📋 Scan Results")
            for key, value in result.items():
                if key != "scanned_at":
                    st.markdown(f"**{key.replace('_', ' ').title()}:** `{value}`")

        with col_r2:
            st.markdown("### 🔷 Raw JSON")
            st.json(result)

        if save_to_master:
            save_scan_result(target, detected, result)
            # Also create an entity
            entity_id = f"ENT-SCAN-{int(datetime.now().timestamp())}"
            add_entity(entity_id, detected, target, "Scan Target", "", "Unknown", "Manual Scan", result.get("note", ""))
            add_event(
                f"EV-SCAN-{int(datetime.now().timestamp())}",
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                f"Scan: {detected}",
                result.get("city", result.get("country", "Unknown")),
                entity_id,
                "Manual Scan"
            )
            st.success("💾 Saved to master database!")

    # Scan history
    st.divider()
    st.markdown("### 📜 Scan History")
    scans = get_all_scans()
    if scans:
        df = []
        for s in scans:
            try:
                r = json.loads(s.get("result_json", "{}"))
                df.append({
                    "Target": s["target"],
                    "Type": s["scan_type"],
                    "Result Summary": r.get("note", str(list(r.values())[:2])),
                    "Scanned At": s["created_at"],
                })
            except Exception:
                pass
        if df:
            import pandas as pd
            st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
    else:
        st.info("No scans yet. Run your first scan above.")
