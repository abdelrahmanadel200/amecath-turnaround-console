"""
AMECATH — Executive Dashboard (Merged Build)
Run with: streamlit run executive_dashboard.py

Reads "AMECATH_Market_Intelligence.xlsx" (Sheet1-Sheet6). Falls back to an
embedded mock dataset with the same schema if the file is missing or
unreadable, so the app never crashes on load.

Tabs:
  1. Target Hospitals & Market Density
  2. Distributors & Tender Coverage
  3. Decision Makers & Value Prop Matrix (KOL)
  4. Competitive Benchmarking
  5. Regulatory Roadmap
  6. Financial Forecast (workbook baseline + interactive what-if simulator)
  7. SAP Batch & Order Tracking (data simulation)
  8. Predictive Lead Time & ETA (data simulation)
  9. Dynamic Pricing & Margin (data simulation)

Tabs 1-6 respect the sidebar Region/Country/Sector filters and are driven by
the workbook. Tabs 7-9 are operational simulators with their own local
controls, intentionally independent of the sidebar filters, and are clearly
labeled as Data Simulation Mode since they are not wired to a live ERP feed.
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
    page_title="AMECATH | Executive Dashboard",
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
# CUSTOM CSS
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
            font-size: 2.1rem; font-weight: 700;
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
        .kpi-value {{ color: {WHITE}; font-size: 1.9rem; font-weight: 700; line-height: 1.15; }}
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

        .kol-card {{
            background: linear-gradient(155deg, {CARD_BG} 0%, {CHARCOAL} 100%);
            border: 1px solid {BORDER}; border-left: 3px solid {TEAL}; border-radius: 14px;
            padding: 18px 20px; margin-bottom: 14px;
        }}
        .kol-role {{ color: {TEAL}; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }}
        .kol-dept {{ color: {WHITE}; font-size: 1.05rem; font-weight: 600; margin-bottom: 10px; }}
        .kol-row {{ margin-bottom: 8px; }}
        .kol-row-label {{ color: {MUTED}; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }}
        .kol-row-value {{ color: #E2E8F0; font-size: 0.88rem; line-height: 1.4; }}
        .kol-pill {{
            display: inline-block; background: rgba(217, 119, 6, 0.15); color: {GOLD};
            border: 1px solid rgba(217, 119, 6, 0.35); border-radius: 20px; padding: 3px 12px;
            font-size: 0.75rem; font-weight: 600; margin-top: 4px;
        }}

        .badge-green {{ display:inline-block; background: rgba(34,197,94,0.12); color:{GREEN}; border: 1px solid rgba(34,197,94,0.4); border-radius: 10px; padding: 10px 16px; font-weight: 700; font-size: 0.85rem; }}
        .badge-yellow {{ display:inline-block; background: rgba(234,179,8,0.12); color:{YELLOW}; border: 1px solid rgba(234,179,8,0.4); border-radius: 10px; padding: 10px 16px; font-weight: 700; font-size: 0.85rem; }}
        .badge-red {{ display:inline-block; background: rgba(239,68,68,0.15); color:{RED}; border: 1px solid rgba(239,68,68,0.5); border-radius: 10px; padding: 10px 16px; font-weight: 700; font-size: 0.85rem; }}

        .step-node {{ display:flex; flex-direction:column; align-items:center; text-align:center; flex:1; }}
        .step-dot {{ width:20px; height:20px; border-radius:50%; background:{CHARCOAL}; border:3px solid {BORDER}; margin-bottom:8px; }}
        .step-dot.done {{ background:{TEAL}; border-color:{TEAL}; }}
        .step-dot.active {{ background:{GOLD}; border-color:{GOLD}; }}
        .step-label {{ color:{WHITE}; font-size:0.74rem; font-weight:600; }}
        .step-sub {{ color:{MUTED}; font-size:0.66rem; }}

        button[data-baseweb="tab"] {{ font-size: 0.9rem; font-weight: 600; color: {MUTED}; }}
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
    accent_class = "kpi-accent" if accent == "teal" else f"kpi-accent {accent}"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="{accent_class}"></div>
    </div>
    """


def section_open(title: str, caption: str = ""):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)


def section_close():
    st.markdown("</div>", unsafe_allow_html=True)


def empty_state(message: str = "No records match the current filter selection."):
    st.markdown(
        f"""<div class="section-card" style="text-align:center; color:{MUTED};">⚠️ {message}</div>""",
        unsafe_allow_html=True,
    )


def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from column names so lookups like df['Region'] never fail
    on a stray 'Region ' or leading space introduced by copy/paste or Excel export."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def safe_filter(df: pd.DataFrame, col: str, selected_values) -> pd.DataFrame:
    """Filter df by col only if col actually exists in df. If it doesn't, return
    df unfiltered rather than raising a KeyError — missing dimensions are treated
    as 'no filter applied' rather than a crash."""
    if col not in df.columns:
        return df
    if not selected_values:
        return df.iloc[0:0]  # nothing selected -> empty result, not an error
    return df[df[col].isin(selected_values)]


def safe_unique(df: pd.DataFrame, col: str) -> list:
    """Sorted unique values for a column, or an empty list if the column is missing."""
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().unique().tolist())


# ==========================================================================
# CONSTANTS
# ==========================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILENAME = "AMECATH_Market_Intelligence.xlsx"
DATA_CANDIDATES = [
    os.path.join(SCRIPT_DIR, DATA_FILENAME),
    DATA_FILENAME,
    os.path.join("/mnt/user-data/uploads", DATA_FILENAME),
    "/mnt/user-data/uploads/AMECATH_Market_Intelligence (1).xlsx",
]

COUNTRY_TO_REGION = {
    "Saudi Arabia": "GCC", "UAE": "GCC", "Qatar": "GCC", "Kuwait": "GCC",
    "Kenya": "East Africa", "Tanzania": "East Africa",
    "Nigeria": "West Africa", "Ghana": "West Africa",
}
REVENUE_COL = "Projected Annual Revenue - Literal Formula (USD)"
ADJ_REVENUE_COL = "Realistic Catheter-Adjusted Revenue (USD)"

# ==========================================================================
# DATA-CLEANING UTILITIES
# ==========================================================================
def _extract_bed_count(value) -> float:
    """Pull the first integer out of strings like '~1200' or '~500 (flagship)'."""
    if pd.isna(value):
        return float("nan")
    match = re.search(r"\d+", str(value))
    return float(match.group()) if match else float("nan")


def _clean_kol_sheet(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Sheet3 was pasted from a comma-containing CSV, so some rows have their
    Value Proposition text spilled into extra unnamed trailing columns.
    Heuristic: for each row, collect all non-null values from column index 3
    onward; the LAST one is the Target Product Line, everything before that
    (joined back together) is the Value Proposition.
    """
    core_cols = ["Department/Specialty", "Key Decision Maker Title (KOL)", "Clinical Pain Point / Priority"]
    trailing_cols = [c for c in raw.columns if c not in core_cols]

    cleaned_rows = []
    for _, row in raw.iterrows():
        fragments = [str(row[c]).strip() for c in trailing_cols if pd.notna(row[c]) and str(row[c]).strip()]
        if not fragments:
            value_prop, product_line = "", ""
        elif len(fragments) == 1:
            value_prop, product_line = "", fragments[0]
        else:
            product_line = fragments[-1]
            value_prop = ", ".join(fragments[:-1])
        cleaned_rows.append(
            {
                "Department/Specialty": row["Department/Specialty"],
                "Key Decision Maker Title (KOL)": row["Key Decision Maker Title (KOL)"],
                "Clinical Pain Point / Priority": row["Clinical Pain Point / Priority"],
                "Value Proposition": value_prop,
                "Target Product Line": product_line,
            }
        )
    return pd.DataFrame(cleaned_rows)


def _mock_dataset():
    """Fallback dataset (same schema as the real workbook) used only if the file can't be read."""
    hospitals = pd.DataFrame(
        [
            ["GCC", "Saudi Arabia", "King Faisal Specialist Hospital", "Government", "~1200", "Nephrology, Transplant, ICU", "Hemodialysis Catheters", "Tier 1 Major"],
            ["GCC", "UAE", "Cleveland Clinic Abu Dhabi", "Private", "~360", "Nephrology, Urology, Vascular Surgery", "Urology Stents", "Tier 1 Major"],
            ["East Africa", "Kenya", "Aga Khan University Hospital", "Private", "~254", "Nephrology, ICU, Cardiology", "Hemodialysis Catheters", "Tier 1 Major"],
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
            ["Nephrology / Dialysis Unit", "Head of Nephrology", "High catheter-related bloodstream infection rates", "Antimicrobial-coated catheters reducing CRBSI", "Hemodialysis Catheters"],
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
    assumptions = {
        "bed_ratio": 0.04, "sessions_per_week": 3,
        "gcc_penetration": 0.12, "africa_penetration": 0.18,
        "gcc_price": 85, "africa_price": 45, "cath_per_100_sessions": 2,
    }
    forecast = pd.DataFrame(
        [
            ["GCC", "Saudi Arabia", 5528], ["GCC", "UAE", 2884], ["GCC", "Qatar", 1191], ["GCC", "Kuwait", 1673],
            ["East Africa", "Kenya", 2567], ["East Africa", "Tanzania", 1820],
            ["West Africa", "Nigeria", 1706], ["West Africa", "Ghana", 2550],
        ],
        columns=["Region", "Country", "Total Hospital Beds (Input, from Sheet1)"],
    )
    forecast["Est. Dialysis/ICU Beds"] = forecast["Total Hospital Beds (Input, from Sheet1)"] * assumptions["bed_ratio"]
    forecast["Annual Procedures/Sessions"] = forecast["Est. Dialysis/ICU Beds"] * assumptions["sessions_per_week"] * 52
    forecast["Applied Yr-1 Penetration Rate"] = forecast["Region"].apply(
        lambda r: assumptions["gcc_penetration"] if r == "GCC" else assumptions["africa_penetration"]
    )
    forecast["Serviceable Sessions (Yr1 Units, per formula)"] = forecast["Annual Procedures/Sessions"] * forecast["Applied Yr-1 Penetration Rate"]
    forecast["Blended Unit Price (USD)"] = forecast["Region"].apply(
        lambda r: assumptions["gcc_price"] if r == "GCC" else assumptions["africa_price"]
    )
    forecast[REVENUE_COL] = forecast["Serviceable Sessions (Yr1 Units, per formula)"] * forecast["Blended Unit Price (USD)"]
    forecast[ADJ_REVENUE_COL] = forecast[REVENUE_COL] * (assumptions["cath_per_100_sessions"] / 100)

    # Apply the same cleanup used on the real workbook, so the mock path can
    # never drift out of sync with the live-data schema:
    hospitals = _clean_columns(hospitals)
    distributors = _clean_columns(distributors)
    kol = _clean_columns(kol)
    competitive = _clean_columns(competitive)
    regulatory = _clean_columns(regulatory)
    forecast = _clean_columns(forecast)

    # distributors_df needs a Region column for the sidebar filter to work on
    # this fallback path too — derive it the same way the real loader does,
    # rather than hardcoding it, so the two paths can't drift apart again.
    if "Region" not in distributors.columns and "Country" in distributors.columns:
        distributors["Region"] = distributors["Country"].map(COUNTRY_TO_REGION).fillna("Other")

    return hospitals, distributors, kol, competitive, regulatory, forecast, assumptions


@st.cache_data(show_spinner="Loading AMECATH_Market_Intelligence.xlsx ...")
def load_workbook(path: str):
    hospitals = pd.read_excel(path, sheet_name="Sheet1")
    distributors = pd.read_excel(path, sheet_name="Sheet2")
    kol_raw = pd.read_excel(path, sheet_name="Sheet3")
    competitive = pd.read_excel(path, sheet_name="Sheet4")
    regulatory = pd.read_excel(path, sheet_name="Sheet5")

    hospitals = _clean_columns(hospitals)
    distributors = _clean_columns(distributors)
    kol_raw = _clean_columns(kol_raw)
    competitive = _clean_columns(competitive)
    regulatory = _clean_columns(regulatory)

    hospitals["Bed Count (Est.)"] = hospitals["Estimated Bed Count"].apply(_extract_bed_count)
    if "Country" in distributors.columns:
        distributors["Region"] = distributors["Country"].map(COUNTRY_TO_REGION).fillna("Other")
    kol = _clean_kol_sheet(kol_raw)

    # Sheet6: assumptions block (rows 2-8) + per-country detail table (header row 12)
    raw6 = pd.read_excel(path, sheet_name="Sheet6", header=None)
    assumptions = {
        "bed_ratio": float(raw6.iloc[1, 1]),
        "sessions_per_week": float(raw6.iloc[2, 1]),
        "gcc_penetration": float(raw6.iloc[3, 1]),
        "africa_penetration": float(raw6.iloc[4, 1]),
        "gcc_price": float(raw6.iloc[5, 1]),
        "africa_price": float(raw6.iloc[6, 1]),
        "cath_per_100_sessions": float(raw6.iloc[7, 1]),
    }
    forecast = pd.read_excel(path, sheet_name="Sheet6", header=11).dropna(how="all")
    forecast = forecast[forecast["Country"].notna()]
    forecast.columns = [str(c).strip() for c in forecast.columns]

    return hospitals, distributors, kol, competitive, regulatory, forecast, assumptions


# ==========================================================================
# LOAD DATA (real workbook first, mock fallback second)
# ==========================================================================
data_source = "Live Workbook"
workbook_path = next((p for p in DATA_CANDIDATES if os.path.exists(p)), None)

try:
    if workbook_path is None:
        raise FileNotFoundError("Workbook not found in expected locations.")
    hospitals_df, distributors_df, kol_df, competitive_df, regulatory_df, forecast_df, assumptions = load_workbook(workbook_path)
except Exception:
    hospitals_df, distributors_df, kol_df, competitive_df, regulatory_df, forecast_df, assumptions = _mock_dataset()
    data_source = "Data Simulation Mode (embedded fallback dataset)"

if workbook_path is None and data_source == "Live Workbook":
    data_source = "Data Simulation Mode (embedded fallback dataset)"

# ==========================================================================
# SIDEBAR
# ==========================================================================
st.sidebar.markdown(
    f"""
    <div style="padding: 6px 0 18px 0;">
        <div style="color:{WHITE}; font-size:1.3rem; font-weight:700;">AMECATH</div>
        <div style="color:{MUTED}; font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase;">
            Executive Intelligence Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(f"**Data Source:** {data_source}")
st.sidebar.markdown("---")

st.sidebar.markdown("**🌍 Region**")
all_regions = safe_unique(hospitals_df, "Region")
selected_regions = st.sidebar.multiselect("Region", options=all_regions, default=all_regions, label_visibility="collapsed")

st.sidebar.markdown("**📍 Country**")
if "Region" in hospitals_df.columns and "Country" in hospitals_df.columns:
    country_pool = sorted(hospitals_df.loc[hospitals_df["Region"].isin(selected_regions), "Country"].dropna().unique().tolist())
else:
    country_pool = safe_unique(hospitals_df, "Country")
selected_countries = st.sidebar.multiselect("Country", options=country_pool, default=country_pool, label_visibility="collapsed")

st.sidebar.markdown("**🏛️ Sector**")
SECTOR_COL = "Sector (Gov/Private/Military)" if "Sector (Gov/Private/Military)" in hospitals_df.columns else "Sector"
all_sectors = safe_unique(hospitals_df, SECTOR_COL)
selected_sectors = st.sidebar.multiselect("Sector", options=all_sectors, default=all_sectors, label_visibility="collapsed")

st.sidebar.markdown("---")
if st.sidebar.button("↺ Reset Filters", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Verified AMECATH certifications: CE Mark, ISO 13485, SFDA. US FDA / Health Canada clearance "
    "are not currently held and are intentionally not referenced anywhere in this dashboard."
)
st.sidebar.caption("Tabs 7-9 (SAP Tracking, Predictive ETA, Dynamic Pricing) are Data Simulation Mode tools, independent of the filters above.")

# Apply filters — safe_filter no-ops (returns the frame unfiltered) if a
# dimension column doesn't exist on a given dataframe, instead of raising
# a KeyError. This is what fixes the crash: distributors_df is filtered by
# "Region" and "Country" only if those columns are actually present.
hosp_f = hospitals_df
hosp_f = safe_filter(hosp_f, "Region", selected_regions)
hosp_f = safe_filter(hosp_f, "Country", selected_countries)
hosp_f = safe_filter(hosp_f, SECTOR_COL, selected_sectors)

dist_f = distributors_df
dist_f = safe_filter(dist_f, "Region", selected_regions)
dist_f = safe_filter(dist_f, "Country", selected_countries)

fore_f = forecast_df
fore_f = safe_filter(fore_f, "Region", selected_regions)
fore_f = safe_filter(fore_f, "Country", selected_countries)

# ==========================================================================
# HEADER
# ==========================================================================
st.markdown('<div class="dash-title">AMECATH Executive Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dash-subtitle">Market Intelligence · Competitive &amp; Regulatory Matrix · Financial Modeling · Supply Chain Execution</div>',
    unsafe_allow_html=True,
)
st.write("")

g1, g2, g3, g4 = st.columns(4)
with g1:
    st.markdown(kpi_card("Total Target Hospitals", f"{hosp_f['Facility Name'].nunique()}"), unsafe_allow_html=True)
with g2:
    beds_total = hosp_f["Bed Count (Est.)"].sum() if "Bed Count (Est.)" in hosp_f.columns else float("nan")
    st.markdown(kpi_card("Total Beds Covered", f"{beds_total:,.0f}" if pd.notna(beds_total) else "—", "gold"), unsafe_allow_html=True)
with g3:
    st.markdown(kpi_card("Target Distributors", f"{dist_f['Distributor Name'].nunique()}"), unsafe_allow_html=True)
with g4:
    baseline_rev = fore_f[REVENUE_COL].sum() if REVENUE_COL in fore_f.columns and not fore_f.empty else 0
    st.markdown(kpi_card("Baseline Revenue Projection (Yr1)", f"${baseline_rev:,.0f}" if baseline_rev else "—", "gold"), unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    [
        "🏥 Hospitals",
        "🚚 Distributors",
        "🎯 KOL Matrix",
        "⚔️ Competitive",
        "📜 Regulatory",
        "💰 Financial Forecast",
        "🔗 SAP Tracking",
        "✈️ Predictive ETA",
        "💎 Pricing & Margin",
    ]
)

# ==========================================================================
# TAB 1 — HOSPITALS
# ==========================================================================
with tab1:
    if hosp_f.empty:
        empty_state()
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("Total Hospitals", f"{hosp_f['Facility Name'].nunique()}"), unsafe_allow_html=True)
        with c2:
            avg_beds = hosp_f["Bed Count (Est.)"].mean()
            st.markdown(kpi_card("Avg. Bed Capacity (Est.)", f"{avg_beds:,.0f}" if pd.notna(avg_beds) else "—", "gold"), unsafe_allow_html=True)
        with c3:
            total_beds = hosp_f["Bed Count (Est.)"].sum()
            st.markdown(kpi_card("Total Bed Capacity (Est.)", f"{total_beds:,.0f}" if pd.notna(total_beds) else "—"), unsafe_allow_html=True)
        with c4:
            tier_col = "Account Tier (Tier 1 Major / Tier 2 Regional)"
            tier1_share = hosp_f[tier_col].str.contains("Tier 1", na=False).mean() * 100 if tier_col in hosp_f.columns else 0
            st.markdown(kpi_card("Tier 1 Accounts", f"{tier1_share:,.0f}%", "gold"), unsafe_allow_html=True)

        st.write("")
        col_a, col_b = st.columns([1.3, 1])
        with col_a:
            section_open("Hospital Density by Region", "Facility count across covered markets")
            density = hosp_f.groupby("Region")["Facility Name"].nunique().reset_index(name="Hospitals")
            fig = px.bar(density, x="Region", y="Hospitals", text="Hospitals", template=PLOTLY_TEMPLATE)
            fig.update_traces(marker_color=TEAL, textposition="outside", marker_line_width=0, width=0.45)
            fig.update_layout(height=340, showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            section_close()
        with col_b:
            section_open("Sector Breakdown", "Gov / Private / Military mix")
            if SECTOR_COL in hosp_f.columns:
                sector_mix = hosp_f[SECTOR_COL].value_counts().reset_index()
                sector_mix.columns = ["Sector", "Count"]
                fig2 = px.pie(sector_mix, names="Sector", values="Count", hole=0.62, template=PLOTLY_TEMPLATE)
                fig2.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
                fig2.update_layout(height=340, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            else:
                st.caption("Sector data not available in the current dataset.")
            section_close()

        section_open("Bed Capacity by Country", "Estimated total beds, aggregated by country")
        beds_by_country = hosp_f.groupby("Country")["Bed Count (Est.)"].sum().reset_index().sort_values("Bed Count (Est.)")
        fig3 = px.bar(beds_by_country, x="Bed Count (Est.)", y="Country", orientation="h", template=PLOTLY_TEMPLATE)
        fig3.update_traces(marker_color=GOLD, marker_line_width=0)
        fig3.update_layout(height=360, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        section_close()

        section_open("Filtered Hospital Directory", f"{len(hosp_f)} of {len(hospitals_df)} facilities shown")
        st.dataframe(hosp_f.drop(columns=["Bed Count (Est.)"], errors="ignore").reset_index(drop=True), use_container_width=True, height=380)
        section_close()

# ==========================================================================
# TAB 2 — DISTRIBUTORS
# ==========================================================================
with tab2:
    if dist_f.empty:
        empty_state()
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Total Distributors", f"{dist_f['Distributor Name'].nunique()}"), unsafe_allow_html=True)
        with c2:
            tender_capable = (dist_f["Tendering Capability (Yes/No)"].str.strip() == "Yes").sum()
            st.markdown(kpi_card("Tender-Capable Partners", f"{tender_capable}", "gold"), unsafe_allow_html=True)
        with c3:
            target_partners = (dist_f["Potential Pipeline Status (Target Partner/Prospect)"].str.strip() == "Target Partner").sum()
            st.markdown(kpi_card("Target Partners", f"{target_partners}"), unsafe_allow_html=True)

        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            section_open("Market Coverage", "National vs. Regional distributor footprint")
            coverage = dist_f["Market Coverage (National/Regional)"].value_counts().reset_index()
            coverage.columns = ["Coverage", "Count"]
            fig4 = px.bar(coverage, x="Coverage", y="Count", text="Count", template=PLOTLY_TEMPLATE)
            fig4.update_traces(marker_color=TEAL, textposition="outside", marker_line_width=0, width=0.4)
            fig4.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            section_close()
        with col_b:
            section_open("Pipeline Status Mix", "Target Partner vs. Prospect")
            pipeline = dist_f["Potential Pipeline Status (Target Partner/Prospect)"].value_counts().reset_index()
            pipeline.columns = ["Status", "Count"]
            fig5 = px.pie(pipeline, names="Status", values="Count", hole=0.62, template=PLOTLY_TEMPLATE)
            fig5.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
            fig5.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
            section_close()

        section_open("Distributor Directory", f"{len(dist_f)} of {len(distributors_df)} partners shown")
        st.dataframe(dist_f.reset_index(drop=True), use_container_width=True, height=380)
        section_close()

# ==========================================================================
# TAB 3 — KOL MATRIX
# ==========================================================================
with tab3:
    section_open("Search &amp; Filter")
    search_term = st.text_input(
        "Search by department, KOL title, or product line",
        placeholder="e.g. Nephrology, ICU Director, Dialysis Catheters ...",
        label_visibility="collapsed",
    )
    section_close()

    kol_view = kol_df.copy()
    if search_term.strip():
        mask = (
            kol_view["Department/Specialty"].str.contains(search_term, case=False, na=False)
            | kol_view["Key Decision Maker Title (KOL)"].str.contains(search_term, case=False, na=False)
            | kol_view["Target Product Line"].str.contains(search_term, case=False, na=False)
        )
        kol_view = kol_view[mask]

    if kol_view.empty:
        empty_state("No decision-maker records match your search.")
    else:
        st.markdown(kpi_card("Mapped Clinical Roles", f"{len(kol_view)}"), unsafe_allow_html=True)
        st.write("")
        cols = st.columns(2)
        for i, (_, row) in enumerate(kol_view.iterrows()):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="kol-card">
                        <div class="kol-role">{row['Key Decision Maker Title (KOL)']}</div>
                        <div class="kol-dept">{row['Department/Specialty']}</div>
                        <div class="kol-row">
                            <div class="kol-row-label">Clinical Pain Point</div>
                            <div class="kol-row-value">{row['Clinical Pain Point / Priority']}</div>
                        </div>
                        <div class="kol-row">
                            <div class="kol-row-label">Value Proposition</div>
                            <div class="kol-row-value">{row['Value Proposition'] or '&mdash;'}</div>
                        </div>
                        <div class="kol-pill">{row['Target Product Line']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==========================================================================
# TAB 4 — COMPETITIVE BENCHMARKING
# ==========================================================================
with tab4:
    section_open("Search &amp; Filter")
    comp_search = st.text_input(
        "Search by brand, product category, or price positioning",
        placeholder="e.g. Fresenius, CVC, Premium ...",
        label_visibility="collapsed",
        key="comp_search",
    )
    section_close()

    comp_view = competitive_df.copy()
    price_col = "Price Positioning (High/Mid/Low)"
    if comp_search.strip():
        mask = (
            comp_view["Competitor Brand"].str.contains(comp_search, case=False, na=False)
            | comp_view["Product Category"].str.contains(comp_search, case=False, na=False)
            | comp_view[price_col].str.contains(comp_search, case=False, na=False)
        )
        comp_view = comp_view[mask]

    if comp_view.empty:
        empty_state("No competitors match your search.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(kpi_card("Competitors Mapped", f"{comp_view['Competitor Brand'].nunique()}"), unsafe_allow_html=True)
        with c2:
            premium_share = (comp_view[price_col].str.contains("High", na=False)).mean() * 100
            st.markdown(kpi_card("Premium-Tier Share", f"{premium_share:,.0f}%", "gold"), unsafe_allow_html=True)

        st.write("")
        section_open("Price Positioning Mix")
        pos_mix = comp_view[price_col].value_counts().reset_index()
        pos_mix.columns = ["Positioning", "Count"]
        fig6 = px.bar(pos_mix, x="Positioning", y="Count", text="Count", template=PLOTLY_TEMPLATE)
        fig6.update_traces(marker_color=GOLD, textposition="outside", marker_line_width=0, width=0.4)
        fig6.update_layout(height=300, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        section_close()

        section_open(
            "Competitive Benchmarking Matrix",
            f"{len(comp_view)} of {len(competitive_df)} competitors shown &mdash; positioning is directional, not published price lists",
        )
        st.dataframe(comp_view.reset_index(drop=True), use_container_width=True, height=420)
        section_close()

# ==========================================================================
# TAB 5 — REGULATORY ROADMAP
# ==========================================================================
with tab5:
    st.markdown(
        f"""<div class="section-card" style="border-left:3px solid {TEAL}; padding:14px 20px;">
        <div class="section-caption" style="margin-bottom:0;">
        This tab covers all regulatory target markets and is not filtered by the sidebar's
        Region/Country/Sector controls, since it may include markets not yet in the hospital target list.
        Verified AMECATH credentials referenced throughout: CE Mark, ISO 13485, SFDA.
        </div></div>""",
        unsafe_allow_html=True,
    )
    if regulatory_df.empty:
        empty_state("No regulatory records available.")
    else:
        st.markdown(kpi_card("Markets Mapped", f"{regulatory_df['Country'].nunique()}"), unsafe_allow_html=True)
        st.write("")
        cols = st.columns(2)
        for i, (_, row) in enumerate(regulatory_df.iterrows()):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div class="kol-card">
                        <div class="kol-role">{row['Target Authority']}</div>
                        <div class="kol-dept">{row['Country']}</div>
                        <div class="kol-row">
                            <div class="kol-row-label">Required Certificates / Route</div>
                            <div class="kol-row-value">{row['Required Certificates / Registration Route']}</div>
                        </div>
                        <div class="kol-row">
                            <div class="kol-row-label">CE / ISO / SFDA Leverage</div>
                            <div class="kol-row-value">{row['Compliance Status via CE / ISO / SFDA']}</div>
                        </div>
                        <div class="kol-pill">⏱ {row['Estimated Access Timeline']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==========================================================================
# TAB 6 — FINANCIAL FORECAST (workbook baseline + interactive simulator)
# ==========================================================================
with tab6:
    if fore_f.empty:
        empty_state()
    else:
        section_open("Workbook Baseline (as filtered by sidebar)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Yr1 Revenue — Literal Formula", f"${fore_f[REVENUE_COL].sum():,.0f}"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Yr1 Revenue — Realistic Adjusted", f"${fore_f[ADJ_REVENUE_COL].sum():,.0f}", "gold"), unsafe_allow_html=True)
        with c3:
            total_sessions = fore_f["Annual Procedures/Sessions"].sum() if "Annual Procedures/Sessions" in fore_f.columns else 0
            st.markdown(kpi_card("Annual Dialysis Sessions Modeled", f"{total_sessions:,.0f}"), unsafe_allow_html=True)
        st.caption(
            "The Literal Formula figure follows Beds × Sessions/Week × 52 × Penetration % × Unit Price, treating "
            "every session as one billable unit. The Realistic Adjusted figure applies a catheter-replacement-rate "
            "factor as a more conservative estimate. Both are planning-stage assumptions, not verified sales data."
        )

        col_a, col_b = st.columns(2)
        with col_a:
            rev_by_country = fore_f[["Country", REVENUE_COL]].sort_values(REVENUE_COL)
            fig7 = px.bar(rev_by_country, x=REVENUE_COL, y="Country", orientation="h", template=PLOTLY_TEMPLATE)
            fig7.update_traces(marker_color=TEAL, marker_line_width=0)
            fig7.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="", title="Revenue by Country")
            st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
        with col_b:
            region_split = fore_f.groupby("Region")[REVENUE_COL].sum().reset_index()
            fig8 = px.pie(region_split, names="Region", values=REVENUE_COL, hole=0.62, template=PLOTLY_TEMPLATE)
            fig8.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
            fig8.update_layout(height=320, showlegend=False, title="Revenue Split by Region")
            st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
        section_close()

        section_open("What-If Simulator", "Adjust assumptions to recalculate Year 1 revenue in real time")
        sl1, sl2, sl3 = st.columns(3)
        with sl1:
            sim_bed_ratio = st.slider("Dialysis/ICU Bed Ratio (%)", 1.0, 10.0, assumptions["bed_ratio"] * 100, 0.5) / 100
        with sl2:
            sim_sessions = st.slider("Weekly Sessions per Bed", 1, 7, int(assumptions["sessions_per_week"]))
        with sl3:
            sim_penetration_gcc = st.slider("GCC Penetration Rate (%)", 1.0, 40.0, assumptions["gcc_penetration"] * 100, 1.0) / 100
        sim_penetration_africa = st.slider("Africa Penetration Rate (%)", 1.0, 40.0, assumptions["africa_penetration"] * 100, 1.0) / 100

        sim_df = fore_f[["Region", "Country", "Total Hospital Beds (Input, from Sheet1)"]].copy()
        sim_df["Est. Beds"] = sim_df["Total Hospital Beds (Input, from Sheet1)"] * sim_bed_ratio
        sim_df["Annual Sessions"] = sim_df["Est. Beds"] * sim_sessions * 52
        sim_df["Penetration"] = sim_df["Region"].apply(lambda r: sim_penetration_gcc if r == "GCC" else sim_penetration_africa)
        sim_df["Serviceable Sessions"] = sim_df["Annual Sessions"] * sim_df["Penetration"]
        sim_df["Unit Price (USD)"] = sim_df["Region"].apply(
            lambda r: assumptions["gcc_price"] if r == "GCC" else assumptions["africa_price"]
        )
        sim_df["Simulated Revenue (USD)"] = sim_df["Serviceable Sessions"] * sim_df["Unit Price (USD)"]

        st.write("")
        st.markdown(kpi_card("Simulated Year 1 Revenue", f"${sim_df['Simulated Revenue (USD)'].sum():,.0f}", "gold"), unsafe_allow_html=True)
        st.dataframe(sim_df, use_container_width=True, height=300)
        section_close()

        section_open("Bottom-Up Forecast Detail (Workbook Baseline)")
        st.dataframe(fore_f.reset_index(drop=True), use_container_width=True, height=340)
        section_close()

# ==========================================================================
# TAB 7 — SAP BATCH & ORDER TRACKING (Data Simulation Mode)
# ==========================================================================
STAGES_T7 = [
    "SAP MM\nRaw Material Procurement",
    "SAP PP\nCleanroom Production",
    "SAP QM\nSterilization & QA Release",
    "SAP SD\nExport Logistics",
    "Customs & Delivery",
]
KNOWN_BATCHES = {
    "SAP-45001298": {"stage": 2, "product": "Hemodialysis Catheter", "destination": "Saudi Arabia"},
    "PO-88231": {"stage": 3, "product": "Triple Lumen CVC", "destination": "Kenya"},
    "PO-88240": {"stage": 1, "product": "Urology Stent", "destination": "UAE"},
}

with tab7:
    section_open(
        "Batch / Order Lookup",
        f"Data Simulation Mode — try a reference ID ({', '.join(KNOWN_BATCHES.keys())}) or enter any ID for a simulated status",
    )
    batch_id = st.text_input("Order or Batch ID", value="SAP-45001298", label_visibility="collapsed")
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
        completion_pct = int(((stage + 1) / len(STAGES_T7)) * 100)

        section_open(f"Batch `{batch_id}`")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Product Line", info["product"]), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Destination", info["destination"]), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Completion", f"{completion_pct}%", "gold"), unsafe_allow_html=True)

        st.write("")
        step_cols = st.columns(len(STAGES_T7))
        for i, (col, label) in enumerate(zip(step_cols, STAGES_T7)):
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
        st.markdown('<div class="badge-green">✔ Quality Compliance: CE Mark &amp; ISO 13485 Released</div>', unsafe_allow_html=True)
        section_close()

# ==========================================================================
# TAB 8 — PREDICTIVE LEAD TIME & ETA (Data Simulation Mode)
# ==========================================================================
with tab8:
    section_open("Shipment Predictor", "Data Simulation Mode — lead times below are illustrative planning assumptions")
    p1, p2, p3 = st.columns(3)
    with p1:
        dest_country = st.selectbox("Target Country", ["Saudi Arabia", "UAE", "Kenya", "Nigeria", "Ghana", "Qatar", "Kuwait", "Tanzania"])
    with p2:
        ship_mode = st.radio("Shipping Mode", ["Air Freight", "Sea Freight"], horizontal=True)
    with p3:
        order_date = st.date_input("Order Date", value=dt.date.today())
    section_close()

    TRANSIT_DAYS = {"Air Freight": 3, "Sea Freight": 28}
    CUSTOMS_DAYS = {"Saudi Arabia": 3, "UAE": 2, "Qatar": 3, "Kuwait": 4, "Kenya": 6, "Nigeria": 10, "Ghana": 7, "Tanzania": 6}
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

    fig_cc = go.Figure()
    fig_cc.add_trace(go.Bar(y=["Sea Freight"], x=[sea_total], orientation="h", marker_color=RED, name="Sea"))
    fig_cc.add_trace(go.Bar(y=["Air Freight"], x=[air_total], orientation="h", marker_color=GREEN, name="Air"))
    fig_cc.update_layout(template=PLOTLY_TEMPLATE, height=200, showlegend=False, xaxis_title="Total Cash Conversion Days", margin=dict(l=10, r=10, t=10, b=30))
    st.plotly_chart(fig_cc, use_container_width=True, config={"displayModeBar": False})
    st.markdown(kpi_card(f"Cash Conversion Acceleration — {dest_country}", f"{acceleration}x faster via Air Freight", "gold"), unsafe_allow_html=True)
    section_close()

# ==========================================================================
# TAB 9 — DYNAMIC PRICING & MARGIN (Data Simulation Mode)
# ==========================================================================
with tab9:
    section_open("Order Cost Basis", "Data Simulation Mode — replace with actual bill-of-materials costing before pricing approval")
    b1, b2, b3 = st.columns(3)
    with b1:
        order_value = st.number_input("Order Value (USD)", value=42000, step=1000)
    with b2:
        base_cogs_pct = st.slider("Baseline COGS (% of Order Value)", 40, 85, 62)
    with b3:
        polymer_share = st.slider("Polyurethane/Pebax Share of COGS (%)", 10, 60, 35)
    section_close()

    section_open("Raw Material Price Sensitivity")
    s1, s2 = st.columns(2)
    with s1:
        polyurethane_change = st.slider("Polyurethane Cost Change (%)", -30, 60, 0)
    with s2:
        nitinol_change = st.slider("Nitinol Wire Cost Change (%)", -30, 60, 0)
    section_close()

    base_cogs = order_value * (base_cogs_pct / 100)
    nitinol_share = 100 - polymer_share
    polymer_cost = base_cogs * (polymer_share / 100)
    nitinol_cost = base_cogs * (nitinol_share / 100)
    adjusted_cogs = polymer_cost * (1 + polyurethane_change / 100) + nitinol_cost * (1 + nitinol_change / 100)
    gross_margin_usd = order_value - adjusted_cogs
    gross_margin_pct = (gross_margin_usd / order_value) * 100 if order_value else 0

    section_open("Live COGS &amp; Gross Margin")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(kpi_card("Adjusted COGS", f"${adjusted_cogs:,.0f}"), unsafe_allow_html=True)
    with m2:
        st.markdown(kpi_card("Gross Margin (USD)", f"${gross_margin_usd:,.0f}", "gold"), unsafe_allow_html=True)
    with m3:
        st.markdown(kpi_card("Gross Margin (%)", f"{gross_margin_pct:,.1f}%", "gold"), unsafe_allow_html=True)

    st.write("")
    if gross_margin_pct > 30:
        st.markdown('<div class="badge-green">🟢 APPROVED ORDER — Margin Above Threshold</div>', unsafe_allow_html=True)
    elif gross_margin_pct >= 20:
        st.markdown('<div class="badge-yellow">🟡 MARGIN SQUEEZED — Requires Management Approval</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-red">🔴 ORDER LOCKED — Repricing Required</div>', unsafe_allow_html=True)
    section_close()

st.write("")
st.markdown(
    f'<div style="text-align:center; color:{MUTED}; font-size:0.72rem; padding: 10px 0 30px 0;">'
    "AMECATH Executive Dashboard &middot; Internal Use Only"
    "</div>",
    unsafe_allow_html=True,
)
