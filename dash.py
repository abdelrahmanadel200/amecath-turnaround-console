# -*- coding: utf-8 -*-
"""
AMECATH_MEA_Executive_Dashboard_Pro.py
=======================================
Elite, production-grade, multi-page Streamlit executive dashboard for the
AMECATH MEA Dialysis market-entry workbook.

Run locally with:
    streamlit run AMECATH_MEA_Executive_Dashboard_Pro.py

Requires:
    pip install streamlit pandas plotly openpyxl numpy
"""

import os
import re
import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# 0. PAGE CONFIG (must be the first Streamlit call)
# ============================================================================
st.set_page_config(
    page_title="AMECATH MEA | Executive Dialysis Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# 1. THEME / DESIGN TOKENS
# ============================================================================
NAVY       = "#0A192F"
NAVY_LIGHT = "#112240"
NAVY_CARD  = "#0E1F38"
TEAL       = "#64FFDA"
TEAL_DARK  = "#2FBF9F"
SLATE      = "#8892B0"
SLATE_LT   = "#CCD6F6"
WHITE      = "#E6F1FF"
GOLD       = "#FFD369"
CORAL      = "#FF6B6B"
AMBER      = "#FFB86B"

REGION_COLORS = {
    "GCC": TEAL,
    "Southern Africa": GOLD,
    "North Africa": CORAL,
    "West Africa": AMBER,
    "East Africa": "#7C9CFF",
}

PLOTLY_TEMPLATE = "plotly_dark"

def base_layout(fig, height=440, legend=True):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Helvetica, Arial, sans-serif", color=SLATE_LT, size=13),
        margin=dict(l=10, r=10, t=60, b=10),
        height=height,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(color=SLATE_LT, size=11),
        ) if legend else dict(),
        hoverlabel=dict(bgcolor=NAVY_LIGHT, font_size=12, font_color=WHITE, bordercolor=TEAL),
        title=dict(font=dict(color=WHITE, size=17, family="Inter, sans-serif")),
    )
    fig.update_xaxes(gridcolor="rgba(136,146,176,0.12)", zerolinecolor="rgba(136,146,176,0.12)")
    fig.update_yaxes(gridcolor="rgba(136,146,176,0.12)", zerolinecolor="rgba(136,146,176,0.12)")
    return fig


# ============================================================================
# 2. GLOBAL CSS
# ============================================================================
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"]  {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at 15% 0%, {NAVY_LIGHT} 0%, {NAVY} 45%, #060E1D 100%);
    color: {WHITE};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #081326 0%, {NAVY} 100%);
    border-right: 1px solid rgba(100,255,218,0.12);
}}
section[data-testid="stSidebar"] * {{
    color: {SLATE_LT};
}}

/* Headings */
h1, h2, h3, h4 {{
    color: {WHITE} !important;
    font-weight: 700 !important;
    letter-spacing: 0.2px;
}}
h1 {{ border-bottom: 1px solid rgba(100,255,218,0.18); padding-bottom: 14px; }}

p, span, label, div {{
    color: {SLATE_LT};
}}

/* Metric / KPI cards */
.kpi-card {{
    background: linear-gradient(145deg, {NAVY_CARD} 0%, {NAVY_LIGHT} 100%);
    border: 1px solid rgba(100,255,218,0.16);
    border-radius: 16px;
    padding: 22px 22px 18px 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease;
    height: 100%;
}}
.kpi-card:hover {{
    transform: translateY(-4px);
    border: 1px solid rgba(100,255,218,0.55);
    box-shadow: 0 14px 34px rgba(100,255,218,0.10), 0 8px 24px rgba(0,0,0,0.4);
}}
.kpi-label {{
    color: {SLATE};
    font-size: 12.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    margin-bottom: 8px;
}}
.kpi-value {{
    color: {TEAL};
    font-size: 30px;
    font-weight: 800;
    line-height: 1.15;
}}
.kpi-sub {{
    color: {SLATE};
    font-size: 12.5px;
    margin-top: 6px;
}}

/* Generic glass section container */
.glass-card {{
    background: rgba(17, 34, 64, 0.55);
    border: 1px solid rgba(100,255,218,0.14);
    border-radius: 18px;
    padding: 20px 22px;
    margin-bottom: 18px;
    backdrop-filter: blur(6px);
    box-shadow: 0 8px 22px rgba(0,0,0,0.30);
}}

/* Competitor cards */
.comp-card {{
    background: linear-gradient(160deg, {NAVY_CARD} 0%, {NAVY_LIGHT} 100%);
    border-left: 4px solid {TEAL};
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.30);
    transition: transform 0.2s ease;
}}
.comp-card:hover {{ transform: translateX(4px); }}
.comp-card.benchmark {{ border-left: 4px solid {GOLD}; background: linear-gradient(160deg, rgba(255,211,105,0.08) 0%, {NAVY_LIGHT} 100%); }}
.comp-title {{ color: {WHITE}; font-weight: 700; font-size: 16px; margin-bottom: 2px; }}
.comp-tag {{ display:inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;
             letter-spacing: 0.4px; margin-bottom:10px; }}
.tag-high {{ background: rgba(255,107,107,0.18); color: {CORAL}; }}
.tag-mid  {{ background: rgba(100,255,218,0.18); color: {TEAL}; }}
.tag-low  {{ background: rgba(255,184,107,0.18); color: {AMBER}; }}
.comp-field-label {{ color:{SLATE}; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.6px; margin-top:10px; }}
.comp-field-value {{ color: {SLATE_LT}; font-size: 13.3px; line-height:1.5; }}
.comp-advantage {{ color: {TEAL}; font-size: 13.3px; line-height:1.5; font-weight: 500; }}

/* Section badge */
.section-badge {{
    display:inline-block; background: rgba(100,255,218,0.10); color:{TEAL};
    border: 1px solid rgba(100,255,218,0.35); padding:4px 14px; border-radius:20px;
    font-size:12px; font-weight:700; letter-spacing:0.6px; margin-bottom:10px;
}}

/* Dataframe container */
[data-testid="stDataFrame"] {{
    border: 1px solid rgba(100,255,218,0.14);
    border-radius: 12px;
    overflow: hidden;
}}

hr {{ border-color: rgba(100,255,218,0.15); }}

.stRadio > label, .stSlider > label, .stMultiSelect > label, .stSelectbox > label {{
    color: {TEAL} !important; font-weight:600; font-size: 13px;
}}
div[data-baseweb="select"] > div {{
    background-color: {NAVY_CARD}; border-color: rgba(100,255,218,0.25);
}}

.footer-note {{ color:{SLATE}; font-size:11.5px; text-align:center; padding-top: 30px; }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# 3. DATA LOADING
# ============================================================================
DEFAULT_FILENAME = "AMECATH_MEA_Master_Dialysis_Workbook_Final.xlsx"

SHEETS = {
    "hospitals": "Target_Hospitals",
    "distributors": "Distributors_Pipeline",
    "kols": "KOLs_Decision_Makers",
    "competitors": "Competitor_Analysis",
    "regulatory": "Regulatory_Timelines",
    "forecast": "Master_HD_PD_Forecast",
    "citations": "Data_Sources_Citations",
}


def _locate_workbook_bytes():
    """Locate the workbook on disk next to the script, else offer an uploader."""
    candidates = [DEFAULT_FILENAME, os.path.join(os.path.dirname(__file__), DEFAULT_FILENAME)]
    for c in candidates:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f.read()

    st.sidebar.warning("⚠️ Workbook not found next to the script.")
    uploaded = st.sidebar.file_uploader(
        "Upload AMECATH_MEA_Master_Dialysis_Workbook_Final.xlsx", type=["xlsx"]
    )
    if uploaded is not None:
        return uploaded.read()

    st.error(
        f"Could not locate **{DEFAULT_FILENAME}**. Place it next to this script "
        "or upload it using the sidebar control to continue."
    )
    st.stop()


@st.cache_data(show_spinner="Loading AMECATH MEA workbook…")
def load_all_data(file_bytes: bytes):
    """Parse every sheet of the workbook into clean DataFrames."""
    xl = pd.ExcelFile(io.BytesIO(file_bytes))

    hospitals = pd.read_excel(xl, SHEETS["hospitals"])
    hospitals.columns = [str(c).replace("\n", " ").strip() for c in hospitals.columns]

    distributors = pd.read_excel(xl, SHEETS["distributors"])
    distributors.columns = [str(c).replace("\n", " ").strip() for c in distributors.columns]

    kols = pd.read_excel(xl, SHEETS["kols"])
    kols.columns = [str(c).replace("\n", " ").strip() for c in kols.columns]

    competitors = pd.read_excel(xl, SHEETS["competitors"])
    competitors.columns = [str(c).replace("\n", " ").strip() for c in competitors.columns]

    regulatory = pd.read_excel(xl, SHEETS["regulatory"])
    regulatory.columns = [str(c).replace("\n", " ").strip() for c in regulatory.columns]

    citations = pd.read_excel(xl, SHEETS["citations"], header=1)
    citations.columns = [str(c).replace("\n", " ").strip() for c in citations.columns]
    citations = citations.dropna(how="all")

    def clean_numeric(series):
        return (
            series.astype(str)
            .str.replace("~", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
            .astype(float)
        )

    if "Total Bed Count" in hospitals.columns:
        hospitals["Total Bed Count (Num)"] = clean_numeric(hospitals["Total Bed Count"])
    stations_col = [c for c in hospitals.columns if "Dedicated Dialysis" in c]
    if stations_col:
        hospitals["Dialysis Stations"] = clean_numeric(hospitals[stations_col[0]].astype(str))

    wb_raw = pd.read_excel(xl, SHEETS["forecast"], header=None)
    raw = wb_raw.values.tolist()

    def find_section(keyword, start=0):
        for i in range(start, len(raw)):
            v = raw[i][0]
            if pd.notna(v) and keyword.lower() in str(v).lower():
                return i
        return None

    sec_a = find_section("SECTION A")
    sec_b = find_section("SECTION B")

    def extract_section(title_idx, end_idx):
        header_idx = title_idx + 1
        header_row = raw[header_idx]
        last_col = max(i for i, v in enumerate(header_row) if pd.notna(v)) + 1
        header = [str(h).replace("\n", " ").strip() for h in header_row[:last_col]]
        data = []
        r = header_idx + 1
        stop = end_idx if end_idx is not None else len(raw)
        while r < stop:
            row = raw[r][:last_col]
            if pd.isna(row[0]) and (len(row) < 2 or pd.isna(row[1])):
                break
            data.append(row)
            r += 1
        return pd.DataFrame(data, columns=header)

    hd_full = extract_section(sec_a, sec_b)
    pd_full = extract_section(sec_b, None)

    hd_full.columns = [re.sub(r"\s*\(Patients.*?\)$", "", c).strip() for c in hd_full.columns]

    hd_total_row = hd_full[hd_full["Region"].astype(str).str.upper() == "TOTAL"]
    hd_df = hd_full[hd_full["Region"].astype(str).str.upper() != "TOTAL"].copy()

    pd_total_row = pd_full[pd_full["Country"].astype(str).str.contains("TOTAL", case=False, na=False)]
    pd_df = pd_full[~pd_full["Country"].astype(str).str.contains("TOTAL", case=False, na=False)].copy()

    numeric_cols_hd = [c for c in hd_df.columns if c not in ("Region", "Country", "Citation Reference")]
    for c in numeric_cols_hd:
        hd_df[c] = pd.to_numeric(hd_df[c], errors="coerce")

    numeric_cols_pd = [c for c in pd_df.columns if c not in ("Region", "Country", "Citation Reference")]
    for c in numeric_cols_pd:
        pd_df[c] = pd.to_numeric(pd_df[c], errors="coerce")

    return {
        "hospitals": hospitals,
        "distributors": distributors,
        "kols": kols,
        "competitors": competitors,
        "regulatory": regulatory,
        "citations": citations,
        "hd_forecast": hd_df.reset_index(drop=True),
        "hd_total": hd_total_row.reset_index(drop=True),
        "pd_forecast": pd_df.reset_index(drop=True),
        "pd_total": pd_total_row.reset_index(drop=True),
    }


def parse_timeline_months(text):
    if not isinstance(text, str):
        return (np.nan, np.nan)
    nums = re.findall(r"\d+", text.split("(")[0])
    if len(nums) >= 2:
        return (float(nums[0]), float(nums[1]))
    elif len(nums) == 1:
        return (float(nums[0]), float(nums[0]))
    return (np.nan, np.nan)


def fmt_usd(x, decimals=0):
    if pd.isna(x):
        return "—"
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:,.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:,.1f}K"
    return f"${x:,.{decimals}f}"


def fmt_num(x):
    if pd.isna(x):
        return "—"
    return f"{x:,.0f}"


def kpi_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# 4. LOAD DATA
# ============================================================================
_file_bytes = _locate_workbook_bytes()
DATA = load_all_data(_file_bytes)

hospitals_df   = DATA["hospitals"]
distributors_df = DATA["distributors"]
kols_df        = DATA["kols"]
competitors_df = DATA["competitors"]
regulatory_df  = DATA["regulatory"]
citations_df   = DATA["citations"]
hd_df          = DATA["hd_forecast"]
hd_total       = DATA["hd_total"]
pd_df          = DATA["pd_forecast"]
pd_total       = DATA["pd_total"]

ALL_COUNTRIES = sorted(hospitals_df["Country"].dropna().unique().tolist())


# ============================================================================
# 5. SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.markdown(
    f"""
    <div style="text-align:center; padding: 6px 0 18px 0;">
        <div style="font-size:34px;">🩺</div>
        <div style="color:{TEAL}; font-weight:800; font-size:19px; letter-spacing:0.5px;">AMECATH MEA</div>
        <div style="color:{SLATE}; font-size:12px; letter-spacing:1.2px;">DIALYSIS MARKET INTELLIGENCE</div>
    </div>
    <hr style="margin:0 0 14px 0;">
    """,
    unsafe_allow_html=True,
)

PAGES = [
    "📊 Executive Overview & Market TAM",
    "💰 3-Year Financial Revenue Model",
    "🏥 Target Hospitals & Infrastructure",
    "🤝 Distributors & Channel Pipeline",
    "⚔️ Competitor Intelligence & Positioning",
    "🏛️ Regulatory Timelines & Compliance",
    "📚 Strategic Insights & Data Citations",
]
page = st.sidebar.radio("NAVIGATE", PAGES, label_visibility="visible")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown(
    f"""
    <div style="color:{SLATE}; font-size:11.5px; line-height:1.6;">
    <b style="color:{TEAL};">Coverage</b><br>
    13 MEA Markets · 5 Sub-Regions<br>
    GCC · Southern Africa · North Africa<br>
    West Africa · East Africa
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)


# ============================================================================
# PAGE FUNCTIONS
# ============================================================================
def page_overview():
    st.title("📊 Executive Overview & Market TAM")
    st.markdown('<span class="section-badge">MACRO VIEW · 13 MEA COUNTRIES</span>', unsafe_allow_html=True)

    total_hd_patients = hd_df["Active HD Patients"].sum() if "Active HD Patients" in hd_df.columns else np.nan
    total_pd_patients = pd_df["Active PD Patients"].sum() if "Active PD Patients" in pd_df.columns else np.nan
    total_hd_tam = hd_df["Total HD TAM (USD)"].sum() if "Total HD TAM (USD)" in hd_df.columns else np.nan
    total_pd_tam = pd_df["PD TAM (USD)"].sum() if "PD TAM (USD)" in pd_df.columns else np.nan
    total_tam = total_hd_tam + total_pd_tam

    st_tam = hd_df["ST TAM (USD)"].sum() if "ST TAM (USD)" in hd_df.columns else np.nan
    lt_tam = hd_df["LT TAM (USD)"].sum() if "LT TAM (USD)" in hd_df.columns else np.nan
    st_share = st_tam / (st_tam + lt_tam) * 100 if (st_tam + lt_tam) else np.nan
    lt_share = 100 - st_share

    yr_cols_hd = [c for c in hd_df.columns if c.startswith("Yr") and "HD Rev" in c]
    yr_cols_pd = [c for c in pd_df.columns if c.startswith("Yr") and "PD Rev" in c]
    three_yr_rev = hd_df[yr_cols_hd].sum().sum() + pd_df[yr_cols_pd].sum().sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Active HD Patients", fmt_num(total_hd_patients), f"+{fmt_num(total_pd_patients)} PD patients (GCC)")
    with c2:
        kpi_card("Total Market TAM (USD)", fmt_usd(total_tam), "HD + PD catheter & consumables TAM")
    with c3:
        kpi_card("Short vs Long-Term Share", f"{st_share:,.1f}% / {lt_share:,.1f}%", "Short-Term / Long-Term catheter TAM")
    with c4:
        kpi_card("3-Yr Projected Revenue", fmt_usd(three_yr_rev), "Cumulative Yr1–Yr3, HD + PD")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Regional Market Share — Total HD TAM")
        region_tam = hd_df.groupby("Region", as_index=False)["Total HD TAM (USD)"].sum()
        fig = px.pie(
            region_tam, names="Region", values="Total HD TAM (USD)", hole=0.58,
            color="Region", color_discrete_map=REGION_COLORS,
        )
        fig.update_traces(
            textinfo="percent+label", textfont=dict(color=WHITE, size=12),
            marker=dict(line=dict(color=NAVY, width=2)),
            hovertemplate="<b>%{label}</b><br>TAM: %{value:$,.0f}<br>%{percent}<extra></extra>",
        )
        fig.add_annotation(text=f"<b>{fmt_usd(total_hd_tam)}</b><br><span style='font-size:11px;color={SLATE}'>HD TAM</span>",
                            showarrow=False, font=dict(color=TEAL, size=18), x=0.5, y=0.5)
        base_layout(fig, height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Short-Term vs Long-Term TAM by Country (USD)")
        plot_df = hd_df.sort_values("Total HD TAM (USD)", ascending=False)
        fig = go.Figure()
        fig.add_bar(x=plot_df["Country"], y=plot_df["ST TAM (USD)"], name="Short-Term TAM",
                    marker_color=TEAL, hovertemplate="%{x}<br>ST TAM: %{y:$,.0f}<extra></extra>")
        fig.add_bar(x=plot_df["Country"], y=plot_df["LT TAM (USD)"], name="Long-Term TAM",
                    marker_color=GOLD, hovertemplate="%{x}<br>LT TAM: %{y:$,.0f}<extra></extra>")
        fig.update_layout(barmode="group")
        base_layout(fig, height=420)
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def page_financial():
    st.title("💰 3-Year Financial Revenue Model")
    st.markdown('<span class="section-badge">FORECAST · APPROVED PENETRATION & REGIONAL ASP</span>', unsafe_allow_html=True)

    st.sidebar.markdown(f"<b style='color:{TEAL};'>🎛️ Revenue Simulator</b>", unsafe_allow_html=True)
    pen_multiplier = st.sidebar.slider("Penetration Rate Multiplier", 0.5, 2.0, 1.0, 0.05)
    asp_multiplier = st.sidebar.slider("ASP Multiplier", 0.7, 1.5, 1.0, 0.05)

    yr_labels = ["Yr1", "Yr2", "Yr3"]
    base_rev = {}
    sim_rev = {}
    for yr in yr_labels:
        hd_rev_col = f"{yr} HD Rev (USD)"
        pd_rev_col = f"{yr} PD Rev (USD)"
        base_hd = hd_df[hd_rev_col].sum() if hd_rev_col in hd_df.columns else 0
        base_pd = pd_df[pd_rev_col].sum() if pd_rev_col in pd_df.columns else 0
        base_rev[yr] = base_hd + base_pd
        sim_rev[yr] = (base_hd + base_pd) * pen_multiplier * asp_multiplier

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Yr1 Revenue (Approved)", fmt_usd(base_rev["Yr1"]), "Base case")
    with c2:
        kpi_card("Yr3 Revenue (Approved)", fmt_usd(base_rev["Yr3"]), "Base case")
    with c3:
        kpi_card("Yr3 Revenue (Simulated)", fmt_usd(sim_rev["Yr3"]), f"Pen ×{pen_multiplier:.2f} · ASP ×{asp_multiplier:.2f}")
    with c4:
        delta_pct = (sim_rev["Yr3"] / base_rev["Yr3"] - 1) * 100 if base_rev["Yr3"] else 0
        kpi_card("Simulated Δ vs Approved (Yr3)", f"{delta_pct:+.1f}%", "Sensitivity output")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Growth Trajectory — Approved vs Simulated (Yr1–Yr3, USD)")
        traj = pd.DataFrame({
            "Year": yr_labels * 2,
            "Revenue": [base_rev[y] for y in yr_labels] + [sim_rev[y] for y in yr_labels],
            "Scenario": ["Approved"] * 3 + ["Simulated"] * 3,
        })
        fig = px.line(traj, x="Year", y="Revenue", color="Scenario", markers=True,
                      color_discrete_map={"Approved": SLATE, "Simulated": TEAL})
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        fig.update_traces(fill="tozeroy", selector=dict(name="Simulated"), fillcolor="rgba(100,255,218,0.10)")
        base_layout(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("HD Revenue Stack by Region")
        region_yr = hd_df.groupby("Region")[[f"{y} HD Rev (USD)" for y in yr_labels]].sum().reset_index()
        region_yr_m = region_yr.melt(id_vars="Region", var_name="Year", value_name="Revenue")
        region_yr_m["Year"] = region_yr_m["Year"].str.extract(r"(Yr\d)")
        fig = px.bar(region_yr_m, x="Year", y="Revenue", color="Region", color_discrete_map=REGION_COLORS)
        fig.update_layout(barmode="stack")
        base_layout(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def page_hospitals():
    st.title("🏥 Target Hospitals & Infrastructure")
    st.markdown('<span class="section-badge">HOSPITAL DENSITY · TIER · SECTOR · 13 MARKETS</span>', unsafe_allow_html=True)

    sector_col = [c for c in hospitals_df.columns if "Sector" in c][0]

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        sel_countries = st.multiselect("Filter by Country", ALL_COUNTRIES, default=ALL_COUNTRIES)
    with fcol2:
        sel_tiers = st.multiselect("Filter by Tier", sorted(hospitals_df["Account Tier"].dropna().unique()),
                                    default=sorted(hospitals_df["Account Tier"].dropna().unique()))
    with fcol3:
        max_station = int(np.nanmax(hospitals_df["Dialysis Stations"])) if "Dialysis Stations" in hospitals_df else 100
        station_range = st.slider("Dialysis Station Capacity", 0, max_station, (0, max_station))

    filt = hospitals_df[
        hospitals_df["Country"].isin(sel_countries)
        & hospitals_df["Account Tier"].isin(sel_tiers)
        & hospitals_df["Dialysis Stations"].between(station_range[0], station_range[1])
    ]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Facilities Matched", fmt_num(len(filt)), f"of {len(hospitals_df)} total")
    with c2:
        kpi_card("Tier 1 Major", fmt_num((filt["Account Tier"] == "Tier 1 Major").sum()), "flagship accounts")
    with c3:
        kpi_card("Total Dialysis Stations", fmt_num(filt["Dialysis Stations"].sum()), "in filtered set")
    with c4:
        kpi_card("Countries Covered", fmt_num(filt["Country"].nunique()), "of 13 MEA markets")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"Filtered Facility Directory ({len(filt)} records)")
    st.dataframe(filt.drop(columns=["Total Bed Count (Num)"], errors="ignore"), use_container_width=True, height=460)
    st.markdown("</div>", unsafe_allow_html=True)


def page_distributors():
    st.title("🤝 Distributors & Channel Pipeline")
    st.markdown('<span class="section-badge">CHANNEL NETWORK · TENDERING · PARTNERSHIP STATUS</span>', unsafe_allow_html=True)
    st.dataframe(distributors_df, use_container_width=True, height=440)


def page_competitor():
    st.title("⚔️ Competitor Intelligence & Market Positioning")
    st.markdown('<span class="section-badge">COMPETITIVE MATRIX · GLOBAL MAJORS & VALUE PLAYERS</span>', unsafe_allow_html=True)
    st.dataframe(competitors_df, use_container_width=True, height=420)


def page_regulatory():
    st.title("🏛️ Regulatory Timelines & Compliance Tracker")
    st.markdown('<span class="section-badge">COUNTRY ROADMAP · AUTHORITIES · CE / ISO 13485 PATHWAYS</span>', unsafe_allow_html=True)
    st.dataframe(regulatory_df, use_container_width=True, height=460)


def page_insights():
    st.title("📚 Strategic Insights, Methodology & Data Citations")
    st.markdown('<span class="section-badge">EXECUTIVE SYNTHESIS · METHODOLOGY · VERIFIED SOURCES</span>', unsafe_allow_html=True)
    st.dataframe(citations_df, use_container_width=True, height=520)


# ============================================================================
# 6. ROUTER
# ============================================================================
ROUTES = {
    PAGES[0]: page_overview,
    PAGES[1]: page_financial,
    PAGES[2]: page_hospitals,
    PAGES[3]: page_distributors,
    PAGES[4]: page_competitor,
    PAGES[5]: page_regulatory,
    PAGES[6]: page_insights,
}

ROUTES[page]()
