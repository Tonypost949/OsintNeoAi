import streamlit as st
import pandas as pd


def render():
    st.markdown("""
    <style>
    .main { background-color: #0a0e1a; color: #c8d8f0; }
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: #141d35 !important;
        border: 1px solid #1e2d50 !important;
        color: #e8f4ff !important;
        font-family: 'Courier New', monospace;
    }
    .stSlider > div > div { color: #00d4ff; }
    .stDataFrame { border: 1px solid #1e2d50; border-radius: 6px; }
    .stDataFrame thead th { background: #0f1628 !important; color: #00d4ff !important; }
    .stDataFrame tbody td { color: #c8d8f0; background: #0a0e1a; }
    .stDataFrame tbody tr:nth-child(even) td { background: #141d35; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏘️ Real Estate Analyzer")
    st.markdown("<p style='color:#5a7090;font-family:Courier New;'>Property valuation, mortgage modeling, and investment analysis.</p>", unsafe_allow_html=True)

    # ── Property Inputs ──
    with st.expander("📋 Property Details", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            address = st.text_input("Property Address", "123 Main St, Anytown, USA")
            price = st.number_input("Purchase Price ($)", min_value=0, value=500000, step=10000)
            sqft = st.number_input("Square Footage", min_value=0, value=2000, step=100)
        with c2:
            beds = st.number_input("Bedrooms", min_value=0, value=3, step=1)
            baths = st.number_input("Bathrooms", min_value=0.0, value=2.0, step=0.5)
            year_built = st.number_input("Year Built", min_value=1800, max_value=2030, value=2000, step=1)
        with c3:
            hoa = st.number_input("Monthly HOA ($)", min_value=0, value=0, step=25)
            prop_tax_rate = st.number_input("Property Tax Rate (%)", min_value=0.0, value=1.2, step=0.1)
            insurance = st.number_input("Annual Insurance ($)", min_value=0, value=1800, step=100)

    # ── Mortgage Inputs ──
    with st.expander("🏦 Mortgage Terms"):
        c1, c2, c3 = st.columns(3)
        with c1:
            down_pct = st.slider("Down Payment %", 0, 100, 20)
        with c2:
            rate = st.number_input("Interest Rate (%)", min_value=0.0, value=6.5, step=0.1)
        with c3:
            term_years = st.selectbox("Loan Term", [15, 20, 30], index=2)

    # ── Investment Inputs ──
    with st.expander("📈 Investment Assumptions"):
        c1, c2, c3 = st.columns(3)
        with c1:
            rent = st.number_input("Monthly Rent ($)", min_value=0, value=3000, step=100)
            vacancy = st.number_input("Vacancy Rate (%)", min_value=0.0, value=8.0, step=0.5)
        with c2:
            mgmt_pct = st.number_input("Management Fee (%)", min_value=0.0, value=8.0, step=0.5)
            repair_pct = st.number_input("Repairs / Maint (%)", min_value=0.0, value=8.0, step=0.5)
        with c3:
            capex_pct = st.number_input("CapEx Reserve (%)", min_value=0.0, value=5.0, step=0.5)
            appreciation = st.number_input("Annual Appreciation (%)", min_value=0.0, value=3.0, step=0.5)

    # ── Calculations ──
    down_amt = price * (down_pct / 100)
    loan = price - down_amt
    n = term_years * 12
    r = rate / 100 / 12
    if r > 0:
        p_i = loan * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        p_i = loan / n
    tax_monthly = (price * (prop_tax_rate / 100)) / 12
    ins_monthly = insurance / 12
    pmi_monthly = 0 if down_pct >= 20 else (loan * 0.0075) / 12
    hoa_monthly = hoa
    total_monthly = p_i + tax_monthly + ins_monthly + pmi_monthly + hoa_monthly

    # ── Mortgage Summary ──
    st.markdown("<hr style='border-color:#1e2d50;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>🏦 MORTGAGE SUMMARY</p>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Down Payment", f"${down_amt:,.0f}")
    c2.metric("Loan Amount", f"${loan:,.0f}")
    c3.metric("P&I", f"${p_i:,.0f}/mo")
    c4.metric("Total Monthly", f"${total_monthly:,.0f}/mo")
    c5.metric("$/sqft", f"${price/sqft:,.0f}")

    # ── PITI Breakdown ──
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>📊 PITI BREAKDOWN</p>", unsafe_allow_html=True)
    piti_data = pd.DataFrame({
        "Component": ["Principal & Interest", "Property Tax", "Insurance", "PMI", "HOA"],
        "Monthly": [p_i, tax_monthly, ins_monthly, pmi_monthly, hoa_monthly],
        "% of Total": [
            p_i / total_monthly * 100,
            tax_monthly / total_monthly * 100,
            ins_monthly / total_monthly * 100,
            pmi_monthly / total_monthly * 100,
            hoa_monthly / total_monthly * 100,
        ]
    })
    st.dataframe(piti_data.style.format({"Monthly": "${:,.0f}", "% of Total": "{:.1f}%"}), hide_index=True, use_container_width=True)

    # ── Investment Analysis ──
    st.markdown("<hr style='border-color:#1e2d50;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>📈 INVESTMENT ANALYSIS</p>", unsafe_allow_html=True)

    gross_rent = rent * 12
    vacancy_loss = gross_rent * (vacancy / 100)
    effective_income = gross_rent - vacancy_loss
    mgmt_cost = effective_income * (mgmt_pct / 100)
    repair_cost = effective_income * (repair_pct / 100)
    capex_cost = effective_income * (capex_pct / 100)
    tax_annual = price * (prop_tax_rate / 100)
    opex = mgmt_cost + repair_cost + capex_cost + tax_annual + insurance + (hoa * 12)
    noi = effective_income - opex
    annual_debt = p_i * 12
    cash_flow = noi - annual_debt
    coc = (cash_flow / (down_amt + (price * 0.03))) * 100 if (down_amt + (price * 0.03)) > 0 else 0
    cap_rate = (noi / price) * 100 if price > 0 else 0
    dscr = noi / annual_debt if annual_debt > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("NOI", f"${noi:,.0f}/yr")
    c2.metric("Cash Flow", f"${cash_flow:,.0f}/yr", delta=f"${cash_flow/12:,.0f}/mo")
    c3.metric("Cap Rate", f"{cap_rate:.2f}%")
    c4.metric("Cash-on-Cash", f"{coc:.2f}%")
    c5.metric("DSCR", f"{dscr:.2f}x")

    # ── Rent vs Buy ──
    st.markdown("<hr style='border-color:#1e2d50;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>⚖️ RENT VS BUY COMPARISON</p>", unsafe_allow_html=True)
    own_monthly = total_monthly
    rent_monthly = rent
    delta = own_monthly - rent_monthly
    rvb_data = pd.DataFrame({
        "": ["Own", "Rent"],
        "Monthly Cost": [own_monthly, rent_monthly],
        "Annual Cost": [own_monthly * 12, rent_monthly * 12],
    })
    st.dataframe(rvb_data.style.format({"Monthly Cost": "${:,.0f}", "Annual Cost": "${:,.0f}"}), hide_index=True, use_container_width=True)
    st.markdown(f"<p style='color:#ffd700;font-family:Courier New;'>Monthly delta: Owning costs <b>${delta:+,.0f}/mo</b> more than renting.</p>", unsafe_allow_html=True)

    # ── Sensitivity Matrix ──
    st.markdown("<hr style='border-color:#1e2d50;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>🎲 SENSITIVITY: RENT vs PURCHASE PRICE</p>", unsafe_allow_html=True)

    prices = [price * 0.90, price * 0.95, price]
    rents = [rent * 0.85, rent * 0.90, rent, rent * 1.10, rent * 1.20]
    matrix = []
    for p in prices:
        row = {}
        l = p * (1 - down_pct / 100)
        if r > 0:
            pi = l * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        else:
            pi = l / n
        t = (p * (prop_tax_rate / 100)) / 12
        tot = pi + t + ins_monthly + pmi_monthly + hoa_monthly
        for rv in rents:
            gi = rv * 12
            vi = gi * (vacancy / 100)
            ei = gi - vi
            mc = ei * (mgmt_pct / 100)
            rc = ei * (repair_pct / 100)
            cc = ei * (capex_pct / 100)
            o = mc + rc + cc + tax_annual + insurance + (hoa * 12)
            no = ei - o
            cf = no - (pi * 12)
            row[f"${rv:,.0f}"] = f"${cf:,.0f}"
        matrix.append(row)
    df_mat = pd.DataFrame(matrix, index=[f"${p:,.0f}" for p in prices])
    st.dataframe(df_mat, use_container_width=True)

    # ── Exit Scenarios ──
    st.markdown("<hr style='border-color:#1e2d50;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>🚪 EXIT SCENARIOS (3% appreciation)</p>", unsafe_allow_html=True)
    exit_data = []
    for yr in [3, 5, 7, 10]:
        sp = price * ((1.03) ** yr)
        sc = sp * 0.055
        # remaining balance
        bal = loan * (((1 + r) ** n - (1 + r) ** (yr * 12)) / ((1 + r) ** n - 1)) if r > 0 else loan * (1 - (yr * 12) / n)
        np = sp - sc - bal
        ti = down_amt + (price * 0.03)
        ret = np - ti
        roi = ((np / ti) ** (1 / yr) - 1) * 100 if ti > 0 and yr > 0 else 0
        exit_data.append({
            "Year": yr,
            "Sale Price": f"${sp:,.0f}",
            "Selling Costs": f"-${sc:,.0f}",
            "Loan Balance": f"-${bal:,.0f}",
            "Net Proceeds": f"${np:,.0f}",
            "Total Invested": f"${ti:,.0f}",
            "Profit/Loss": f"${ret:,.0f}",
            "Annualized ROI": f"{roi:.1f}%",
        })
    st.dataframe(pd.DataFrame(exit_data), hide_index=True, use_container_width=True)

    # ── Verdict ──
    st.markdown("<hr style='border-color:#1e2d50;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d4ff;font-family:Courier New;font-weight:bold;'>🎯 VERDICT</p>", unsafe_allow_html=True)
    verdict = []
    if coc >= 8:
        verdict.append("✅ Strong cash-on-cash return — beats index funds.")
    elif coc >= 4:
        verdict.append("⚠️ Modest cash flow — you're buying appreciation, not yield.")
    else:
        verdict.append("❌ Negative cash flow — deal relies entirely on appreciation.")
    if dscr >= 1.25:
        verdict.append("✅ DSCR healthy — lenders will approve.")
    elif dscr >= 1.0:
        verdict.append("⚠️ DSCR tight — rent barely covers mortgage.")
    else:
        verdict.append("❌ DSCR below 1.0 — rent does NOT cover the mortgage.")
    if cap_rate >= 6:
        verdict.append("✅ Cap rate above 6% — solid for cash-flow investors.")
    elif cap_rate >= 4:
        verdict.append("⚠️ Cap rate 4-6% — typical for A/B markets.")
    else:
        verdict.append("❌ Cap rate below 4% — appreciation play only.")
    for v in verdict:
        st.markdown(f"<p style='color:#c8d8f0;font-family:Courier New;'>{v}</p>", unsafe_allow_html=True)
