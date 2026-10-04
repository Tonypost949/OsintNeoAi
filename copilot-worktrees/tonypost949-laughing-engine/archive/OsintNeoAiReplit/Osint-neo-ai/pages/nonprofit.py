import streamlit as st
import pandas as pd
import sqlite3
from utils.database import get_connection

# ── Static dataset: Huntington Beach homeless nonprofits ─────────────────────
HB_NONPROFITS = [
    {
        "Name": "Mercy House / HB Navigation Center",
        "Type": "Shelter",
        "Population": "Adults & couples (HB ties)",
        "Services": "Emergency shelter (174 beds), housing navigation, storage, shuttles",
        "Address": "Huntington Beach, CA (referral only)",
        "Phone": "",
        "Website": "mercyhouse.net",
        "Church_Affiliated": False,
        "Risk_Flag": "High",
        "Notes": "Operates HB Navigation Center on behalf of City of HB. Referral required.",
    },
    {
        "Name": "Colette's Children's Home",
        "Type": "Shelter",
        "Population": "Homeless women & children",
        "Services": "Temp shelter (30 days), meals, case mgmt, life skills, job help, bus passes",
        "Address": "9372 Prince Dr Suite 106, Huntington Beach, CA 92647",
        "Phone": "(714) 596-1380",
        "Website": "coletteschildrenshome.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Mon–Fri 8AM–5PM. Women may stay up to 30 days.",
    },
    {
        "Name": "Robyne's Nest",
        "Type": "Youth Services",
        "Population": "At-risk & homeless HS students",
        "Services": "Housing support, school completion, prevention of trafficking & substance use",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "robynesnest.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Referrals from HB & Newport Mesa school districts.",
    },
    {
        "Name": "Coast to Coast Foundation",
        "Type": "Outreach",
        "Population": "General homeless",
        "Services": "Street outreach, case management, coordinated entry system",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "coasttocoastfoundation.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Medium",
        "Notes": "Partners directly with HB Police Homeless Liaison Officer Program.",
    },
    {
        "Name": "Waymakers HB Youth Shelter",
        "Type": "Youth Shelter",
        "Population": "Youth ages 11–17",
        "Services": "12-bed crisis shelter (24/7), runaway/abused/homeless youth, family reunification",
        "Address": "7291 Talbert Ave, Huntington Beach, CA 92648",
        "Phone": "(714) 842-6600",
        "Website": "",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "24 hours a day, 7 days a week.",
    },
    {
        "Name": "Orange County Rescue Mission",
        "Type": "Shelter / Rehab",
        "Population": "Men, women, children, veterans",
        "Services": "Emergency shelter, food, rehab programs, medical/dental/optical clinic",
        "Address": "1 Hope Drive, Tustin, CA 92782",
        "Phone": "",
        "Website": "rescuemission.org",
        "Church_Affiliated": True,
        "Risk_Flag": "Medium",
        "Notes": "Faith-based. Serves all of Orange County including HB.",
    },
    {
        "Name": "Someone Cares Soup Kitchen",
        "Type": "Food / Basic Needs",
        "Population": "Homeless, unemployed, working poor, seniors",
        "Services": "Daily meals 7 days/week, showers Mon & Wed 2–4PM",
        "Address": "Orange County, CA",
        "Phone": "",
        "Website": "someonecaressoupkitchen.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Mon–Fri 12–3PM meals; Sat–Sun 9–11AM breakfast.",
    },
    {
        "Name": "Mary's Kitchen Pantry",
        "Type": "Food Pantry",
        "Population": "Food-insecure residents",
        "Services": "Emergency food assistance, pantry",
        "Address": "Orange, CA (serves HB)",
        "Phone": "",
        "Website": "maryskitchen.org",
        "Church_Affiliated": True,
        "Risk_Flag": "Low",
        "Notes": "Faith-based food pantry serving Orange County.",
    },
    {
        "Name": "Assistance League of Huntington Beach",
        "Type": "Community Services",
        "Population": "General community",
        "Services": "Community assistance, basic needs, clothing, school supplies",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "alhuntingtonbeach.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Volunteer-run community service organization.",
    },
    {
        "Name": "Orange County Food Bank",
        "Type": "Food Bank",
        "Population": "Food-insecure & homeless",
        "Services": "Large-scale food distribution across Orange County",
        "Address": "Orange County, CA",
        "Phone": "",
        "Website": "feedoc.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Part of the Second Harvest Food Bank network.",
    },
    {
        "Name": "Build Futures",
        "Type": "Youth Housing",
        "Population": "Homeless youth ages 18–24",
        "Services": "Housing, job training, education, medical, mental health",
        "Address": "Orange County, CA",
        "Phone": "",
        "Website": "buildfutures.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Mon/Wed/Fri 9AM–5PM. Partners with faith-based orgs & community services.",
    },
    {
        "Name": "Casa Youth Shelter",
        "Type": "Youth Shelter",
        "Population": "Youth ages 12–17",
        "Services": "Emergency shelter 24/7, meals, showers, clothing, counseling",
        "Address": "Orange County, CA",
        "Phone": "",
        "Website": "",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "For runaways, abused or abandoned youth.",
    },
    {
        "Name": "Give It Back To Kids (GIBTK)",
        "Type": "Youth / Family",
        "Population": "Children in need",
        "Services": "Hope and support for children, HB-based",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "giveitbacktokids.com",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "HB-based nonprofit focused on children.",
    },
    {
        "Name": "StandUp For Kids – Orange County",
        "Type": "Youth Housing",
        "Population": "Homeless youth 18–24",
        "Services": "Rapid rehousing, transitional & permanent housing",
        "Address": "Orange County, CA",
        "Phone": "(714) 356-5437",
        "Website": "standupforkids.org/orange-county",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "",
    },
    {
        "Name": "We Care Orange County",
        "Type": "Prevention",
        "Population": "At-risk of homelessness",
        "Services": "Rent/utility assistance, case management, food pantry",
        "Address": "Los Alamitos area (serves OC)",
        "Phone": "",
        "Website": "wecareorangecounty.org",
        "Church_Affiliated": False,
        "Risk_Flag": "Low",
        "Notes": "Homelessness prevention focused.",
    },
    {
        "Name": "Childnet Youth and Family Services",
        "Type": "Youth / Family",
        "Population": "Foster youth & families",
        "Services": "Foster care, mental health, family preservation, transitional housing",
        "Address": "Orange County, CA",
        "Phone": "",
        "Website": "childnet.org",
        "Church_Affiliated": False,
        "Risk_Flag": "High",
        "Notes": "In master DB as ENT-016. ProPublica full filing scanned. Tied to case files.",
    },
]

# Churches with city social worker hours
HB_CHURCHES = [
    # ── Large / Megachurch ────────────────────────────────────────────────────
    {
        "Name": "Mariners Church – HB Campus",
        "Denomination": "Non-Denominational",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "marinerschurch.org",
        "Size_Tier": "Megachurch",
        "Est_Attendance": "~20,000 (all campuses)",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Largest church presence in HB. Main campus in Irvine. HB branch est. 2015.",
    },
    {
        "Name": "Compass Bible Church HB (CompassHB)",
        "Denomination": "Non-Denominational",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "compasshb.com",
        "Size_Tier": "Large",
        "Est_Attendance": "Large (multi-service)",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    {
        "Name": "First Christian Church of HB (FCCHB)",
        "Denomination": "Christian / Non-Denom",
        "Address": "1207 Main St, Huntington Beach, CA 92648",
        "Phone": "",
        "Website": "fcchb.org",
        "Size_Tier": "Large",
        "Est_Attendance": "Large (multi-service)",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Downtown HB landmark church.",
    },
    {
        "Name": "Calvary Chapel Huntington Beach",
        "Denomination": "Calvary Chapel",
        "Address": "5772 McFadden Ave, Huntington Beach, CA 92649",
        "Phone": "",
        "Website": "calvary-hb.org",
        "Size_Tier": "Large",
        "Est_Attendance": "Large",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Rooted in original Calvary Chapel movement.",
    },
    {
        "Name": "Calvary Chapel Beachside",
        "Denomination": "Calvary Chapel",
        "Address": "19400 Beach Blvd, Huntington Beach, CA 92648",
        "Phone": "",
        "Website": "calvarybeachside.com",
        "Size_Tier": "Large",
        "Est_Attendance": "Large",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    # ── Mid-Size ─────────────────────────────────────────────────────────────
    {
        "Name": "Seabreeze Community Church",
        "Denomination": "Non-Denominational",
        "Address": "18162 Gothard St, Huntington Beach, CA",
        "Phone": "",
        "Website": "seabreeze.org",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Consistently rated one of the most attended churches in HB.",
    },
    {
        "Name": "Saddleback Church – HB Campus",
        "Denomination": "Evangelical Non-Denom",
        "Address": "Huntington Beach, CA",
        "Phone": "",
        "Website": "saddleback.com",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Campus of the nationally known Saddleback Church.",
    },
    {
        "Name": "ShoreLife Church",
        "Denomination": "Baptist",
        "Address": "4952 Warner Ave #320, Huntington Beach, CA 92649",
        "Phone": "",
        "Website": "shorelife.org",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Est. 2007+.",
    },
    {
        "Name": "BeachCities Church",
        "Denomination": "Non-Denominational",
        "Address": "9872 Hamilton Ave, Huntington Beach, CA 92646",
        "Phone": "",
        "Website": "beachcities.org",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Modern worship, small groups focus.",
    },
    {
        "Name": "Crosspoint Church",
        "Denomination": "Non-Denominational",
        "Address": "7661 Warner Ave, Huntington Beach, CA 92647",
        "Phone": "",
        "Website": "crosspointhb.org",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    {
        "Name": "St. Bonaventure Catholic Church",
        "Denomination": "Catholic",
        "Address": "16400 Springdale St, Huntington Beach, CA 92649",
        "Phone": "",
        "Website": "stbonaventurehb.org",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "One of the largest Catholic parishes in HB.",
    },
    {
        "Name": "St. Mary's by the Sea",
        "Denomination": "Catholic",
        "Address": "321 10th St, Huntington Beach, CA 92648",
        "Phone": "",
        "Website": "stmarysbythesea.net",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Downtown HB Catholic parish near the pier.",
    },
    {
        "Name": "Saints Simon & Jude",
        "Denomination": "Catholic",
        "Address": "20444 Magnolia St, Huntington Beach, CA 92646",
        "Phone": "",
        "Website": "stsj.org",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    {
        "Name": "St. Vincent de Paul",
        "Denomination": "Catholic",
        "Address": "8345 Talbert Ave, Huntington Beach, CA 92646",
        "Phone": "",
        "Website": "stvdphb.com",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "SVdP parish — associated with St. Vincent de Paul Society charitable work.",
    },
    {
        "Name": "Hope Chapel Huntington Beach",
        "Denomination": "Foursquare",
        "Address": "715 Lake St, Huntington Beach, CA",
        "Phone": "",
        "Website": "",
        "Size_Tier": "Mid-Size",
        "Est_Attendance": "Mid-size",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    # ── Community / Smaller ───────────────────────────────────────────────────
    {
        "Name": "Community Bible Church",
        "Denomination": "Non-Denominational",
        "Address": "401 6th St, Huntington Beach, CA 92648",
        "Phone": "",
        "Website": "cbchb.org",
        "Size_Tier": "Community",
        "Est_Attendance": "Smaller",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "Mission-focused. Downtown HB.",
    },
    {
        "Name": "First United Methodist Church",
        "Denomination": "Methodist",
        "Address": "2721 Delaware St, Huntington Beach, CA 92648",
        "Phone": "",
        "Website": "fumchb.org",
        "Size_Tier": "Community",
        "Est_Attendance": "Smaller",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    {
        "Name": "Community United Methodist Church",
        "Denomination": "Methodist",
        "Address": "6652 Heil Ave, Huntington Beach, CA",
        "Phone": "",
        "Website": "",
        "Size_Tier": "Community",
        "Est_Attendance": "Smaller",
        "City_Dropsite": True,
        "City_Hours": "Wednesdays 1:30–3:00 PM — City social workers on-site",
        "Notes": "Official City of HB social worker drop-in site.",
    },
    {
        "Name": "Refuge Calvary Chapel",
        "Denomination": "Calvary Chapel",
        "Address": "7800 Edinger Ave, Huntington Beach, CA",
        "Phone": "",
        "Website": "",
        "Size_Tier": "Community",
        "Est_Attendance": "Smaller",
        "City_Dropsite": True,
        "City_Hours": "Thursdays 11:00 AM–12:30 PM — City social workers on-site",
        "Notes": "Official City of HB social worker drop-in site.",
    },
    {
        "Name": "Warner Baptist Church",
        "Denomination": "Baptist",
        "Address": "7360 Warner Ave, Huntington Beach, CA 92647",
        "Phone": "",
        "Website": "",
        "Size_Tier": "Community",
        "Est_Attendance": "Smaller",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
    {
        "Name": "Faith Lutheran Church",
        "Denomination": "Lutheran",
        "Address": "8200 Ellis Ave, Huntington Beach, CA 92646",
        "Phone": "",
        "Website": "",
        "Size_Tier": "Community",
        "Est_Attendance": "Smaller",
        "City_Dropsite": False,
        "City_Hours": "",
        "Notes": "",
    },
]


def render():
    st.markdown("## 🏛️ Nonprofit Intelligence — Huntington Beach")

    # ── Top metrics ─────────────────────────────────────────────────────────
    total = len(HB_NONPROFITS)
    church_aff = sum(1 for x in HB_NONPROFITS if x["Church_Affiliated"])
    high_risk  = sum(1 for x in HB_NONPROFITS if x["Risk_Flag"] == "High")
    in_db = 0
    try:
        conn = get_connection()
        in_db = conn.execute(
            "SELECT COUNT(*) FROM entities WHERE lower(type) LIKE '%org%' OR lower(category) LIKE '%nonprofit%'"
        ).fetchone()[0]
        conn.close()
    except Exception:
        pass

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏛️ Nonprofits", total)
    c2.metric("✝️ HB Churches", len(HB_CHURCHES))
    c3.metric("🏛️ City Drop-Sites", sum(1 for c in HB_CHURCHES if c["City_Dropsite"]))
    c4.metric("🔴 High Interest", high_risk)
    c5.metric("📌 In Master DB", in_db)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 HB Homeless Orgs",
        "✝️ Churches / Drop-in Sites",
        "📌 Master DB Orgs",
        "➕ Add to Master DB",
    ])

    # ── TAB 1: HB Homeless Orgs ──────────────────────────────────────────────
    with tab1:
        st.markdown("### Huntington Beach Homeless & Housing Nonprofits")
        st.caption("Source: City of HB, GreatNonprofits, Yelp — verified March 2026")

        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search = st.text_input("🔍 Search orgs", placeholder="name, service, population…", key="np_search")
        with col_f2:
            type_filter = st.selectbox("Filter by type", ["All"] + sorted(set(x["Type"] for x in HB_NONPROFITS)), key="np_type")

        df = pd.DataFrame(HB_NONPROFITS)
        if search:
            mask = df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
            df = df[mask]
        if type_filter != "All":
            df = df[df["Type"] == type_filter]

        # Color-code Risk_Flag
        def style_risk(val):
            colors = {"High": "color:#ff4444;font-weight:bold", "Medium": "color:#ffd700", "Low": "color:#00ff88"}
            return colors.get(val, "")

        st.markdown(f"**{len(df)} organizations**")

        for _, row in df.iterrows():
            risk_color = {"High": "#ff4444", "Medium": "#ffd700", "Low": "#00ff88"}.get(row["Risk_Flag"], "#5a7090")
            church_badge = "✝️ " if row["Church_Affiliated"] else ""
            with st.expander(f"{church_badge}{row['Name']}  —  {row['Type']}  [ {row['Risk_Flag']} ]"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Population:** {row['Population']}")
                    st.markdown(f"**Services:** {row['Services']}")
                    st.markdown(f"**Address:** {row['Address']}")
                with col_b:
                    if row["Phone"]:
                        st.markdown(f"**Phone:** {row['Phone']}")
                    if row["Website"]:
                        st.markdown(f"**Website:** [{row['Website']}](https://{row['Website']})")
                    st.markdown(
                        f"**Risk Flag:** <span style='color:{risk_color}'>{row['Risk_Flag']}</span>",
                        unsafe_allow_html=True,
                    )
                if row["Notes"]:
                    st.info(row["Notes"])

        st.divider()
        st.markdown("#### 🏛️ City of HB — Official Contact")
        st.markdown("""
| Resource | Details |
|---|---|
| **City Social Workers** | (714) 536-5576 |
| **Email** | [email protected] |
| **HB Police Lobby** | 2000 Main St — Tues 9–11AM, Wed 10AM–12PM |
""")

    # ── TAB 2: Churches / Drop-in Sites ─────────────────────────────────────
    with tab2:
        st.markdown("### Top 20 Churches — Huntington Beach, CA")
        st.caption("Source: Outreach 100, Hartford Institute, pastors.ai, City of HB — verified March 2026")

        # Search + filter
        col_cs1, col_cs2 = st.columns([2, 1])
        with col_cs1:
            church_search = st.text_input("🔍 Search churches", placeholder="name, denomination, address…", key="church_search")
        with col_cs2:
            tier_filter = st.selectbox("Filter by size", ["All", "Megachurch", "Large", "Mid-Size", "Community"], key="church_tier")

        filtered = HB_CHURCHES
        if church_search:
            filtered = [c for c in filtered if church_search.lower() in str(c).lower()]
        if tier_filter != "All":
            filtered = [c for c in filtered if c["Size_Tier"] == tier_filter]

        # Tier color map
        tier_colors = {
            "Megachurch": "#7b2fff",
            "Large":      "#00d4ff",
            "Mid-Size":   "#ffd700",
            "Community":  "#00ff88",
        }

        # City drop-in sites first
        drop_sites = [c for c in filtered if c["City_Dropsite"]]
        if drop_sites:
            st.markdown("#### 🏛️ City Social Worker Drop-In Sites")
            for c in drop_sites:
                st.markdown(f"""
<div style='background:#0f1628;border:2px solid #ffd700;border-radius:8px;padding:1em;margin-bottom:0.8em'>
  <div style='color:#ffd700;font-size:1rem;font-weight:bold'>⚠️ ✝️ {c['Name']}</div>
  <div style='color:#c8d8f0;margin-top:0.3em'>📍 {c['Address']} &nbsp;|&nbsp; {c['Denomination']}</div>
  <div style='color:#ffd700;margin-top:0.3em'>🕐 {c['City_Hours']}</div>
  {f"<div style='color:#5a7090;margin-top:0.3em'>{c['Notes']}</div>" if c['Notes'] else ""}
</div>
""", unsafe_allow_html=True)
            st.divider()

        # Group remaining by tier
        for tier in ["Megachurch", "Large", "Mid-Size", "Community"]:
            tier_churches = [c for c in filtered if c["Size_Tier"] == tier and not c["City_Dropsite"]]
            if not tier_churches:
                continue
            color = tier_colors.get(tier, "#c8d8f0")
            st.markdown(f"<div style='color:{color};font-size:0.85rem;font-weight:bold;letter-spacing:0.1em;margin-top:1em'>── {tier.upper()} ──</div>", unsafe_allow_html=True)
            for c in tier_churches:
                website_html = f"<a href='https://{c['Website']}' target='_blank' style='color:#00d4ff'>{c['Website']}</a>" if c["Website"] else ""
                notes_html   = f"<div style='color:#5a7090;margin-top:0.3em;font-size:0.85rem'>{c['Notes']}</div>" if c["Notes"] else ""
                with st.expander(f"✝️ {c['Name']}  ·  {c['Denomination']}"):
                    ca, cb = st.columns(2)
                    with ca:
                        st.markdown(f"**📍 Address:** {c['Address']}")
                        st.markdown(f"**⛪ Denomination:** {c['Denomination']}")
                    with cb:
                        st.markdown(f"**📊 Size Tier:** <span style='color:{color}'>{c['Size_Tier']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**👥 Est. Attendance:** {c['Est_Attendance']}")
                        if c["Website"]:
                            st.markdown(f"**🌐 Website:** {website_html}", unsafe_allow_html=True)
                    if c["Notes"]:
                        st.info(c["Notes"])

        st.divider()
        st.markdown("#### ✝️ Faith-Affiliated Nonprofits")
        church_orgs = [x for x in HB_NONPROFITS if x["Church_Affiliated"]]
        if church_orgs:
            for org in church_orgs:
                st.markdown(f"- **{org['Name']}** — {org['Services']}")
        else:
            st.info("No faith-affiliated orgs flagged in current list.")

    # ── TAB 3: Master DB Orgs ────────────────────────────────────────────────
    with tab3:
        st.markdown("### Organizations Currently in Master Intelligence DB")
        try:
            conn = get_connection()
            df_db = pd.read_sql_query(
                "SELECT entity_id, label, type, category, risk_level, source, notes FROM entities WHERE lower(type) LIKE '%org%' OR lower(category) LIKE '%nonprofit%' OR lower(category) LIKE '%church%' OR lower(category) LIKE '%government%'",
                conn
            )
            conn.close()
            if df_db.empty:
                st.info("No org-type entities in master DB yet.")
            else:
                st.dataframe(df_db, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"DB error: {e}")

    # ── TAB 4: Add to Master DB ──────────────────────────────────────────────
    with tab4:
        st.markdown("### Add a Nonprofit / Church to Master Intelligence DB")

        all_orgs = [x["Name"] for x in HB_NONPROFITS] + [c["Name"] for c in HB_CHURCHES]
        quick_names = ["-- Select from HB list --"] + sorted(all_orgs) + ["Custom entry"]
        pick = st.selectbox("Quick-fill from HB org / church list", quick_names, key="np_quick")

        prefill = {}
        if pick not in ("-- Select from HB list --", "Custom entry"):
            prefill = next((x for x in HB_NONPROFITS if x["Name"] == pick), {})
            if not prefill:
                c = next((x for x in HB_CHURCHES if x["Name"] == pick), {})
                if c:
                    prefill = {"Name": c["Name"], "Address": c["Address"], "Phone": c.get("Phone",""), "Website": c.get("Website",""), "Notes": c.get("Notes","")}

        with st.form("add_nonprofit_form"):
            label   = st.text_input("Organization Name *", value=prefill.get("Name", ""))
            category = st.selectbox("Category", ["Nonprofit", "Church", "Government", "Faith-Based", "Food Bank", "Shelter", "Youth Services", "Other"])
            address  = st.text_input("Address", value=prefill.get("Address", ""))
            phone    = st.text_input("Phone", value=prefill.get("Phone", ""))
            website  = st.text_input("Website", value=prefill.get("Website", ""))
            risk     = st.selectbox("Risk Level", ["Unknown", "Low", "Medium", "High"], index=0)
            source   = st.text_input("Source", value="HB Nonprofit Research — March 2026")
            notes    = st.text_area("Notes", value=prefill.get("Notes", ""))
            submitted = st.form_submit_button("➕ Add to Master DB", type="primary")

            if submitted:
                if not label.strip():
                    st.error("Organization name is required.")
                else:
                    try:
                        conn = get_connection()
                        last = conn.execute("SELECT entity_id FROM entities ORDER BY id DESC LIMIT 1").fetchone()
                        last_num = int(last[0].replace("ENT-", "")) if last else 0
                        new_id = f"ENT-{last_num + 1:03d}"
                        geo = ""
                        if "Huntington Beach" in address:
                            geo = "33.6595, -117.9988"
                        conn.execute(
                            "INSERT INTO entities (entity_id, type, label, category, geo_location, risk_level, source, notes) VALUES (?,?,?,?,?,?,?,?)",
                            (new_id, "Organization", label.strip(), category, geo, risk, source, notes)
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Added **{label}** as {new_id} to master DB.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saving: {e}")
