"""
AMECATH — Executive Market Intelligence & Operations Platform
Run with: streamlit run app.py

Reads "AMECATH_Market_Intelligence.xlsx" (6 sheets) from the working directory.
Falls back to embedded mock data (same schema) if the file is missing or
unreadable, so the app never crashes on load.
"""

import os
import re
import random
import hashlib
import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================================
# PAGE CONFIG
# ==========================================================================
st.set_page_config(
    page_title="AMECATH | Executive Intelligence Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================
# PALETTE
# ==========================================================================
NAVY = "#0F172A"
CHARCOAL = "#1E293B"
TEAL = "#0EA5E9"
GOLD = "#D97706"
WHITE = "#FFFFFF"
MUTED = "#94A3B8"
CARD_BG = "#152238"
BORDER = "rgba(148, 163, 184, 0.15)"
RED = "#EF4444"
YELLOW = "#EAB308"
GREEN = "#22C55E"

CHART_COLORWAY = [TEAL, GOLD, "#22D3EE", "#F59E0B", "#38BDF8", "#FBBF24"]

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
        colorway=CHART_COLORWAY,
        xaxis=dict(showgrid=False, zeroline=False, linecolor=BORDER, tickfont=dict(color=MUTED)),
        yaxis=dict(showgrid=True, gridcolor=BORDER, zeroline=False, tickfont=dict(color=MUTED)),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0")),
        margin=dict(l=10, r=10, t=40, b=10),
    )
)

# ==========================================================================
# CSS
# ==========================================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background: linear-gradient(180deg, {NAVY} 0%, #0B1220 100%); color: {WHITE}; }}
        section[data-testid="stSidebar"] {{ background: {CHARCOAL}; border-right: 1px solid {BORDER}; }}
        section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        h1, h2, h3, h4 {{ color: {WHITE} !important; font-weight: 600 !important; letter-spacing: -0.02em; }}

        .dash-title {{
            font-size: 2.0rem; font-weight: 700;
            background: linear-gradient(90deg, {WHITE} 0%, {TEAL} 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;
        }}
        .dash-subtitle {{ color: {MUTED}; font-size: 0.92rem; margin-top: 2px; letter-spacing: 0.02em; text-transform: uppercase; }}

        .kpi-card {{
            background: linear-gradient(155deg, {CARD_BG} 0%, {CHARCOAL} 100%);
            border: 1px solid {BORDER}; border-radius: 16px; padding: 20px 22px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.25); height: 100%;
        }}
        .kpi-label {{ color: {MUTED}; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }}
        .kpi-value {{ color: {WHITE}; font-size: 1.8rem; font-weight: 700; line-height: 1.15; }}
        .kpi-accent {{ display:inline-block; width:34px; height:3px; border-radius:3px; background:{TEAL}; margin-top:10px; }}
        .kpi-accent.gold {{ background:{GOLD}; }}
        .kpi-accent.red {{ background:{RED}; }}
        .kpi-accent.green {{ background:{GREEN}; }}

        .section-card {{
            background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 16px;
            padding: 20px 22px; margin-bottom: 18px;
        }}
        .section-title {{ color: {WHITE}; font-size: 1rem; font-weight: 600; margin-bottom: 4px; }}
        .section-caption {{ color: {MUTED}; font-size: 0.8rem; margin-bottom: 14px; }}

        .badge-green {{ display:inline-block; background: rgba(34,197,94,0.12); color:{GREEN}; border: 1px solid rgba(34,197,94,0.4); border-radius: 10px; padding: 10px 16px; font-weight: 700; font-size: 0.85rem; }}
        .badge-yellow {{ display:inline-block; background: rgba(234,179,8,0.12); color:{YELLOW}; border: 1px solid rgba(234,179,8,0.4); border-radius: 10px; padding: 10px 16px; font-weight: 700; font-size: 0.85rem; }}
        .badge-red {{ display:inline-block; background: rgba(239,68,68,0.15); color:{RED}; border: 1px solid rgba(239,68,68,0.5); border-radius: 10px; padding: 10px 16px; font-weight: 700; font-size: 0.85rem; }}

        .step-node {{ display:flex; flex-direction:column; align-items:center; text-align:center; flex:1; }}
        .step-dot {{ width:20px; height:20px; border-radius:50%; background:{CHARCOAL}; border:3px solid {BORDER}; margin-bottom:8px; }}
        .step-dot.done {{ background:{TEAL}; border-color:{TEAL}; }}
        .step-dot.active {{ background:{GOLD}; border-color:{GOLD}; }}
        .step-label {{ color:{WHITE}; font-size:0.74rem; font-weight:600; }}
        .step-sub {{ color:{MUTED}; font-size:0.66rem; }}

        button[data-baseweb="tab"] {{ font-size: 0.92rem; font-weight: 600; color: {MUTED}; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ color: {TEAL} !important; }}
        div[data-baseweb="tab-highlight"] {{ background-color: {TEAL} !important; }}
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden; }}
        span[data-baseweb="tag"] {{ background-color: {TEAL} !important; }}
        .stButton>button {{ background: linear-gradient(135deg, {TEAL} 0%, #0284C7 100%); color: {WHITE}; border: none; border-radius: 10px; font-weight: 600; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(label: str, value: str, accent: str = "teal") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-accent {accent}"></div>
    </div>
    """


def section_open(title: str, caption: str = ""):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)


def section_close():
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================================
# DATA LOADING — real workbook first, mock fallback second
# ==========================================================================
DATA_FILENAME = "AMECATH_Market_Intelligence.xlsx"
DATA_CANDIDATES = [
    DATA_FILENAME,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILENAME),
    "/mnt/user-data/uploads/AMECATH_Market_Intelligence.xlsx",
    "/mnt/user-data/uploads/AMECATH_Market_Intelligence (1).xlsx",
]

COUNTRY_TO_REGION = {
    "Saudi Arabia": "GCC", "UAE": "GCC", "Qatar": "GCC", "Kuwait": "GCC",
    "Kenya": "East Africa", "Tanzania": "East Africa",
    "Nigeria": "West Africa", "Ghana": "West Africa",
}


def _extract_bed_count(value) -> float:
    if pd.isna(value):
        return float("nan")
    m = re.search(r"\d+", str(value))
    return float(m.group()) if m else float("nan")


def _clean_kol_sheet(raw: pd.DataFrame) -> pd.DataFrame:
    core = ["Department/Specialty", "Key Decision Maker Title (KOL)", "Clinical Pain Point / Priority"]
    trailing = [c for c in raw.columns if c not in core]
    rows = []
    for _, row in raw.iterrows():
        frags = [str(row[c]).strip() for c in trailing if pd.notna(row[c]) and str(row[c]).strip()]
        if not frags:
            vp, pl = "", ""
        elif len(frags) == 1:
            vp, pl = "", frags[0]
        else:
            pl = frags[-1]
            vp = ", ".join(frags[:-1])
        rows.append({**{c: row[c] for c in core}, "Value Proposition": vp, "Target Product Line": pl})
    return pd.DataFrame(rows)


def _mock_dataset():
    """Fallback dataset, matching the real workbook's schema, used only if the file can't be read."""
    hospitals = pd.DataFrame(
        [
            ["GCC", "Saudi Arabia", "King Faisal Specialist Hospital", "Government", "~1200", "Nephrology, Transplant, ICU", "Dialysis Catheters", "Tier 1 Major"],
            ["GCC", "UAE", "Cleveland Clinic Abu Dhabi", "Private", "~360", "Nephrology, Urology, Vascular Surgery", "Urology Stents", "Tier 1 Major"],
            ["East Africa", "Kenya", "Aga Khan University Hospital", "Private", "~254", "Nephrology, ICU, Cardiology", "Dialysis Catheters", "Tier 1 Major"],
            ["West Africa", "Nigeria", "Lagos University Teaching Hospital", "Government", "~761", "Nephrology, Urology, Transplant", "CVC", "Tier 1 Major"],
        ],
        columns=["Region", "Country", "Facility Name", "Sector (Gov/Private/Military)", "Estimated Bed Count",
                 "Key Specialties", "Target Vascular/Urology/Dialysis Products", "Account Tier (Tier 1 Major / Tier 2 Regional)"],
    )
    distributors = pd.DataFrame(
        [
            ["Saudi Arabia", "Attieh Medico", "ICU/ER, Urology, Radiology", "National", "Yes", "Target Partner"],
            ["UAE", "Zahrawi Group", "Urology, Dialysis, Vascular, ICU", "Regional", "Yes", "Target Partner"],
            ["Kenya", "Crown Healthcare", "General Medical Equipment & Supplies", "Regional", "Yes", "Target Partner"],
        ],
        columns=["Country", "Distributor Name", "Specialty Focus", "Market Coverage (National/Regional)",
                 "Tendering Capability (Yes/No)", "Potential Pipeline Status (Target Partner/Prospect)"],
    )
    kol = pd.DataFrame(
        [
            ["Nephrology / Dialysis Unit", "Head of Nephrology", "High catheter-related bloodstream infection rates", "Antimicrobial-coated catheters reducing CRBSI", "Dialysis Catheters"],
            ["ICU / Critical Care", "ICU Director", "CLABSI risk in unstable patients", "Antimicrobial CVCs with rapid-insertion design", "Central Venous Catheters"],
            ["Urology", "Head of Urology", "Stent encrustation and repeat exchange procedures", "Encrustation-resistant ureteral stents", "Urology Stents"],
        ],
        columns=["Department/Specialty", "Key Decision Maker Title (KOL)", "Clinical Pain Point / Priority", "Value Proposition", "Target Product Line"],
    )
    competitive = pd.DataFrame(
        [
            ["AMECATH", "CVC, Hemodialysis Catheters, Urology Stents", "Thermosensitive Polyurethane & Pebax, Smart Grooves >350 mL/min flow", "Mid / Value-for-Money", "Newer brand awareness", "Competitive tender pricing with CE/ISO/SFDA-ready documentation"],
            ["BD (Bard)", "CVCs, Dialysis Catheters", "Premium polyurethane, broad size range", "High / Premium", "Premium pricing limits cost-sensitive tenders", "AMECATH undercuts on price at comparable core specs"],
            ["Teleflex (Arrow)", "CVCs, Dialysis Catheters", "Strong brand equity, antimicrobial options", "High / Premium", "Heavy distributor markup", "Faster tender-ready private labeling"],
        ],
        columns=["Competitor Brand", "Product Category", "Technical Specs (Illustrative Positioning)",
                 "Price Positioning (High/Mid/Low)", "Weaknesses / Gaps", "AMECATH Competitive Advantage"],
    )
    regulatory = pd.DataFrame(
        [
            ["Saudi Arabia", "SFDA + NUPCO", "MDMA2 technical file via GHAD portal; local Authorized Representative required", "CE + ISO support technical file", "6-9 months"],
            ["UAE", "MoHAP / DOH / DHA", "Federal MoHAP registration; emirate-level DOH/DHA registration", "CE + ISO core evidence", "3-6 months"],
            ["Kenya", "PPB", "Recognized-authority abridged review pathway", "CE + ISO accepted", "3-4 months"],
        ],
        columns=["Country", "Target Authority", "Required Certificates / Registration Route",
                 "Compliance Status via CE / ISO / SFDA", "Estimated Access Timeline"],
    )
    forecast = pd.DataFrame(
        [
            ["GCC", "Saudi Arabia", 5528], ["GCC", "UAE", 2884], ["GCC", "Qatar", 1191], ["GCC", "Kuwait", 1673],
            ["East Africa", "Kenya", 2567], ["East Africa", "Tanzania", 1820],
            ["West Africa", "Nigeria", 1706], ["West Africa", "Ghana", 2550],
        ],
        columns=["Region", "Country", "Total Hospital Beds"],
    )
    assumptions = {
        "bed_ratio": 0.04, "sessions_per_week": 3,
        "gcc_penetration": 0.12, "africa_penetration": 0.18,
        "gcc_price": 85, "africa_price": 45,
    }
    return hospitals, distributors, kol, competitive, regulatory, forecast, assumptions


@st.cache_data(show_spinner="Loading market intelligence data...")
def load_data(path: str):
    hospitals = pd.read_excel(path, sheet_name="Sheet1")
    distributors = pd.read_excel(path, sheet_name="Sheet2")
    kol_raw = pd.read_excel(path, sheet_name="Sheet3")
    competitive = pd.read_excel(path, sheet_name="Sheet4")
    regulatory = pd.read_excel(path, sheet_name="Sheet5")

    hospitals.columns = [str(c).strip() for c in hospitals.columns]
    distributors.columns = [str(c).strip() for c in distributors.columns]
    competitive.columns = [str(c).strip() for c in competitive.columns]
    regulatory.columns = [str(c).strip() for c in regulatory.columns]

    hospitals["Bed Count (Est.)"] = hospitals["Estimated Bed Count"].apply(_extract_bed_count)
    distributors["Region"] = distributors["Country"].map(COUNTRY_TO_REGION).fillna("Other")
    kol = _clean_kol_sheet(kol_raw)

    raw6 = pd.read_excel(path, sheet_name="Sheet6", header=None)
    assumptions = {
        "bed_ratio": float(raw6.iloc[1, 1]),
        "sessions_per_week": float(raw6.iloc[2, 1]),
        "gcc_penetration": float(raw6.iloc[3, 1]),
        "africa_penetration": float(raw6.iloc[4, 1]),
        "gcc_price": float(raw6.iloc[5, 1]),
        "africa_price": float(raw6.iloc[6, 1]),
    }
    forecast = pd.read_excel(path, sheet_name="Sheet6", header=11).dropna(how="all")
    forecast = forecast[forecast["Country"].notna()][["Region", "Country", "Total Hospital Beds (Input, from Sheet1)"]]
    forecast.columns = ["Region", "Country", "Total Hospital Beds"]

    return hospitals, distributors, kol, competitive, regulatory, forecast, assumptions


data_source = "Live Workbook"
workbook_path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)

try:
    if workbook_path is None:
        raise FileNotFoundError("Workbook not found in expected locations.")
    hospitals_df, distributors_df, kol_df, competitive_df, regulatory_df, forecast_df, assumptions = load_data(workbook_path)
except Exception:
    hospitals_df, distributors_df, kol_df, competitive_df, regulatory_df, forecast_df, assumptions = _mock_dataset()
    data_source = "Data Simulation Mode (fallback dataset)"

# ==========================================================================
# SIDEBAR
# ==========================================================================
st.sidebar.markdown(
    f"""
    <div style="padding: 6px 0 18px 0;">
        <div style="color:{WHITE}; font-size:1.25rem; font-weight:700;">AMECATH</div>
        <div style="color:{MUTED}; font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase;">
            Executive Intelligence Platform
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(f"**Data Source:** {data_source}")
st.sidebar.markdown("---")
st.sidebar.caption(
    "Regulatory certifications referenced throughout this platform reflect AMECATH's verified "
    "credentials: CE Mark, ISO 13485, and SFDA. No US FDA or Health Canada clearance is held at "
    "this time — see the note on the Executive Market Intelligence tab."
)
st.sidebar.markdown("---")
st.sidebar.caption("AMECATH · Internal Use Only")

# ==========================================================================
# HEADER
# ==========================================================================
st.markdown('<div class="dash-title">Executive Market Intelligence &amp; Operations Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dash-subtitle">Market Intelligence · Competitive &amp; Regulatory Matrix · Financial Modeling · Supply Chain Execution</div>',
    unsafe_allow_html=True,
)
st.write("")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Executive Market Intelligence",
        "🥊 Competitor & Regulatory Matrix",
        "💰 Financial Revenue Model",
        "🔗 SAP Batch & Order Tracking",
        "✈️ Predictive Lead Time & ETA",
        "💎 Dynamic Pricing & Margin",
    ]
)

# ==========================================================================
# TAB 1 — EXECUTIVE MARKET INTELLIGENCE
# ==========================================================================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Target Hospitals", f"{hospitals_df['Facility Name'].nunique()}"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Distributors Mapped", f"{distributors_df['Distributor Name'].nunique()}"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Target Countries", f"{hospitals_df['Country'].nunique()}", "gold"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Verified Certifications", "CE · ISO 13485 · SFDA", "gold"), unsafe_allow_html=True)

    st.markdown(
        f"""<div class="section-card" style="border-left:3px solid {GOLD};">
        <div class="section-caption" style="margin-bottom:0;">
        <b>Regulatory accuracy note:</b> AMECATH's confirmed regulatory footprint, per the Master
        Technical Handbook, is CE Mark, ISO 13485, and SFDA approval. US FDA and Health Canada
        clearance are not currently held and should not be represented as active certifications in
        any external materials until formally obtained.
        </div></div>""",
        unsafe_allow_html=True,
    )

    st.write("")
    section_open("Hospital Directory", "Filter by country, sector, and account tier")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        f_country = st.multiselect("Country", sorted(hospitals_df["Country"].unique()), default=sorted(hospitals_df["Country"].unique()))
    with fc2:
        sector_col = "Sector (Gov/Private/Military)" if "Sector (Gov/Private/Military)" in hospitals_df.columns else "Sector"
        f_sector = st.multiselect("Sector", sorted(hospitals_df[sector_col].dropna().unique()), default=sorted(hospitals_df[sector_col].dropna().unique()))
    with fc3:
        tier_col = "Account Tier (Tier 1 Major / Tier 2 Regional)" if "Account Tier (Tier 1 Major / Tier 2 Regional)" in hospitals_df.columns else "Account Tier"
        f_tier = st.multiselect("Account Tier", sorted(hospitals_df[tier_col].dropna().unique()), default=sorted(hospitals_df[tier_col].dropna().unique()))

    hosp_view = hospitals_df[
        hospitals_df["Country"].isin(f_country)
        & hospitals_df[sector_col].isin(f_sector)
        & hospitals_df[tier_col].isin(f_tier)
    ]
    st.dataframe(hosp_view.drop(columns=["Bed Count (Est.)"], errors="ignore"), use_container_width=True, height=320)
    section_close()

    section_open("Distributor Pipeline", "Filter by market coverage and tendering capability")
    dc1, dc2 = st.columns(2)
    coverage_col = "Market Coverage (National/Regional)" if "Market Coverage (National/Regional)" in distributors_df.columns else "Market Coverage"
    tender_col = "Tendering Capability (Yes/No)" if "Tendering Capability (Yes/No)" in distributors_df.columns else "Tendering Capability"
    with dc1:
        f_coverage = st.multiselect("Market Coverage", sorted(distributors_df[coverage_col].dropna().unique()), default=sorted(distributors_df[coverage_col].dropna().unique()))
    with dc2:
        f_tender = st.multiselect("Tendering Capability", sorted(distributors_df[tender_col].dropna().unique()), default=sorted(distributors_df[tender_col].dropna().unique()))
    dist_view = distributors_df[distributors_df[coverage_col].isin(f_coverage) & distributors_df[tender_col].isin(f_tender)]
    st.dataframe(dist_view, use_container_width=True, height=280)
    section_close()

    section_open("KOL &amp; Clinical Alignment Map", "Clinical pain points mapped directly to AMECATH product solutions")
    cols = st.columns(2)
    for i, (_, row) in enumerate(kol_df.iterrows()):
        with cols[i % 2]:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {TEAL};">
                <div style="color:{TEAL}; font-size:0.72rem; font-weight:700; text-transform:uppercase;">{row['Key Decision Maker Title (KOL)']}</div>
                <div style="color:{WHITE}; font-weight:600; margin-bottom:8px;">{row['Department/Specialty']}</div>
                <div style="color:{MUTED}; font-size:0.72rem; text-transform:uppercase; font-weight:600;">Clinical Pain Point</div>
                <div style="color:#E2E8F0; font-size:0.85rem; margin-bottom:6px;">{row['Clinical Pain Point / Priority']}</div>
                <div style="color:{GOLD}; font-size:0.78rem; font-weight:600;">→ {row['Target Product Line']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    section_close()

# ==========================================================================
# TAB 2 — COMPETITOR & REGULATORY MATRIX
# ==========================================================================
with tab2:
    price_col = "Price Positioning (High/Mid/Low)" if "Price Positioning (High/Mid/Low)" in competitive_df.columns else "Price Positioning"
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(kpi_card("Competitors Benchmarked", f"{competitive_df['Competitor Brand'].nunique()}"), unsafe_allow_html=True)
    with c2:
        premium_share = (competitive_df[price_col].str.contains("High", na=False)).mean() * 100
        st.markdown(kpi_card("Premium-Tier Competitor Share", f"{premium_share:,.0f}%", "gold"), unsafe_allow_html=True)

    section_open("Competitor Benchmark Matrix")
    st.dataframe(competitive_df, use_container_width=True, height=340)
    
    # Fix for Pandas / Plotly version compatibility
    price_counts = competitive_df[price_col].value_counts().reset_index()
    price_counts.columns = ["Positioning", "Count"]

    fig_c = px.bar(
        price_counts,
        x="Positioning", y="Count", template=PLOTLY_TEMPLATE,
    )
    fig_c.update_traces(marker_color=GOLD, marker_line_width=0)
    fig_c.update_layout(height=280, showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})
    section_close()

    section_open("Regulatory Fast-Track Compliance Tracker", "Country-specific registration pathways and estimated market-access timelines")
    st.dataframe(regulatory_df, use_container_width=True, height=320)
    section_close()

# ==========================================================================
# TAB 3 — FINANCIAL REVENUE MODEL (BOTTOM-UP SIMULATOR)
# ==========================================================================
with tab3:
    section_open("Bottom-Up Revenue Simulator", "Adjust assumptions to recalculate Year 1 revenue in real time")

    sl1, sl2, sl3 = st.columns(3)
    with sl1:
        bed_ratio = st.slider("Dialysis/ICU Bed Ratio (%)", 1.0, 10.0, assumptions["bed_ratio"] * 100, 0.5) / 100
    with sl2:
        sessions_wk = st.slider("Weekly Sessions per Bed", 1, 7, int(assumptions["sessions_per_week"]))
    with sl3:
        penetration = st.slider("Target Year-1 Penetration Rate (%)", 1.0, 40.0, assumptions["gcc_penetration"] * 100, 1.0) / 100

    st.caption(
        "A single penetration rate is applied across all markets for this simulator. The underlying "
        "workbook differentiates GCC (premium pricing) from Africa (value pricing) — see the Financial "
        "Forecast sheet for the region-specific baseline."
    )

    model_df = forecast_df.copy()
    model_df["Est. Dialysis/ICU Beds"] = model_df["Total Hospital Beds"] * bed_ratio
    model_df["Annual Sessions"] = model_df["Est. Dialysis/ICU Beds"] * sessions_wk * 52
    model_df["Serviceable Sessions (Yr1)"] = model_df["Annual Sessions"] * penetration
    model_df["Unit Price (USD)"] = model_df["Region"].apply(
        lambda r: assumptions["gcc_price"] if r == "GCC" else assumptions["africa_price"]
    )
    model_df["Projected Revenue (USD)"] = model_df["Serviceable Sessions (Yr1)"] * model_df["Unit Price (USD)"]

    total_revenue = model_df["Projected Revenue (USD)"].sum()
    st.write("")
    st.markdown(kpi_card("Recalculated Year 1 Revenue Target", f"${total_revenue:,.0f}", "gold"), unsafe_allow_html=True)
    st.caption(
        "This is a planning-stage bottom-up estimate driven by the assumptions above, not verified "
        "sales data. Validate bed ratios, session rates, and pricing before board-level commitments."
    )
    section_close()

    col_a, col_b = st.columns(2)
    with col_a:
        section_open("Revenue Breakdown by Country")
        fig_country = px.bar(
            model_df.sort_values("Projected Revenue (USD)"), x="Projected Revenue (USD)", y="Country",
            orientation="h", template=PLOTLY_TEMPLATE,
        )
        fig_country.update_traces(marker_color=TEAL, marker_line_width=0)
        fig_country.update_layout(height=340, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_country, use_container_width=True, config={"displayModeBar": False})
        section_close()
    with col_b:
        section_open("Revenue Breakdown by Region")
        region_rev = model_df.groupby("Region")["Projected Revenue (USD)"].sum().reset_index()
        fig_region = px.pie(region_rev, names="Region", values="Projected Revenue (USD)", hole=0.6, template=PLOTLY_TEMPLATE)
        fig_region.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
        fig_region.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True, config={"displayModeBar": False})
        section_close()

    section_open("Model Detail")
    st.dataframe(model_df, use_container_width=True, height=320)
    section_close()

# ==========================================================================
# TAB 4 — SAP BATCH & ORDER TRACKING ENGINE
# ==========================================================================
STAGES_T4 = [
    "SAP MM\nRaw Material Procurement",
    "SAP PP\nCleanroom Production",
    "SAP QM\nSterilization & QA Release",
    "SAP SD\nExport Logistics",
    "Customs & Delivery",
]
KNOWN_BATCHES = {
    "SAP-FDA-9001": {"stage": 2, "product": "Hemodialysis Catheter", "destination": "Saudi Arabia"},
    "PO-88231": {"stage": 3, "product": "Triple Lumen CVC", "destination": "Kenya"},
    "PO-88240": {"stage": 1, "product": "Urology Stent", "destination": "UAE"},
}

with tab4:
    section_open(
        "Batch / Order Lookup",
        f"Data Simulation Mode — try a reference ID ({', '.join(KNOWN_BATCHES.keys())}) or enter any ID for a simulated status",
    )
    batch_id = st.text_input("Order or Batch ID", value="SAP-FDA-9001", label_visibility="collapsed")
    section_close()

    if batch_id.strip():
        if batch_id in KNOWN_BATCHES:
            info = KNOWN_BATCHES[batch_id]
        else:
            seed = int(hashlib.md5(batch_id.encode()).hexdigest(), 16)
            rnd = random.Random(seed)
            info = {
                "stage": rnd.randint(0, 4),
                "product": rnd.choice(["Hemodialysis Catheter", "Triple Lumen CVC", "Urology Stent", "Midline Catheter"]),
                "destination": rnd.choice(["Saudi Arabia", "UAE", "Kenya", "Nigeria", "Ghana"]),
            }

        stage = info["stage"]
        completion_pct = int(((stage + 1) / len(STAGES_T4)) * 100)

        section_open(f"Batch `{batch_id}`")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Product Line", info["product"]), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Destination", info["destination"]), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Completion", f"{completion_pct}%", "gold"), unsafe_allow_html=True)

        st.write("")
        step_cols = st.columns(len(STAGES_T4))
        for i, (col, label) in enumerate(zip(step_cols, STAGES_T4)):
            with col:
                dot_class = "done" if i < stage else ("active" if i == stage else "")
                sub = "Complete" if i < stage else ("In Progress" if i == stage else "Pending")
                title, subtitle = label.split("\n")
                st.markdown(
                    f"""<div class="step-node">
                    <div class="step-dot {dot_class}"></div>
                    <div class="step-label">{title}</div>
                    <div class="step-sub">{subtitle}</div>
                    <div class="step-sub" style="margin-top:4px; color:{TEAL if i<=stage else MUTED};">{sub}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.progress(completion_pct / 100)

        st.write("")
        st.markdown(
            f"""<div class="badge-green">✔ Quality Compliance: CE Mark &amp; ISO 13485 Released</div>""",
            unsafe_allow_html=True,
        )
        st.caption(
            "Certificate badge reflects AMECATH's verified regulatory credentials (CE Mark, ISO 13485, "
            "SFDA). US FDA / Health Canada clearance badges are intentionally omitted, as those "
            "certifications are not currently held."
        )
        section_close()

# ==========================================================================
# TAB 5 — PREDICTIVE LEAD TIME & ETA ENGINE
# ==========================================================================
with tab5:
    section_open("Shipment Predictor")
    p1, p2, p3 = st.columns(3)
    with p1:
        dest_country = st.selectbox("Target Country", ["Saudi Arabia", "UAE", "Kenya", "Nigeria", "Ghana", "Qatar", "Kuwait", "Tanzania"])
    with p2:
        ship_mode = st.radio("Shipping Mode", ["Air Freight", "Sea Freight"], horizontal=True)
    with p3:
        order_date = st.date_input("Order Date", value=dt.date.today())
    section_close()

    TRANSIT_DAYS = {"Air Freight": 3, "Sea Freight": 28}
    CUSTOMS_DAYS = {
        "Saudi Arabia": 3, "UAE": 2, "Qatar": 3, "Kuwait": 4,
        "Kenya": 6, "Nigeria": 10, "Ghana": 7, "Tanzania": 6,
    }
    PROD_QA_DAYS = 10

    transit = TRANSIT_DAYS[ship_mode]
    customs = CUSTOMS_DAYS[dest_country]
    total_days = PROD_QA_DAYS + transit + customs
    eta = order_date + dt.timedelta(days=total_days)

    section_open("Predicted Shipment Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(kpi_card("Production & QA", f"{PROD_QA_DAYS} days"), unsafe_allow_html=True)
    with m2:
        st.markdown(kpi_card("Transit Time", f"{transit} days", "gold" if ship_mode == "Air Freight" else "red"), unsafe_allow_html=True)
    with m3:
        st.markdown(kpi_card("Customs Clearance", f"{customs} days"), unsafe_allow_html=True)
    with m4:
        st.markdown(kpi_card("Estimated Arrival", eta.strftime("%d %b %Y"), "green"), unsafe_allow_html=True)
    section_close()

    section_open("Cash Conversion Cycle Comparison — Air vs. Sea")
    air_total = PROD_QA_DAYS + TRANSIT_DAYS["Air Freight"] + customs
    sea_total = PROD_QA_DAYS + TRANSIT_DAYS["Sea Freight"] + customs
    acceleration = round(sea_total / air_total, 1)

    lead_time_df = pd.DataFrame([
        {"Mode": "Air Freight", "Days": air_total},
        {"Mode": "Sea Freight", "Days": sea_total}
    ])
    fig_lead = px.bar(
        lead_time_df, x="Days", y="Mode", orientation="h",
        text="Days", template=PLOTLY_TEMPLATE
    )
    fig_lead.update_traces(marker_color=[TEAL, GOLD], textposition="outside")
    fig_lead.update_layout(height=220, showlegend=False, xaxis_title="Total Days to Delivery", yaxis_title="")
    st.plotly_chart(fig_lead, use_container_width=True, config={"displayModeBar": False})
    
    st.info(f"⚡ **Air Freight** accelerates your delivery pipeline by **{acceleration}x** compared to Sea Freight for {dest_country}.")
    section_close()

# ==========================================================================
# TAB 6 — DYNAMIC PRICING & MARGIN LAYER
# ==========================================================================
with tab6:
    section_open("Raw Material Price Sensitivity & COGS Simulator")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        pu_change = st.slider("Polyurethane Cost Variance (%)", -20.0, 50.0, 0.0, 5.0)
    with m_col2:
        nitinol_change = st.slider("Nitinol Wire Cost Variance (%)", -20.0, 50.0, 0.0, 5.0)

    base_cogs = 25.0  # Base cost per unit in USD
    base_price = 65.0 # Base selling price in USD

    # Simple cost impact model
    pu_weight = 0.6
    nitinol_weight = 0.4
    adjusted_cogs = base_cogs * (1 + (pu_change/100 * pu_weight) + (nitinol_change/100 * nitinol_weight))
    margin_usd = base_price - adjusted_cogs
    margin_pct = (margin_usd / base_price) * 100

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi_card("Adjusted COGS / Unit", f"${adjusted_cogs:.2f}"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Gross Margin / Unit", f"${margin_usd:.2f}", "gold"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Gross Margin %", f"{margin_pct:.1f}%", "green" if margin_pct >= 30 else ("gold" if margin_pct >= 20 else "red")), unsafe_allow_html=True)

    st.write("")
    if margin_pct >= 30:
        st.markdown('<div class="badge-green">🟢 Approved Order — Standard Profitability</div>', unsafe_allow_html=True)
    elif margin_pct >= 20:
        st.markdown('<div class="badge-yellow">🟡 Margin Squeezed — Requires Regional VP Approval</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-red">🔴 Order Locked — Repricing Required Immediately</div>', unsafe_allow_html=True)

    section_close()
