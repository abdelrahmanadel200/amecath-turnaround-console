"""
AMECATH — Executive Market Expansion Dashboard (GCC & Africa)
Run with: streamlit run executive_dashboard.py

Expects a workbook named "حصر.xlsx" in the same folder as this script,
containing three sheets:
    Sheet1 -> Target Hospitals (GCC & Africa)
    Sheet2 -> Medical Distributors & Tendering Capabilities
    Sheet3 -> Decision Makers (KOLs) & Clinical Value Propositions
"""

import os
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================================
# PAGE CONFIG
# ==========================================================================
st.set_page_config(
    page_title="AMECATH | Executive Market Dashboard",
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

CHART_COLORWAY = [TEAL, GOLD, "#22D3EE", "#F59E0B", "#38BDF8", "#FBBF24", "#0284C7"]

# ==========================================================================
# CUSTOM CSS
# ==========================================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp {{
            background: linear-gradient(180deg, {NAVY} 0%, #0B1220 100%);
            color: {WHITE};
        }}

        section[data-testid="stSidebar"] {{
            background: {CHARCOAL};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] * {{
            color: {WHITE} !important;
        }}

        #MainMenu, footer, header {{visibility: hidden;}}

        h1, h2, h3, h4 {{
            color: {WHITE} !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
        }}

        .dash-title {{
            font-size: 2.1rem;
            font-weight: 700;
            background: linear-gradient(90deg, {WHITE} 0%, {TEAL} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }}
        .dash-subtitle {{
            color: {MUTED};
            font-size: 0.95rem;
            font-weight: 400;
            margin-top: 2px;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}

        .kpi-card {{
            background: linear-gradient(155deg, {CARD_BG} 0%, {CHARCOAL} 100%);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 22px 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.25);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            height: 100%;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(0,0,0,0.35);
        }}
        .kpi-label {{
            color: {MUTED};
            font-size: 0.78rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
        }}
        .kpi-value {{
            color: {WHITE};
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1.1;
        }}
        .kpi-accent {{
            display: inline-block;
            width: 34px;
            height: 3px;
            border-radius: 3px;
            background: {TEAL};
            margin-top: 12px;
        }}
        .kpi-accent.gold {{ background: {GOLD}; }}

        .section-card {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 20px 22px;
            margin-bottom: 18px;
        }}
        .section-title {{
            color: {WHITE};
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .section-caption {{
            color: {MUTED};
            font-size: 0.8rem;
            margin-bottom: 14px;
        }}

        button[data-baseweb="tab"] {{
            font-size: 0.95rem;
            font-weight: 600;
            color: {MUTED};
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {TEAL} !important;
        }}
        div[data-baseweb="tab-highlight"] {{
            background-color: {TEAL} !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 12px;
            overflow: hidden;
        }}

        .kol-card {{
            background: linear-gradient(155deg, {CARD_BG} 0%, {CHARCOAL} 100%);
            border: 1px solid {BORDER};
            border-left: 3px solid {TEAL};
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }}
        .kol-role {{
            color: {TEAL};
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 4px;
        }}
        .kol-dept {{
            color: {WHITE};
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .kol-row {{
            margin-bottom: 8px;
        }}
        .kol-row-label {{
            color: {MUTED};
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        .kol-row-value {{
            color: #E2E8F0;
            font-size: 0.88rem;
            line-height: 1.4;
        }}
        .kol-pill {{
            display: inline-block;
            background: rgba(217, 119, 6, 0.15);
            color: {GOLD};
            border: 1px solid rgba(217, 119, 6, 0.35);
            border-radius: 20px;
            padding: 3px 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 4px;
        }}

        span[data-baseweb="tag"] {{
            background-color: {TEAL} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================================
# CONSTANTS
# ==========================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILENAME = "AMECATH_Market_Intelligence.xlsx"
DATA_CANDIDATES = [
    os.path.join(SCRIPT_DIR, DATA_FILENAME),
    DATA_FILENAME,
    os.path.join("/mnt/user-data/uploads", DATA_FILENAME),
]

COUNTRY_TO_REGION = {
    "Saudi Arabia": "GCC",
    "UAE": "GCC",
    "Qatar": "GCC",
    "Kuwait": "GCC",
    "Kenya": "East Africa",
    "Tanzania": "East Africa",
    "Nigeria": "West Africa",
    "Ghana": "West Africa",
}

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
# DATA LOADING
# ==========================================================================
def _find_workbook_path():
    for path in DATA_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


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


@st.cache_data(show_spinner="Loading AMECATH_Market_Intelligence.xlsx ...")
def load_workbook(path: str):
    hospitals = pd.read_excel(path, sheet_name="Sheet1")
    distributors = pd.read_excel(path, sheet_name="Sheet2")
    kol_raw = pd.read_excel(path, sheet_name="Sheet3")
    competitive = pd.read_excel(path, sheet_name="Sheet4")
    regulatory = pd.read_excel(path, sheet_name="Sheet5")
    forecast = pd.read_excel(path, sheet_name="Sheet6", header=11).dropna(how="all")
    forecast = forecast[forecast["Country"].notna()]

    hospitals.columns = [str(c).strip() for c in hospitals.columns]
    distributors.columns = [str(c).strip() for c in distributors.columns]
    competitive.columns = [str(c).strip() for c in competitive.columns]
    regulatory.columns = [str(c).strip() for c in regulatory.columns]
    forecast.columns = [str(c).strip() for c in forecast.columns]

    hospitals["Bed Count (Est.)"] = hospitals["Estimated Bed Count"].apply(_extract_bed_count)
    distributors["Region"] = distributors["Country"].map(COUNTRY_TO_REGION).fillna("Other")
    kol = _clean_kol_sheet(kol_raw)

    return hospitals, distributors, kol, competitive, regulatory, forecast


workbook_path = _find_workbook_path()

if workbook_path is None:
    st.error(
        f"Couldn't find **{DATA_FILENAME}**. Place it in the same folder as this script, "
        "or upload it below."
    )
    uploaded = st.file_uploader("Upload AMECATH_Market_Intelligence.xlsx", type=["xlsx"])
    if uploaded is None:
        st.stop()
    hospitals_df = pd.read_excel(uploaded, sheet_name="Sheet1")
    distributors_df = pd.read_excel(uploaded, sheet_name="Sheet2")
    kol_raw_df = pd.read_excel(uploaded, sheet_name="Sheet3")
    competitive_df = pd.read_excel(uploaded, sheet_name="Sheet4")
    regulatory_df = pd.read_excel(uploaded, sheet_name="Sheet5")
    forecast_df = pd.read_excel(uploaded, sheet_name="Sheet6", header=11).dropna(how="all")
    forecast_df = forecast_df[forecast_df["Country"].notna()]
    hospitals_df["Bed Count (Est.)"] = hospitals_df["Estimated Bed Count"].apply(_extract_bed_count)
    distributors_df["Region"] = distributors_df["Country"].map(COUNTRY_TO_REGION).fillna("Other")
    kol_df = _clean_kol_sheet(kol_raw_df)
else:
    hospitals_df, distributors_df, kol_df, competitive_df, regulatory_df, forecast_df = load_workbook(workbook_path)

# ==========================================================================
# SIDEBAR FILTERS
# ==========================================================================
st.sidebar.markdown(
    f"""
    <div style="padding: 6px 0 18px 0;">
        <div style="color:{WHITE}; font-size:1.3rem; font-weight:700;">AMECATH</div>
        <div style="color:{MUTED}; font-size:0.75rem; letter-spacing:0.08em; text-transform:uppercase;">
            Market Expansion Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("**🌍 Region**")
all_regions = sorted(hospitals_df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Region", options=all_regions, default=all_regions, label_visibility="collapsed"
)

st.sidebar.markdown("**📍 Country**")
country_pool = sorted(
    hospitals_df.loc[hospitals_df["Region"].isin(selected_regions), "Country"].dropna().unique().tolist()
)
selected_countries = st.sidebar.multiselect(
    "Country", options=country_pool, default=country_pool, label_visibility="collapsed"
)

st.sidebar.markdown("**🏛️ Sector**")
all_sectors = sorted(hospitals_df["Sector (Gov/Private/Military)"].dropna().unique().tolist())
selected_sectors = st.sidebar.multiselect(
    "Sector", options=all_sectors, default=all_sectors, label_visibility="collapsed"
)

st.sidebar.markdown("---")
if st.sidebar.button("↺ Reset Filters", use_container_width=True):
    st.rerun()

st.sidebar.markdown(
    f"""<div style="color:{MUTED}; font-size:0.72rem; margin-top:10px;">
    Source: {DATA_FILENAME}<br>Sheets: Hospitals · Distributors · KOL Matrix · Competitive · Regulatory · Forecast
    </div>""",
    unsafe_allow_html=True,
)

# Apply filters
hosp_f = hospitals_df[
    hospitals_df["Region"].isin(selected_regions)
    & hospitals_df["Country"].isin(selected_countries)
    & hospitals_df["Sector (Gov/Private/Military)"].isin(selected_sectors)
]

dist_f = distributors_df[
    distributors_df["Region"].isin(selected_regions) & distributors_df["Country"].isin(selected_countries)
]

fore_f = forecast_df[
    forecast_df["Region"].isin(selected_regions) & forecast_df["Country"].isin(selected_countries)
]
REVENUE_COL = "Projected Annual Revenue - Literal Formula (USD)"
ADJ_REVENUE_COL = "Realistic Catheter-Adjusted Revenue (USD)"

# ==========================================================================
# HEADER
# ==========================================================================
st.markdown('<div class="dash-title">Executive Market Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dash-subtitle">AMECATH · GCC &amp; Africa Expansion Intelligence</div>',
    unsafe_allow_html=True,
)
st.write("")


def kpi_card(label: str, value: str, accent: str = "teal") -> str:
    accent_class = "kpi-accent" if accent == "teal" else "kpi-accent gold"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="{accent_class}"></div>
    </div>
    """


def empty_state(message: str = "No records match the current filter selection."):
    st.markdown(
        f"""<div class="section-card" style="text-align:center; color:{MUTED};">
        ⚠️ {message}
        </div>""",
        unsafe_allow_html=True,
    )


# ==========================================================================
# TOP-LEVEL KPI STRIP (respects sidebar filters, spans all six modules)
# ==========================================================================
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.markdown(kpi_card("Total Target Hospitals", f"{hosp_f['Facility Name'].nunique()}"), unsafe_allow_html=True)
with g2:
    beds_total = hosp_f["Bed Count (Est.)"].sum()
    st.markdown(kpi_card("Total Beds Covered", f"{beds_total:,.0f}" if pd.notna(beds_total) else "—", "gold"), unsafe_allow_html=True)
with g3:
    st.markdown(kpi_card("Target Distributors", f"{dist_f['Distributor Name'].nunique()}"), unsafe_allow_html=True)
with g4:
    baseline_rev = fore_f[REVENUE_COL].sum() if not fore_f.empty else 0
    st.markdown(
        kpi_card("Baseline Revenue Projection (Yr1)", f"${baseline_rev:,.0f}" if baseline_rev else "—", "gold"),
        unsafe_allow_html=True,
    )
st.write("")

# ==========================================================================
# TABS
# ==========================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🏥  Target Hospitals & Market Density",
        "🚚  Distributors & Tender Coverage",
        "🎯  Decision Makers & Value Prop Matrix",
        "⚔️  Competitive Benchmarking",
        "📜  Regulatory Roadmap",
        "💰  Financial Forecast",
    ]
)

# --------------------------------------------------------------------------
# TAB 1 — HOSPITALS
# --------------------------------------------------------------------------
with tab1:
    if hosp_f.empty:
        empty_state()
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("Total Hospitals", f"{hosp_f['Facility Name'].nunique()}"), unsafe_allow_html=True)
        with c2:
            avg_beds = hosp_f["Bed Count (Est.)"].mean()
            st.markdown(
                kpi_card("Avg. Bed Capacity (Est.)", f"{avg_beds:,.0f}" if pd.notna(avg_beds) else "—", "gold"),
                unsafe_allow_html=True,
            )
        with c3:
            total_beds = hosp_f["Bed Count (Est.)"].sum()
            st.markdown(
                kpi_card("Total Bed Capacity (Est.)", f"{total_beds:,.0f}" if pd.notna(total_beds) else "—"),
                unsafe_allow_html=True,
            )
        with c4:
            tier1_share = (
                hosp_f["Account Tier (Tier 1 Major / Tier 2 Regional)"].str.contains("Tier 1", na=False)
            ).mean() * 100
            st.markdown(kpi_card("Tier 1 Accounts", f"{tier1_share:,.0f}%", "gold"), unsafe_allow_html=True)

        st.write("")
        col_a, col_b = st.columns([1.3, 1])

        with col_a:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Hospital Density by Region</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-caption">Facility count across covered markets</div>', unsafe_allow_html=True
            )
            density = hosp_f.groupby("Region")["Facility Name"].nunique().reset_index(name="Hospitals")
            fig = px.bar(density, x="Region", y="Hospitals", text="Hospitals", template=PLOTLY_TEMPLATE)
            fig.update_traces(marker_color=TEAL, textposition="outside", marker_line_width=0, width=0.45)
            fig.update_layout(height=340, showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Sector Breakdown</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-caption">Gov / Private / Military mix</div>', unsafe_allow_html=True)
            sector_mix = hosp_f["Sector (Gov/Private/Military)"].value_counts().reset_index()
            sector_mix.columns = ["Sector", "Count"]
            fig2 = px.pie(sector_mix, names="Sector", values="Count", hole=0.62, template=PLOTLY_TEMPLATE)
            fig2.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
            fig2.update_layout(height=340, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Bed Capacity by Country</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Estimated total beds, aggregated by country</div>', unsafe_allow_html=True
        )
        beds_by_country = (
            hosp_f.groupby("Country")["Bed Count (Est.)"].sum().reset_index().sort_values("Bed Count (Est.)")
        )
        fig3 = px.bar(beds_by_country, x="Bed Count (Est.)", y="Country", orientation="h", template=PLOTLY_TEMPLATE)
        fig3.update_traces(marker_color=GOLD, marker_line_width=0)
        fig3.update_layout(height=360, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Filtered Hospital Directory</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-caption">{len(hosp_f)} of {len(hospitals_df)} facilities shown</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            hosp_f.drop(columns=["Bed Count (Est.)"]).reset_index(drop=True),
            use_container_width=True,
            height=380,
        )
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 2 — DISTRIBUTORS
# --------------------------------------------------------------------------
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
            target_partners = (
                dist_f["Potential Pipeline Status (Target Partner/Prospect)"].str.strip() == "Target Partner"
            ).sum()
            st.markdown(kpi_card("Target Partners", f"{target_partners}"), unsafe_allow_html=True)

        st.write("")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Market Coverage</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-caption">National vs. Regional distributor footprint</div>',
                unsafe_allow_html=True,
            )
            coverage = dist_f["Market Coverage (National/Regional)"].value_counts().reset_index()
            coverage.columns = ["Coverage", "Count"]
            fig4 = px.bar(coverage, x="Coverage", y="Count", text="Count", template=PLOTLY_TEMPLATE)
            fig4.update_traces(marker_color=TEAL, textposition="outside", marker_line_width=0, width=0.4)
            fig4.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Pipeline Status Mix</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-caption">Target Partner vs. Prospect</div>', unsafe_allow_html=True)
            pipeline = dist_f["Potential Pipeline Status (Target Partner/Prospect)"].value_counts().reset_index()
            pipeline.columns = ["Status", "Count"]
            fig5 = px.pie(pipeline, names="Status", values="Count", hole=0.62, template=PLOTLY_TEMPLATE)
            fig5.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
            fig5.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Distributor Directory</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-caption">{len(dist_f)} of {len(distributors_df)} partners shown</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(dist_f.reset_index(drop=True), use_container_width=True, height=380)
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 3 — KOL / VALUE PROP MATRIX
# --------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Search &amp; Filter</div>', unsafe_allow_html=True)
    search_term = st.text_input(
        "Search by department, KOL title, or product line",
        placeholder="e.g. Nephrology, ICU Director, Dialysis Catheters ...",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

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

# --------------------------------------------------------------------------
# TAB 4 — COMPETITIVE BENCHMARKING
# --------------------------------------------------------------------------
with tab4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Search &amp; Filter</div>', unsafe_allow_html=True)
    comp_search = st.text_input(
        "Search by brand, product category, or price positioning",
        placeholder="e.g. Fresenius, CVC, Premium ...",
        label_visibility="collapsed",
        key="comp_search",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    comp_view = competitive_df.copy()
    if comp_search.strip():
        mask = (
            comp_view["Competitor Brand"].str.contains(comp_search, case=False, na=False)
            | comp_view["Product Category"].str.contains(comp_search, case=False, na=False)
            | comp_view["Price Positioning (High/Mid/Low)"].str.contains(comp_search, case=False, na=False)
        )
        comp_view = comp_view[mask]

    if comp_view.empty:
        empty_state("No competitors match your search.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(kpi_card("Competitors Mapped", f"{comp_view['Competitor Brand'].nunique()}"), unsafe_allow_html=True)
        with c2:
            premium_share = (comp_view["Price Positioning (High/Mid/Low)"].str.contains("High", na=False)).mean() * 100
            st.markdown(kpi_card("Premium-Tier Share", f"{premium_share:,.0f}%", "gold"), unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Price Positioning Mix</div>', unsafe_allow_html=True)
        pos_mix = comp_view["Price Positioning (High/Mid/Low)"].value_counts().reset_index()
        pos_mix.columns = ["Positioning", "Count"]
        fig6 = px.bar(pos_mix, x="Positioning", y="Count", text="Count", template=PLOTLY_TEMPLATE)
        fig6.update_traces(marker_color=GOLD, textposition="outside", marker_line_width=0, width=0.4)
        fig6.update_layout(height=300, showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Competitive Benchmarking Matrix</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-caption">{len(comp_view)} of {len(competitive_df)} competitors shown &mdash; '
            "positioning is directional, based on public brand reputation, not published price lists</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(comp_view.reset_index(drop=True), use_container_width=True, height=420)
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 5 — REGULATORY ROADMAP
# --------------------------------------------------------------------------
with tab5:
    st.markdown(
        f"""<div class="section-card" style="border-left:3px solid {TEAL}; padding:14px 20px;">
        <div class="section-caption" style="margin-bottom:0;">
        This tab covers all 8 regulatory target markets from Module 1 (including Egypt and South Africa), which is a
        wider set than the current hospital target list in Tab 1 &mdash; it is not filtered by the sidebar's
        Region/Country/Sector controls.
        </div>
        </div>""",
        unsafe_allow_html=True,
    )
    reg_view = regulatory_df
    if reg_view.empty:
        empty_state("No regulatory records available.")
    else:
        st.markdown(kpi_card("Markets Mapped", f"{reg_view['Country'].nunique()}"), unsafe_allow_html=True)
        st.write("")
        cols = st.columns(2)
        for i, (_, row) in enumerate(reg_view.iterrows()):
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

# --------------------------------------------------------------------------
# TAB 6 — FINANCIAL FORECAST
# --------------------------------------------------------------------------
with tab6:
    if fore_f.empty:
        empty_state()
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                kpi_card("Yr1 Revenue — Literal Formula", f"${fore_f[REVENUE_COL].sum():,.0f}"), unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                kpi_card("Yr1 Revenue — Realistic Adjusted", f"${fore_f[ADJ_REVENUE_COL].sum():,.0f}", "gold"),
                unsafe_allow_html=True,
            )
        with c3:
            total_sessions = fore_f["Annual Procedures/Sessions"].sum()
            st.markdown(kpi_card("Annual Dialysis Sessions Modeled", f"{total_sessions:,.0f}"), unsafe_allow_html=True)

        st.markdown(
            f"""<div class="section-card" style="border-left:3px solid {GOLD};">
            <div class="section-title">⚠️ Modeling Caveat</div>
            <div class="section-caption" style="margin-bottom:0;">
            The <b>Literal Formula</b> figure follows the requested model exactly
            (Beds × Sessions/Week × 52 × Penetration % × Unit Price) and treats every dialysis session as one billable unit.
            Clinically, a single catheter serves many sessions before replacement — the <b>Realistic Adjusted</b> figure applies
            a catheter-replacement-rate factor as a more conservative secondary estimate. Both are planning-stage assumptions,
            not verified market data — validate bed ratios, session rates, and pricing before using for board commitments.
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Revenue Projection by Country (Literal Formula)</div>', unsafe_allow_html=True)
            rev_by_country = fore_f[["Country", REVENUE_COL]].sort_values(REVENUE_COL)
            fig7 = px.bar(rev_by_country, x=REVENUE_COL, y="Country", orientation="h", template=PLOTLY_TEMPLATE)
            fig7.update_traces(marker_color=TEAL, marker_line_width=0)
            fig7.update_layout(height=360, showlegend=False, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Revenue Split — GCC vs. Africa</div>', unsafe_allow_html=True)
            region_split = fore_f.groupby("Region")[REVENUE_COL].sum().reset_index()
            fig8 = px.pie(region_split, names="Region", values=REVENUE_COL, hole=0.62, template=PLOTLY_TEMPLATE)
            fig8.update_traces(textinfo="percent+label", marker_line_color=NAVY, marker_line_width=2)
            fig8.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Bottom-Up Forecast Detail</div>', unsafe_allow_html=True)
        st.dataframe(fore_f.reset_index(drop=True), use_container_width=True, height=380)
        st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown(
    f'<div style="text-align:center; color:{MUTED}; font-size:0.75rem; padding: 10px 0 30px 0;">'
    "AMECATH Executive Dashboard &middot; Internal Use Only"
    "</div>",
    unsafe_allow_html=True,
)
