import streamlit as st
import pandas as pd
import os
from utils.database import (
    get_all_entities, get_all_relationships, get_all_events,
    get_all_scans, get_all_file_scans, add_entity, add_relationship, add_event
)
from utils.excel_gen import generate_master_sheet, MASTER_PATH
from utils.maltego_export import build_mtgx
from datetime import datetime

def render():
    st.markdown("## 📊 OSINT Master Intelligence Sheet")
    st.markdown("All collected intelligence data in one place. Add, view, and export records.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Entities", "🔗 Relationships", "📅 Events", "📁 File Scans", "📤 Export"])

    # ── ENTITIES ──
    with tab1:
        entities = get_all_entities()
        st.markdown(f"### Entities ({len(entities)} records)")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            type_filter = st.selectbox("Filter by Type", ["All", "Person", "Location", "Organization", "Legal", "Document", "Vehicle", "Device", "IP", "Domain", "Phone", "Other"])
        with col_f2:
            risk_filter = st.selectbox("Filter by Risk", ["All", "High", "Medium", "Low", "Unknown"])

        df = pd.DataFrame(entities)
        if not df.empty:
            if type_filter != "All":
                df = df[df["type"] == type_filter]
            if risk_filter != "All":
                df = df[df["risk_level"] == risk_filter]

            def color_risk(val):
                colors = {"High": "background-color: #C0392B; color: white",
                          "Medium": "background-color: #D68910; color: white",
                          "Low": "background-color: #1E8449; color: white"}
                return colors.get(val, "")

            display_cols = ["entity_id", "type", "label", "category", "geo_location", "risk_level", "source", "notes"]
            df_display = df[[c for c in display_cols if c in df.columns]].copy()
            df_display.columns = ["Entity ID", "Type", "Label", "Category", "Geo Location", "Risk", "Source", "Notes"][:len(df_display.columns)]
            styled = df_display.style.applymap(color_risk, subset=["Risk"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### ➕ Add New Entity")
        with st.expander("Add Entity", expanded=False):
            with st.form("add_entity_form"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    eid = st.text_input("Entity ID", value=f"ENT-{int(datetime.now().timestamp())}")
                    etype = st.selectbox("Type", ["Person", "Location", "Vehicle", "Device", "Object", "Organization", "Legal", "IP", "Domain", "Phone"])
                with c2:
                    label = st.text_input("Label / Name")
                    category = st.text_input("Category")
                with c3:
                    geo = st.text_input("Geo Location / Address")
                    risk = st.selectbox("Risk Level", ["Unknown", "Low", "Medium", "High"])
                source = st.text_input("Source")
                notes = st.text_area("Notes", height=80)
                if st.form_submit_button("Add Entity"):
                    if label:
                        add_entity(eid, etype, label, category, geo, risk, source, notes)
                        st.success(f"Entity '{label}' added!")
                        st.rerun()
                    else:
                        st.error("Label is required.")

    # ── RELATIONSHIPS ──
    with tab2:
        relationships = get_all_relationships()
        st.markdown(f"### Relationships ({len(relationships)} records)")
        if relationships:
            df_rel = pd.DataFrame(relationships)
            display_cols = ["relation_id", "source_entity", "target_entity", "relationship_type", "confidence", "source"]
            df_rel = df_rel[[c for c in display_cols if c in df_rel.columns]]
            df_rel.columns = ["Relation ID", "Source Entity", "Target Entity", "Type", "Confidence", "Intel Source"][:len(df_rel.columns)]
            st.dataframe(df_rel, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### ➕ Add New Relationship")
        with st.expander("Add Relationship", expanded=False):
            with st.form("add_rel_form"):
                c1, c2 = st.columns(2)
                with c1:
                    rid = st.text_input("Relation ID", value=f"REL-{int(datetime.now().timestamp())}")
                    src = st.text_input("Source Entity (ID or Name)")
                    tgt = st.text_input("Target Entity (ID or Name)")
                with c2:
                    rel_type = st.selectbox("Relationship Type", [
                        "Located_At", "Resides_At", "Employment", "Business Owner",
                        "Officer", "Shared_Address", "Associated_With", "Family", "Friend",
                        "Suspect", "Plaintiff_vs", "Subject_Of", "Party_In", "Witness_In",
                        "Legal_Dispute", "Filed"
                    ])
                    confidence = st.selectbox("Confidence", ["High", "Medium", "Low"])
                    source = st.text_input("Source")
                if st.form_submit_button("Add Relationship"):
                    if src and tgt:
                        add_relationship(rid, src, tgt, rel_type, confidence, source)
                        st.success("Relationship added!")
                        st.rerun()
                    else:
                        st.error("Source and Target are required.")

    # ── EVENTS ──
    with tab3:
        events = get_all_events()
        st.markdown(f"### Events / Timeline ({len(events)} records)")
        if events:
            df_ev = pd.DataFrame(events)
            display_cols = ["event_id", "timestamp", "event_type", "location", "entities_involved", "source"]
            df_ev = df_ev[[c for c in display_cols if c in df_ev.columns]]
            df_ev.columns = ["Event ID", "Date/Time", "Type", "Location", "Entities", "Source"][:len(df_ev.columns)]
            st.dataframe(df_ev, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### ➕ Add New Event")
        with st.expander("Add Event", expanded=False):
            with st.form("add_event_form"):
                c1, c2 = st.columns(2)
                with c1:
                    evid = st.text_input("Event ID", value=f"EV-{int(datetime.now().timestamp())}")
                    timestamp = st.text_input("Date/Timestamp", value=datetime.now().strftime("%Y-%m-%d"))
                    event_type = st.selectbox("Event Type", [
                        "Criminal Offense", "Bankruptcy", "Tax Lien", "Signal_Loss",
                        "Ex Parte Filing", "Court Hearing", "Evidence Compiled",
                        "Phone Scan", "Data Breach", "Arrest", "Financial Transaction",
                        "Travel", "Social Media Post", "Other"
                    ])
                with c2:
                    location = st.text_input("Location")
                    entities = st.text_input("Entities Involved (IDs or Names)")
                    source = st.text_input("Source")
                if st.form_submit_button("Add Event"):
                    if event_type:
                        add_event(evid, timestamp, event_type, location, entities, source)
                        st.success("Event added!")
                        st.rerun()
                    else:
                        st.error("Event type is required.")

    # ── FILE SCANS ──
    with tab4:
        import sqlite3, json
        conn = sqlite3.connect('data/osint_master.db')
        rows = conn.execute('''SELECT
            file_name, file_type, category, folder, risk_flag,
            names_found, orgs_found, emails_found, phones_found,
            addresses_found, case_numbers, keywords_hit,
            gps_lat, gps_lon, gps_location,
            camera_make, camera_model,
            audio_artist, audio_title, audio_duration,
            content_preview, md5_hash, created_at
            FROM file_scan_results ORDER BY risk_flag DESC, file_name''').fetchall()
        conn.close()

        cols = ["File Name","Type","Category","Folder","Risk",
                "Names Found","Orgs Found","Emails","Phones",
                "Addresses","Case Numbers","Keywords Hit",
                "GPS Lat","GPS Lon","GPS Location",
                "Camera Make","Camera Model",
                "Audio Artist","Audio Title","Duration",
                "Content Preview","MD5","Scanned At"]

        df_fs = pd.DataFrame(rows, columns=cols)
        total = len(df_fs)
        high  = len(df_fs[df_fs["Risk"] == "High"])
        med   = len(df_fs[df_fs["Risk"] == "Medium"])
        named = df_fs["Names Found"].notna().sum()
        orged = df_fs["Orgs Found"].notna().sum()

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Files", total)
        m2.metric("🔴 High Risk", high)
        m3.metric("🟡 Medium Risk", med)
        m4.metric("👤 Names Found", named)
        m5.metric("🏢 Orgs Found", orged)

        st.divider()

        risk_f = st.selectbox("Filter by Risk", ["All", "High", "Medium", "Low"], key="fs_risk")
        type_f = st.selectbox("Filter by Type", ["All"] + sorted(df_fs["Type"].dropna().unique().tolist()), key="fs_type")
        search_f = st.text_input("🔍 Search file names / keywords", key="fs_search")

        df_view = df_fs.copy()
        if risk_f != "All":
            df_view = df_view[df_view["Risk"] == risk_f]
        if type_f != "All":
            df_view = df_view[df_view["Type"] == type_f]
        if search_f:
            mask = df_view.apply(lambda r: r.astype(str).str.contains(search_f, case=False).any(), axis=1)
            df_view = df_view[mask]

        def color_risk_fs(val):
            colors = {"High": "background-color: #C0392B; color: white",
                      "Medium": "background-color: #D68910; color: white",
                      "Low": "background-color: #1E8449; color: white"}
            return colors.get(val, "")

        st.markdown(f"**Showing {len(df_view)} of {total} files**")
        core_cols = ["File Name","Type","Category","Risk","Names Found","Orgs Found","Case Numbers","Keywords Hit","Content Preview"]
        styled_fs = df_view[core_cols].style.applymap(color_risk_fs, subset=["Risk"])
        st.dataframe(styled_fs, use_container_width=True, hide_index=True)

        with st.expander("📍 Show GPS / EXIF / Audio columns"):
            extra_cols = ["File Name","GPS Lat","GPS Lon","GPS Location","Camera Make","Camera Model","Audio Artist","Audio Title","MD5"]
            st.dataframe(df_view[extra_cols], use_container_width=True, hide_index=True)

    # ── EXPORT ──
    with tab5:
        st.markdown("### 📤 Export Master Intelligence Sheet")
        st.markdown("Generate and download your intelligence data in multiple formats.")

        entities_data = get_all_entities()
        rels_data     = get_all_relationships()
        events_data   = get_all_events()
        file_scans    = get_all_file_scans()
        scans         = get_all_scans()

        # ── Excel export ──────────────────────────────────────────────────────
        st.markdown("#### 📊 Excel Master Sheet")
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("""
            **Includes:**
            - 📊 Summary overview
            - 🎯 All entities with risk coloring
            - 🔗 All relationships
            - 📅 Events timeline
            - 📁 File scan results (23 attribute columns)
            - 🔍 Target scan history
            """)
        with col_e2:
            if st.button("🔄 Generate Master Sheet Now", use_container_width=True):
                with st.spinner("Generating Excel master sheet..."):
                    generate_master_sheet(entities_data, rels_data, events_data, file_scans, scans)
                st.success("✅ Master sheet generated!")

            if os.path.exists(MASTER_PATH):
                file_size = os.path.getsize(MASTER_PATH)
                modified  = datetime.fromtimestamp(os.path.getmtime(MASTER_PATH)).strftime("%Y-%m-%d %H:%M:%S")
                st.info(f"📄 Last generated: {modified} ({file_size:,} bytes)")
                with open(MASTER_PATH, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Master Sheet (.xlsx)",
                        data=f,
                        file_name=f"OSINT_Master_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
            else:
                st.warning("No master sheet generated yet. Click 'Generate' above.")

        st.divider()

        # ── Maltego export ────────────────────────────────────────────────────
        st.markdown("#### 🕵️ Maltego Graph Exchange (.mtgx)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("""
            **Opens directly in Maltego CE / Pro / Enterprise.**

            Exports all entities as native Maltego entity types:

            | OSINT Type | Maltego Entity |
            |---|---|
            | Person | `maltego.Person` |
            | Email | `maltego.EmailAddress` |
            | Organization | `maltego.Organization` |
            | Location | `maltego.Location` |
            | IP | `maltego.IPv4Address` |
            | Domain | `maltego.Domain` |
            | Phone | `maltego.PhoneNumber` |
            | Document | `maltego.Document` |

            Relationships become directed edges with confidence weights.
            Risk level is color-coded:
            🔴 High · 🟠 Medium · 🟢 Low
            """)
        with col_m2:
            st.markdown(f"**{len(entities_data)} entities · {len(rels_data)} relationships** ready to export.")

            # Filter options
            maltego_risk_filter = st.multiselect(
                "Include risk levels",
                ["High", "Medium", "Low", "Unknown"],
                default=["High", "Medium", "Low", "Unknown"],
                key="maltego_risk_filter",
            )
            maltego_type_filter = st.multiselect(
                "Include entity types",
                ["Person", "Email", "Organization", "Location", "IP", "Domain", "Phone", "Document", "Legal", "Vehicle", "Device"],
                default=["Person", "Email", "Organization", "Location", "IP", "Domain", "Phone", "Document", "Legal"],
                key="maltego_type_filter",
            )

            filtered_ents = [
                e for e in entities_data
                if e.get("risk_level", "Unknown") in maltego_risk_filter
                and e.get("type", "Other") in maltego_type_filter
            ]
            filtered_ids = {e["entity_id"] for e in filtered_ents}
            filtered_labels = {e["label"] for e in filtered_ents}
            filtered_rels = [
                r for r in rels_data
                if r.get("source_entity") in filtered_ids | filtered_labels
                or r.get("target_entity") in filtered_ids | filtered_labels
            ]

            st.caption(f"Filtered: {len(filtered_ents)} entities · {len(filtered_rels)} relationships")

            if st.button("⚡ Build Maltego Export", use_container_width=True, key="maltego_build"):
                with st.spinner("Building .mtgx graph…"):
                    mtgx_bytes = build_mtgx(filtered_ents, filtered_rels)
                fname = f"OSINT_Neo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mtgx"
                st.download_button(
                    label="⬇️ Download .mtgx for Maltego",
                    data=mtgx_bytes,
                    file_name=fname,
                    mime="application/zip",
                    use_container_width=True,
                    key="maltego_download",
                )
                st.success(f"✅ {len(filtered_ents)} entities and {len(filtered_rels)} relationships exported. "
                           f"Open in Maltego: **File → Import → Import Graph**")
