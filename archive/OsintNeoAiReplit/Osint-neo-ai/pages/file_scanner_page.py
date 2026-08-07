import streamlit as st
import pandas as pd
import os
import json
import tempfile
from datetime import datetime
from utils.file_scanner import scan_directory, get_directory_summary, scan_file, SUPPORTED_EXTENSIONS
from utils.database import save_file_scan, get_all_file_scans


def render():
    st.markdown("## 📁 Local File & Folder Scanner")
    st.markdown("Scan files and folders to extract metadata, GPS data, contacts, and more.")

    tab1, tab2 = st.tabs(["🔍 Scan", "📋 Scan History"])

    with tab1:
        # ── Mode selector ──
        st.markdown("### How do you want to scan?")
        scan_mode = st.radio(
            "Choose scan mode",
            options=["📂 Upload Files / Folder", "📁 Scan Local Folder"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.divider()

        if scan_mode == "📂 Upload Files / Folder":
            # ── Upload-based scanning (works on any device) ──
            st.markdown("### Upload Files or Folder")

            st.markdown("""
            <div style="background:#0f1628;border:1px solid #1e2d50;border-radius:8px;padding:14px;margin-bottom:12px;">
                <p style="color:#00d4ff;font-weight:bold;margin:0 0 8px 0;font-size:1.05rem;">📁 How to scan a folder</p>
                <p style="color:#8a9bb8;font-size:0.88rem;margin:0;line-height:1.5;">
                <b style="color:#c8d8f0">Desktop:</b> Drag & drop a folder straight onto the box below, or click and select files.<br>
                <b style="color:#c8d8f0">Mobile:</b> Tap the box and select files from your device.
                </p>
            </div>
            """, unsafe_allow_html=True)

            uploaded_files = st.file_uploader(
                "Drop files or a folder here",
                accept_multiple_files=True,
                label_visibility="collapsed",
                help="Drag & drop a folder, or select files."
            )

            save_results = st.checkbox("Save to Master Database", value=True)

            with st.expander("Supported File Types"):
                for cat, exts in SUPPORTED_EXTENSIONS.items():
                    st.markdown(f"**{cat.title()}:** {', '.join(exts)}")

            st.divider()

            if uploaded_files:
                st.markdown(f"📦 **{len(uploaded_files)}** file(s) selected")
                if st.button("🚀 Scan Files", use_container_width=True, type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results = []
                    errors = []

                    for i, uploaded_file in enumerate(uploaded_files):
                        progress_bar.progress(min(i / len(uploaded_files), 1.0))
                        status_text.markdown(f"📂 Processing file {i + 1} of {len(uploaded_files)}...")

                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix="_" + uploaded_file.name) as tmp:
                                tmp.write(uploaded_file.getvalue())
                                tmp_path = tmp.name

                            result = scan_file(tmp_path)
                            result["file_path"] = uploaded_file.name
                            result["metadata"]["filename"] = uploaded_file.name
                            results.append(result)
                            os.unlink(tmp_path)
                        except Exception as e:
                            errors.append({"file": uploaded_file.name, "error": str(e)})

                    progress_bar.progress(1.0)
                    status_text.markdown("✅ Scan complete!")

                    if save_results:
                        for r in results:
                            save_file_scan(r["file_path"], r["file_type"], r["file_size"], r["metadata"])

                    _show_results(results, errors)

        else:
            # ── Local path scanning (server-side filesystem) ──
            st.markdown("### Scan a Local Folder")
            col_path, col_opts = st.columns([2, 1])

            with col_path:
                scan_path = st.text_input(
                    "Directory Path",
                    value="/storage/emulated/0/",
                    help="Enter the full path to a directory. For phone data, point to an Android/iPhone backup folder."
                )

            with col_opts:
                max_files = st.number_input("Max Files to Scan", min_value=10, max_value=2000, value=200, step=50)
                save_results = st.checkbox("Save to Master Database", value=True)

            # Quick path shortcuts
            st.markdown("**Quick shortcuts:**")
            shortcuts_row = st.columns(5)
            quick_paths = [
                ("Home", os.path.expanduser("~")),
                ("Downloads", os.path.expanduser("~/Downloads")),
                ("Desktop", os.path.expanduser("~/Desktop")),
                ("Documents", os.path.expanduser("~/Documents")),
                ("Current Project", os.getcwd()),
            ]
            for i, (label, path) in enumerate(quick_paths):
                if shortcuts_row[i].button(label, key=f"quick_{i}", use_container_width=True):
                    scan_path = path
                    st.session_state["scan_path_override"] = path

            if "scan_path_override" in st.session_state:
                scan_path = st.session_state["scan_path_override"]

            with st.expander("Supported File Types"):
                for cat, exts in SUPPORTED_EXTENSIONS.items():
                    st.markdown(f"**{cat.title()}:** {', '.join(exts)}")

            st.divider()

            if st.button("🚀 Start Scan", use_container_width=True, type="primary"):
                if not os.path.exists(scan_path):
                    st.error(f"Path does not exist: `{scan_path}`")
                elif not os.path.isdir(scan_path):
                    st.error("Please provide a directory path, not a file path.")
                else:
                    st.info(f"Scanning: `{scan_path}` (max {max_files} files)")
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def on_progress(current, total):
                        if total > 0:
                            progress_bar.progress(min(current / total, 1.0))
                            status_text.markdown(f"📂 Processing file {current} of {total}...")

                    with st.spinner("Scanning files..."):
                        results, errors = scan_directory(scan_path, max_files=max_files, progress_callback=on_progress)

                    progress_bar.progress(1.0)
                    status_text.markdown("✅ Scan complete!")

                    if save_results:
                        for r in results:
                            save_file_scan(r["file_path"], r["file_type"], r["file_size"], r["metadata"])

                    _show_results(results, errors)

    with tab2:
        st.markdown("### 📋 Previously Scanned Files")
        file_scans = get_all_file_scans()
        if file_scans:
            table_data = []
            for fs in file_scans:
                try:
                    meta = json.loads(fs.get("metadata_json", "{}"))
                except Exception:
                    meta = {}
                table_data.append({
                    "File Name": meta.get("filename", os.path.basename(fs.get("file_path", ""))),
                    "Type": fs["file_type"],
                    "Size (KB)": round(fs["file_size"] / 1024, 1) if fs["file_size"] else 0,
                    "Key Info": _summarize_meta(meta),
                    "Scanned At": fs["created_at"],
                    "Full Path": fs["file_path"],
                })
            df_history = pd.DataFrame(table_data)

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                type_f = st.selectbox("Filter Type", ["All"] + list(df_history["Type"].unique()))
            with col_f2:
                search_f = st.text_input("Search filename")

            if type_f != "All":
                df_history = df_history[df_history["Type"] == type_f]
            if search_f:
                df_history = df_history[df_history["File Name"].str.contains(search_f, case=False, na=False)]

            st.dataframe(df_history, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(file_scans)} files in database")
        else:
            st.info("No file scans recorded yet. Run a scan from the 'Scan' tab.")

def _show_results(results, errors):
    """Display scan results and errors consistently."""
    summary = get_directory_summary(results)
    st.success(f"✅ Scanned {summary['total_files']} files ({summary['total_size_mb']} MB)")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### 📊 Files by Category")
        if summary["by_category"]:
            df_cat = pd.DataFrame(
                list(summary["by_category"].items()),
                columns=["Category", "Count"]
            ).sort_values("Count", ascending=False)
            st.dataframe(df_cat, use_container_width=True, hide_index=True)

    with col_s2:
        st.markdown("#### 🚨 Notable Findings")
        if summary["notable_finds"]:
            for find in summary["notable_finds"]:
                st.warning(find)
        else:
            st.info("No notable findings detected.")

    st.divider()
    st.markdown("#### 📋 All Scanned Files")
    if results:
        table_data = []
        for r in results:
            meta = r.get("metadata", {})
            table_data.append({
                "File Name": meta.get("filename", ""),
                "Type": r["file_type"],
                "Size (KB)": round(r["file_size"] / 1024, 1),
                "Modified": meta.get("modified", ""),
                "MD5": meta.get("md5", "")[:12] + "...",
                "Key Info": _summarize_meta(meta),
                "Path": r["file_path"],
            })
        df_results = pd.DataFrame(table_data)

        cats = ["All"] + list(summary["by_category"].keys())
        cat_filter = st.selectbox("Filter by category", cats)
        if cat_filter != "All":
            df_results = df_results[df_results["Type"] == cat_filter]

        st.dataframe(df_results, use_container_width=True, hide_index=True)

    if errors:
        with st.expander(f"⚠️ {len(errors)} errors during scan"):
            for err in errors[:20]:
                st.markdown(f"- `{err['file']}`: {err['error']}")


def _summarize_meta(meta):
    highlights = []
    if "Make" in meta:
        highlights.append(f"Camera: {meta['Make']} {meta.get('Model','')}")
    if "DateTime" in meta:
        highlights.append(f"Taken: {meta['DateTime']}")
    if "GPSInfo" in meta:
        highlights.append("⚠️ GPS Data Found")
    if "full_name" in meta:
        highlights.append(f"Contact: {meta['full_name']}")
    if "phones" in meta:
        highlights.append(f"Tel: {meta['phones']}")
    if "artist" in meta or "TPE1" in meta:
        highlights.append(f"Artist: {meta.get('artist', meta.get('TPE1',''))}")
    if "duration_sec" in meta:
        highlights.append(f"Duration: {meta['duration_sec']}s")
    if "width" in meta and "height" in meta:
        highlights.append(f"{meta['width']}x{meta['height']}px")
    return " | ".join(highlights) if highlights else "—"
