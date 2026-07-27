"""
AMECATH — Operational Turnaround, Recovery & Market Expansion Console
Executive Enterprise Dashboard
"""

import hashlib
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================================
# PAGE CONFIGURATION
# ==========================================================================
st.set_page_config(
    page_title="AMECATH | Enterprise Turnaround & Market Console",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================
# BRAND PALETTE & STYLING
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

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .slide-wrap {{ animation: fadeIn 0.45s ease; }}

        .dash-title {{
            font-size: 2.0rem; font-weight: 700;
            background: linear-gradient(90deg, {WHITE} 0%, {TEAL} 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;
        }}
        .dash-subtitle {{
            color: {MUTED}; font-size: 0.92rem; margin-top: 2px;
            letter-spacing: 0.02em; text-transform: uppercase;
        }}

        .kpi-card {{
            background: linear-gradient(155deg, {CARD_BG} 0%, {CHARCOAL} 100%);
            border: 1px solid {BORDER}; border-radius: 16px; padding: 20px 22px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.25); height: 100%;
            animation: fadeIn 0.5s ease;
        }}
        .kpi-label {{ color: {MUTED}; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }}
        .kpi-value {{ color: {WHITE}; font-size: 1.8rem; font-weight: 700; line-height: 1.1; }}
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

        .badge-red {{
            display:inline-block; background: rgba(239,68,68,0.15); color:{RED};
            border: 1px solid rgba(239,68,68,0.5); border-radius: 10px; padding: 10px 16px;
            font-weight: 700; font-size: 0.85rem; letter-spacing: 0.03em;
        }}
        .badge-green {{
            display:inline-block; background: rgba(34,197,94,0.12); color:{GREEN};
            border: 1px solid rgba(34,197,94,0.4); border-radius: 10px; padding: 10px 16px;
            font-weight: 700; font-size: 0.85rem;
        }}

        .step-node {{
            display:flex; flex-direction:column; align-items:center; text-align:center; flex:1;
        }}
        .step-dot {{
            width:22px; height:22px; border-radius:50%; background:{CHARCOAL};
            border:3px solid {BORDER}; margin-bottom:8px;
        }}
        .step-dot.done {{ background:{TEAL}; border-color:{TEAL}; }}
        .step-dot.active {{ background:{GOLD}; border-color:{GOLD}; }}
        .step-label {{ color:{WHITE}; font-size:0.78rem; font-weight:600; }}
        .step-sub {{ color:{MUTED}; font-size:0.68rem; }}

        button[data-baseweb="tab"] {{ font-size: 0.95rem; font-weight: 600; color: {MUTED}; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ color: {TEAL} !important; }}
        div[data-baseweb="tab-highlight"] {{ background-color: {TEAL} !important; }}
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden; }}
        .stButton>button {{
            background: linear-gradient(135deg, {TEAL} 0%, #0284C7 100%); color: {WHITE};
            border: none; border-radius: 10px; font-weight: 600;
        }}
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


# ==========================================================================
# OPERATIONAL DATASETS
# ==========================================================================
ORDERS_DATA = pd.DataFrame(
    [
        ["PO-88231", "KSA — MoH Tender", "Hemodialysis Catheters", 42000, 34, 9800, 12],
        ["PO-88240", "Local — Backlog Client A", "CVC Kits", 18500, 22, 11200, 28],
        ["PO-88255", "Kenya — Distributor", "Urology Stents", 27500, 41, 6100, 9],
        ["PO-88260", "Local — Backlog Client B", "Hemodialysis Catheters", 51000, 19, 24300, 35],
        ["PO-88271", "UAE — Private Hospital", "CVC Kits", 33000, 37, 8700, 11],
        ["PO-88284", "Local — Backlog Client C", "Midline Catheters", 15200, 15, 9100, 30],
        ["PO-88290", "Nigeria — Distributor", "Urology Stents", 22800, 39, 5400, 14],
        ["PO-88301", "Local — Backlog Client D", "Hemodialysis Catheters", 47500, 21, 21000, 33],
        ["PO-88312", "Ghana — Distributor", "CVC Kits", 19800, 36, 5200, 13],
        ["PO-88325", "Local — Backlog Client E", "Pediatric CVC", 9800, 44, 2100, 8],
    ],
    columns=[
        "Order ID",
        "Customer / Market",
        "Product Line",
        "Order Value (USD)",
        "Profit Margin %",
        "Raw Material Need (USD)",
        "Days to Cash Inflow",
    ],
)
ORDERS_DATA["Cash Velocity Score"] = (
    ORDERS_DATA["Profit Margin %"] / ORDERS_DATA["Days to Cash Inflow"]
).round(2)
ORDERS_DATA["Priority Tag"] = ORDERS_DATA.apply(
    lambda r: "🟢 Quick Cash" if r["Days to Cash Inflow"] <= 14 else "🟡 High Margin, Slower",
    axis=1,
)

DEAD_STOCK_DATA = pd.DataFrame(
    [
        ["RM-1042", "Polyurethane resin — Lot 2024-B (off-spec color)", 320, 18.5],
        ["RM-1088", "Nitinol wire coil — surplus from cancelled order", 150, 42.0],
        ["RM-1105", "Dacron cuff material — excess batch", 800, 3.2],
        ["RM-1132", "Pebax pellets — slow-moving grade", 210, 15.0],
        ["RM-1150", "Hydrophilic coating solution — near-expiry", 60, 55.0],
        ["RM-1177", "Packaging shells — discontinued SKU size", 4000, 0.9],
    ],
    columns=["SKU", "Description", "Qty on Hand", "Unit Value (USD)"],
)
DEAD_STOCK_DATA["Total Value (USD)"] = DEAD_STOCK_DATA["Qty on Hand"] * DEAD_STOCK_DATA["Unit Value (USD)"]

KNOWN_BATCHES = {
    "SAP-45001298": {"stage": 2, "product": "Hemodialysis Catheter", "destination": "Saudi Arabia (KSA)", "mode": "Air Freight"},
    "SAP-45001310": {"stage": 3, "product": "Triple Lumen CVC", "destination": "Kenya", "mode": "Air Freight"},
    "SAP-45001325": {"stage": 0, "product": "Urology Stent", "destination": "UAE", "mode": "Sea Freight"},
    "SAP-45001340": {"stage": 4, "product": "Foley Catheter", "destination": "Nigeria", "mode": "Air Freight"},
}
STAGES = ["SAP MM\n(Raw Material)", "SAP PP\n(Cleanroom Production)", "SAP QM\n(Sterilization)", "Logistics\n(Freight)", "Delivered"]

# ==========================================================================
# MARKET INTELLIGENCE DATASETS (EMBEDDED)
# ==========================================================================
FACILITIES_DATA = pd.DataFrame([
    {"Region": "GCC", "Country": "Saudi Arabia", "Facility Name": "King Faisal Specialist Hospital & Research Centre (Riyadh)", "Sector": "Government", "Bed Count": "~1200", "Key Specialties": "Nephrology, Transplant, ICU, Oncology", "Target Line": "Dialysis Catheters; Vascular Access (CVC/Midline)", "Account Tier": "Tier 1 Major"},
    {"Region": "GCC", "Country": "Saudi Arabia", "Facility Name": "King Salman Center for Kidney Diseases (Riyadh)", "Sector": "Government", "Bed Count": "~78", "Key Specialties": "Nephrology, Hemodialysis", "Target Line": "Hemodialysis Catheters & Consumables", "Account Tier": "Tier 1 Major"},
    {"Region": "GCC", "Country": "Saudi Arabia", "Facility Name": "King Abdulaziz Medical City (National Guard - Riyadh)", "Sector": "Military", "Bed Count": "~1500", "Key Specialties": "Trauma, Critical Care, Nephrology", "Target Line": "CVC Kits, Dialysis Catheters, Foley Catheters", "Account Tier": "Tier 1 Major"},
    {"Region": "GCC", "Country": "Saudi Arabia", "Facility Name": "King Fahd Medical City (Riyadh)", "Sector": "Government", "Bed Count": "~1200", "Key Specialties": "Comprehensive Medical, ICU, Urology", "Target Line": "Triple-Lumen CVCs, Urology Stents", "Account Tier": "Tier 1 Major"},
    {"Region": "GCC", "Country": "UAE", "Facility Name": "Sheikh Shakhbout Medical City (SSMC) (Abu Dhabi)", "Sector": "Government", "Bed Count": "~740", "Key Specialties": "Critical Care, Nephrology, Surgery", "Target Line": "CVC Kits, Hemodialysis Catheters", "Account Tier": "Tier 1 Major"},
    {"Region": "GCC", "Country": "UAE", "Facility Name": "Cleveland Clinic Abu Dhabi", "Sector": "Private", "Bed Count": "~364", "Key Specialties": "Heart, Vascular, Critical Care, Urology", "Target Line": "Premium CVCs, Hydrophilic Urology Stents", "Account Tier": "Tier 1 Major"},
    {"Region": "Sub-Saharan Africa", "Country": "Kenya", "Facility Name": "Kenyatta National Hospital (Nairobi)", "Sector": "Government", "Bed Count": "~1800", "Key Specialties": "National Referral, Renal Unit, ICU", "Target Line": "Acute & Chronic Dialysis Catheters, CVC Kits", "Account Tier": "Tier 1 Major"},
    {"Region": "Sub-Saharan Africa", "Country": "Kenya", "Facility Name": "Moi Teaching & Referral Hospital (Eldoret)", "Sector": "Government", "Bed Count": "~1000", "Key Specialties": "Renal Care, Critical Care", "Target Line": "Hemodialysis Catheters, Urology Lines", "Account Tier": "Tier 1 Major"},
    {"Region": "Sub-Saharan Africa", "Country": "Nigeria", "Facility Name": "Lagos University Teaching Hospital (LUTH)", "Sector": "Government", "Bed Count": "~760", "Key Specialties": "Nephrology, ICU, General Surgery", "Target Line": "Dialysis Catheters, Standard CVCs", "Account Tier": "Tier 1 Major"},
    {"Region": "Sub-Saharan Africa", "Country": "Ghana", "Facility Name": "Korle Bu Teaching Hospital (Accra)", "Sector": "Government", "Bed Count": "~2000", "Key Specialties": "Renal Unit, Urology, ICU", "Target Line": "Hemodialysis Catheters, Urology Stents", "Account Tier": "Tier 1 Major"}
])

DISTRIBUTORS_DATA = pd.DataFrame([
    {"Country": "UAE", "Distributor Name": "Zahrawi Group", "Specialty Focus": "Urology, Dialysis, Vascular, ICU", "Coverage": "Regional (UAE/KSA/Qatar/Oman)", "Tendering Capability": "Yes", "Status": "Target Partner"},
    {"Country": "Saudi Arabia", "Distributor Name": "Attieh Medico", "Specialty Focus": "ICU/ER, Urology, Radiology", "Coverage": "National (KSA)", "Tendering Capability": "Yes", "Status": "Target Partner"},
    {"Country": "Saudi Arabia", "Distributor Name": "Tamer Group", "Specialty Focus": "General Medical, Devices, Pharma", "Coverage": "National (KSA)", "Tendering Capability": "Yes", "Status": "Target Partner"},
    {"Country": "Saudi Arabia", "Distributor Name": "Naghi Medical", "Specialty Focus": "Hospital Consumables, ICU, Surgical", "Coverage": "National (KSA)", "Tendering Capability": "Yes", "Status": "Target Partner"},
    {"Country": "Kenya", "Distributor Name": "Crown Healthcare", "Specialty Focus": "General Medical & Critical Care", "Coverage": "Regional (Kenya/Uganda/Tanzania)", "Tendering Capability": "Yes", "Status": "Target Partner"},
    {"Country": "Nigeria", "Distributor Name": "JNC International", "Specialty Focus": "Medical Equipment, Critical Care, Dialysis", "Coverage": "National (Nigeria)", "Tendering Capability": "Yes", "Status": "Target Partner"},
    {"Country": "Ghana", "Distributor Name": "Unichem Ghana", "Specialty Focus": "Pharma & Medical Consumables", "Coverage": "National (Ghana)", "Tendering Capability": "Yes", "Status": "Prospect"}
])

KOLS_DATA = pd.DataFrame([
    {"Department": "Nephrology / Dialysis Unit", "Key Decision Maker": "Head of Nephrology / Dialysis Medical Director", "Clinical Pain Point": "High catheter-related bloodstream infection (CRBSI) rates; vascular access site longevity", "Value Proposition": "Antimicrobial & biocompatible Polyurethane/Pebax line extends catheter life and reduces infection", "Target Product Line": "Dialysis Catheters (Acute & Chronic)"},
    {"Department": "ICU / Critical Care", "Key Decision Maker": "ICU Director / Consultant Intensivist", "Clinical Pain Point": "CLABSI infection risks; insertion speed and mechanical kink resistance", "Value Proposition": "Thermosensitive catheter softens at body temperature; anti-occlusion Smart Grooves design", "Target Product Line": "Central Venous Catheters (CVCs)"},
    {"Department": "Urology Department", "Key Decision Maker": "Head of Urology / Senior Consultant Urologist", "Clinical Pain Point": "Stent encrustation, patient discomfort, and difficult placement past strictures", "Value Proposition": "Hydrophilic coating ensures smooth passage; Nitinol core anti-kinking wire", "Target Product Line": "Double-J Stents & Ureteric Sheaths"}
])

COMPETITORS_DATA = pd.DataFrame([
    {"Brand": "AMECATH", "Product Category": "CVC, Dialysis, Urology", "Technical Specs": "Thermosensitive Polyurethane & Pebax; Smart Grooves (>350 mL/min flow); Nitinol guidewires; Hydrophilic coating", "Price Positioning": "Mid / Value-for-Money", "Weaknesses / Gaps": "Brand awareness expansion needed; establishing regional clinical registries", "AMECATH Strategic Advantage": "CE/ISO/SFDA certified; high flow performance at competitive pricing; rapid tender responsiveness"},
    {"Brand": "BD (Bard)", "Product Category": "CVCs, Dialysis Catheters", "Technical Specs": "Premium polyurethane, high biocompatibility, established antimicrobial coating options", "Price Positioning": "High / Premium", "Weaknesses / Gaps": "Premium pricing limits accessibility in cost-sensitive tenders; long global lead times", "AMECATH Strategic Advantage": "Optimized cost structure matching core flow rates with significantly shorter regional delivery times"},
    {"Brand": "Teleflex (Arrow)", "Product Category": "CVCs, Dialysis Catheters", "Technical Specs": "Arrowg+ard antimicrobial coating technology, extensive sizing portfolio", "Price Positioning": "High / Premium", "Weaknesses / Gaps": "High cost per unit; complex commercial structures in regional markets", "AMECATH Strategic Advantage": "Direct flexibility in packaging configurations and direct channel partner margin allocation"},
    {"Brand": "B. Braun", "Product Category": "Vascular Access, Urology", "Technical Specs": "High safety engineering standards, integrated safety needle systems", "Price Positioning": "Mid-High", "Weaknesses / Gaps": "Broad portfolio reduces agility for specialized custom vascular access tenders", "AMECATH Strategic Advantage": "Agile production scheduling and specialized focus on acute dialysis and vascular catheter lines"}
])

REGULATORY_DATA = pd.DataFrame([
    {"Country": "Saudi Arabia", "Authority": "SFDA + NUPCO Tenders", "Required Registration": "MDMA via GHAD Portal; Technical File Assessment; Authorized Representative with MDEL", "Compliance Status": "CE Mark & ISO 13485 support Technical File submission", "Estimated Timeline": "6 - 9 Months"},
    {"Country": "UAE", "Authority": "MoHAP + DOH Abu Dhabi / DHA Dubai", "Required Registration": "MoHAP Device Registration; Local Authorized Representative required", "Compliance Status": "CE Mark & ISO 13485 are core supporting documentation", "Estimated Timeline": "3 - 6 Months"},
    {"Country": "Kenya", "Authority": "Pharmacy and Poisons Board (PPB)", "Required Registration": "PPB Import License and Product Registration; Free Sale Certificate", "Compliance Status": "CE Mark & ISO 13485 accepted for expedited review", "Estimated Timeline": "3 - 5 Months"},
    {"Country": "Nigeria", "Authority": "NAFDAC", "Required Registration": "NAFDAC Device Registration, Factory Inspection / Audit documentation", "Compliance Status": "CE Mark + ISO 13485 required for fast-track processing", "Estimated Timeline": "4 - 8 Months"},
    {"Country": "Ghana", "Authority": "FDA Ghana", "Required Registration": "Medical Device Registration with FDA Ghana; Local Agent representation", "Compliance Status": "CE Mark & ISO 13485 serve as primary technical evidence", "Estimated Timeline": "3 - 6 Months"}
])

# ==========================================================================
# SIDEBAR
# ==========================================================================
st.sidebar.markdown(
    f"""
    <div style="padding: 6px 0 18px 0;">
        <div style="color:{WHITE}; font-size:1.25rem; font-weight:700;">AMECATH</div>
        <div style="color:{MUTED}; font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase;">
            Enterprise Turnaround &amp; Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"""<div style="color:{MUTED}; font-size:0.78rem; line-height:1.5;">
    Unified executive management console integrating operational recovery, cash velocity modeling, real-time SAP tracking, and regional market intelligence.
    </div>""",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.caption("AMECATH · Enterprise Analytics Suite")

# ==========================================================================
# HEADER
# ==========================================================================
st.markdown('<div class="dash-title">Operational Turnaround &amp; Strategic Recovery Console</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dash-subtitle">Liquidity Recovery · Capacity Governance · Real-Time SAP Pipeline · MEA Market Expansion</div>',
    unsafe_allow_html=True,
)
st.write("")

# 4-TAB NAVIGATION
tab_deck, tab_sim, tab_sap, tab_market = st.tabs([
    "📊 Executive Presentation Deck",
    "⚡ Plan B: Cash & Capacity Simulator",
    "🔗 Live SAP Batch Tracker",
    "🗺️ Market Expansion & Intelligence"
])

# ==========================================================================
# TAB 1 — EXECUTIVE PRESENTATION DECK
# ==========================================================================
with tab_deck:
    SLIDES = [
        "1. Executive Pivot",
        "2. Immediate Financial Restructuring",
        "3. Governance & Capacity Policy",
        "4. Supply Chain Route Optimization",
        "5. Regional Expansion Strategy",
        "6. Integrated Operating Model",
    ]

    if "slide_idx" not in st.session_state:
        st.session_state.slide_idx = 0

    nav_l, nav_mid, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("◀ Previous", use_container_width=True, disabled=st.session_state.slide_idx == 0):
            st.session_state.slide_idx = max(0, st.session_state.slide_idx - 1)
    with nav_mid:
        chosen = st.selectbox(
            "Jump to slide", SLIDES, index=st.session_state.slide_idx, label_visibility="collapsed"
        )
        st.session_state.slide_idx = SLIDES.index(chosen)
    with nav_r:
        if st.button("Next ▶", use_container_width=True, disabled=st.session_state.slide_idx == len(SLIDES) - 1):
            st.session_state.slide_idx = min(len(SLIDES) - 1, st.session_state.slide_idx + 1)

    st.progress((st.session_state.slide_idx + 1) / len(SLIDES))
    st.write("")

    idx = st.session_state.slide_idx
    st.markdown('<div class="slide-wrap">', unsafe_allow_html=True)

    # Slide 1
    if idx == 0:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🔄 Operational Pivot: Stabilizing Liquidity & Capacity Governance")
        st.markdown(
            f"""<div class="section-caption" style="font-size:0.95rem; margin-bottom:18px;">
            To support sustainable growth in target MEA markets, immediate operational priority is focused on resolving working capital bottlenecks and aligning production flow.
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("#### Primary Working Capital Bottlenecks")
        c1, c2, c3, c4 = st.columns(4)
        steps = ["Working Capital Strain", "Capital Allocation Bottleneck", "Capacity Utilization Stress", "Fulfillment Schedule Extended"]
        for col, step, i in zip([c1, c2, c3, c4], steps, range(4)):
            with col:
                st.markdown(
                    f"""<div class="section-card" style="text-align:center; border-top:3px solid {RED};">
                    <div style="color:{MUTED}; font-size:0.72rem;">STAGE {i+1}</div>
                    <div style="color:{WHITE}; font-weight:600; margin-top:4px;">{step}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # Slide 2
    elif idx == 1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Financial Stabilization — Primary & Alternative Pathways")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {TEAL};">
                <div class="section-title">Pathway A — Target Working Capital Bridge</div>
                <div class="section-caption" style="margin-bottom:0;">
                Targeted working capital injection ring-fenced specifically for raw material procurement tied to verified open purchase orders. Mitigates market risk as production aligns directly with committed customer demand.
                </div></div>""",
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GOLD};">
                <div class="section-title">Pathway B — Self-Funded Internal Recovery</div>
                <div class="section-caption" style="margin-bottom:0;">
                Internal cash flow optimization program utilizing micro-batch raw material scheduling, cash-velocity order prioritization, and strategic realization of unallocated inventory assets.
                </div></div>""",
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown("#### 🎚️ Model: Cash Cycle Acceleration Impact")
        uplift = st.slider(
            "Estimated cash-cycle acceleration percentage (%)",
            0, 50, 20, key="uplift_slider",
        )
        base_cycle_days = 30
        new_cycle_days = round(base_cycle_days * (1 - uplift / 100))
        bridge_need_base = 180000
        bridge_need_adjusted = round(bridge_need_base * (1 - uplift / 100 * 0.6))
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                kpi_card("Avg. Cash Conversion Cycle", f"{new_cycle_days} days (was {base_cycle_days})", "teal"),
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                kpi_card("Estimated Working Capital Capital Need", f"${bridge_need_adjusted:,.0f} (was ${bridge_need_base:,.0f})", "gold"),
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Slide 3
    elif idx == 2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🛡️ Policy Framework — Operating Discipline")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {TEAL};">
                <div class="section-title">Capacity Threshold Cap (85-90%)</div>
                <div class="section-caption" style="margin-bottom:0;">Automated production capping protocols within SAP when facility utilization reaches peak parameters to safeguard fulfillment timelines.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {GOLD};">
                <div class="section-title">Dedicated Material Advance Structure</div>
                <div class="section-caption" style="margin-bottom:0;">Standardized commercial terms requiring direct advance coverage for dedicated raw material requirements on new purchase contracts.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {GREEN};">
                <div class="section-title">Revolving Material Reserve</div>
                <div class="section-caption" style="margin-bottom:0;">Systematic allocation of operating margin into a standing raw material liquidity fund to ensure continuous production flow.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Slide 4
    elif idx == 3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🚢➔✈️ Supply Chain Optimization — Logistics Redirection")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {RED};">
                <div class="section-title">Maritime Long-Haul Freight (Baseline)</div>
                <div class="kpi-value" style="font-size:2.4rem; color:{RED};">28-35 days</div>
                <div class="section-caption" style="margin-bottom:0;">Extended transit durations and higher inventory holding costs tied to regional maritime corridors.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GREEN};">
                <div class="section-title">Regional Air Freight Routes (Optimized)</div>
                <div class="kpi-value" style="font-size:2.4rem; color:{GREEN};">2-4 days</div>
                <div class="section-caption" style="margin-bottom:0;">Direct regional corridors connecting manufacturing units directly to key GCC and African healthcare hubs.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        st.write("")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=["Maritime Transit"], x=[31], orientation="h", marker_color=RED, name="Sea"))
        fig.add_trace(go.Bar(y=["Air Express Freight"], x=[3], orientation="h", marker_color=GREEN, name="Air"))
        fig.update_layout(
            template=PLOTLY_TEMPLATE, height=200, showlegend=False,
            xaxis_title="Fulfillment Lead Time (Days)", margin=dict(l=10, r=10, t=10, b=30),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Slide 5
    elif idx == 4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🌍 Market Expansion — Middle East & Africa Framework")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("Target Medical Centers", "38 Facilities"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Mapped Jurisdictions", "8 Countries"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Year-1 Baseline Opportunity", "$804,000", "gold"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("Regulatory Clearances", "3 - 9 Months"), unsafe_allow_html=True)
        st.markdown(
            f"""<div class="section-card" style="border-left:3px solid {GOLD}; margin-top:14px;">
            <div class="section-caption" style="margin-bottom:0;">
            <b>Planning Model Baseline:</b> The $804K Year-1 benchmark reflects a bottom-up model centered strictly on core hemodialysis lines across priority hospital networks, excluding additional expansion upside from CVC and Urology categories.
            </div></div>""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Slide 6
    elif idx == 5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🔗 Integrated SAP Decision Engine")
        st.markdown(
            f"""<div class="section-caption" style="font-size:0.95rem;">
            The executive suite provides active analytical models and real-time operational simulation across production, finance, and regional supply networks.
            </div>""",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {TEAL};">
                <div class="section-title">⚡ Plan B: Cash & Capacity Simulator</div>
                <div class="section-caption" style="margin-bottom:0;">Dynamic capacity threshold gauges, margin-versus-velocity prioritization matrices, and material asset realization modeling.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GOLD};">
                <div class="section-title">🔗 Real-Time SAP Pipeline Tracker</div>
                <div class="section-caption" style="margin-bottom:0;">Batch-level monitoring across SAP MM, PP, QM, and SD modules with integrated freight efficiency comparative analytics.</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.write("")
        summary_lines = [
            "AMECATH Enterprise Turnaround & Strategic Expansion - Executive Summary",
            "=" * 75,
            "",
            "1. OPERATIONAL PIVOT",
            "   Stabilizing liquidity and establishing strict production governance to ensure",
            "   consistent delivery performance before expanding regional volume.",
            "",
            "2. WORKING CAPITAL STABILIZATION",
            "   - Pathway A: Ring-fenced working capital facility for committed purchase orders.",
            "   - Pathway B: Micro-batch scheduling and cash-velocity prioritization.",
            "",
            "3. CAPACITY GOVERNANCE POLICY",
            "   - Enforcing an 85-90% facility utilization cap within SAP.",
            "   - Commercial advance terms for custom material requirements.",
            "   - Revolving material reserve allocation.",
            "",
            "4. LOGISTICS NETWORK OPTIMIZATION",
            "   - Transitioning to direct regional air corridors (2-4 days transit).",
            "   - Accelerating capital velocity by ~5x compared to maritime routes.",
            "",
            "5. MEA REGIONAL EXPANSION",
            "   - 38 priority medical institutions across GCC and Sub-Saharan markets.",
            "   - Baseline initial annual opportunity model: $804,000 (Hemodialysis core).",
            "",
            "6. INTEGRATED DECISION SYSTEMS",
            "   - Live operational simulator and SAP S/4HANA tracking interface.",
        ]
        st.download_button(
            "⬇ Download Executive Summary (.txt)",
            data="\n".join(summary_lines),
            file_name="AMECATH_Executive_Summary.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================================
# TAB 2 — PLAN B: CASH FLOW & CAPACITY SIMULATOR
# ==========================================================================
with tab_sim:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Facility Capacity Governance Gauge")
    st.markdown(
        '<div class="section-caption">Adjust facility utilization to model operational threshold controls</div>',
        unsafe_allow_html=True,
    )
    utilization = st.slider("Plant Capacity Utilization (%)", 0, 100, 78, key="cap_slider")

    gauge_col, badge_col = st.columns([2, 1])
    with gauge_col:
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=utilization,
                number={"suffix": "%", "font": {"color": WHITE}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": MUTED},
                    "bar": {"color": GOLD if utilization >= 85 else TEAL},
                    "steps": [
                        {"range": [0, 85], "color": "rgba(14,165,233,0.15)"},
                        {"range": [85, 100], "color": "rgba(239,68,68,0.25)"},
                    ],
                    "threshold": {"line": {"color": RED, "width": 4}, "thickness": 0.8, "value": 85},
                },
            )
        )
        fig_gauge.update_layout(template=PLOTLY_TEMPLATE, height=280, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
    with badge_col:
        st.write("")
        st.write("")
        if utilization >= 85:
            st.markdown(
                '<div class="badge-red">🔴 CAPACITY THRESHOLD REACHED<br>NEW PO LOCKOUT ACTIVE</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="badge-green">🟢 OPERATING WITHIN CAPACITY<br>NEW PO ALLOCATION OPEN</div>',
                unsafe_allow_html=True,
            )
        st.caption(f"Governance Threshold: 85% · Active Level: {utilization}%")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Order Prioritization Engine (Cash Velocity Model)")
    st.markdown(
        '<div class="section-caption">Prioritize production order fulfillment based on margin yield and capital conversion cycle velocity</div>',
        unsafe_allow_html=True,
    )

    sort_mode = st.radio(
        "Sort Criteria", ["Cash Velocity (Margin ÷ Days to Cash)", "Profit Margin %", "Days to Cash Inflow"],
        horizontal=True,
    )
    sort_col = {
        "Cash Velocity (Margin ÷ Days to Cash)": "Cash Velocity Score",
        "Profit Margin %": "Profit Margin %",
        "Days to Cash Inflow": "Days to Cash Inflow",
    }[sort_mode]
    ascending = sort_col == "Days to Cash Inflow"
    orders_sorted = ORDERS_DATA.sort_values(sort_col, ascending=ascending).reset_index(drop=True)

    min_margin = st.slider("Minimum Profit Margin % Filter", 0, 50, 0, key="margin_filter")
    orders_view = orders_sorted[orders_sorted["Profit Margin %"] >= min_margin]

    st.dataframe(orders_view, use_container_width=True, height=320)

    fig_pri = px.bar(
        orders_view, x="Order ID", y="Cash Velocity Score", color="Priority Tag",
        template=PLOTLY_TEMPLATE, color_discrete_map={"🟢 Quick Cash": TEAL, "🟡 High Margin, Slower": GOLD},
    )
    fig_pri.update_layout(height=280, xaxis_title="Order ID", yaxis_title="Velocity Rating")
    st.plotly_chart(fig_pri, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📦 Material Inventory Realization")
    st.markdown(
        '<div class="section-caption">Select unallocated material lots for re-allocation or direct liquidation</div>',
        unsafe_allow_html=True,
    )
    selected_skus = []
    cols = st.columns(2)
    for i, row in DEAD_STOCK_DATA.iterrows():
        with cols[i % 2]:
            checked = st.checkbox(
                f"{row['SKU']} — {row['Description']} ({row['Qty on Hand']:,} units @ ${row['Unit Value (USD)']:.2f})",
                key=f"dead_{row['SKU']}",
            )
            if checked:
                selected_skus.append(row["SKU"])

    unlocked_value = DEAD_STOCK_DATA[DEAD_STOCK_DATA["SKU"].isin(selected_skus)]["Total Value (USD)"].sum()
    st.write("")
    st.markdown(
        kpi_card("Total Liquidity Unlocked", f"${unlocked_value:,.0f}", "green" if unlocked_value else "teal"),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================================
# TAB 3 — LIVE SAP BATCH TRACKER
# ==========================================================================
with tab_sap:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 SAP S/4HANA Order & Batch Search")
    st.markdown(
        f'<div class="section-caption">Enter active SAP Order ID (Reference IDs: {", ".join(KNOWN_BATCHES.keys())})</div>',
        unsafe_allow_html=True,
    )
    batch_id = st.text_input("Batch / PO Reference Number", value="SAP-45001298")
    st.markdown("</div>", unsafe_allow_html=True)

    if batch_id.strip():
        if batch_id in KNOWN_BATCHES:
            info = KNOWN_BATCHES[batch_id]
        else:
            seed = int(hashlib.md5(batch_id.encode()).hexdigest(), 16)
            rnd = random.Random(seed)
            info = {
                "stage": rnd.randint(0, 4),
                "product": rnd.choice(["Hemodialysis Catheter", "Triple Lumen CVC", "Urology Stent", "Foley Catheter"]),
                "destination": rnd.choice(["Saudi Arabia (KSA)", "Kenya", "UAE", "Nigeria", "Ghana"]),
                "mode": rnd.choice(["Air Freight", "Sea Freight"]),
            }

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### 📦 Active Reference: `{batch_id}`")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Product Category", info["product"]), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Destination Market", info["destination"]), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Transportation Mode", info["mode"], "gold"), unsafe_allow_html=True)

        st.write("")
        st.markdown("#### Production & Logistics Pipeline Stage")
        stage = info["stage"]
        step_cols = st.columns(len(STAGES))
        for i, (col, label) in enumerate(zip(step_cols, STAGES)):
            with col:
                dot_class = "done" if i < stage else ("active" if i == stage else "")
                sub = "Complete" if i < stage else ("In Progress" if i == stage else "Pending")
                st.markdown(
                    f"""<div class="step-node">
                    <div class="step-dot {dot_class}"></div>
                    <div class="step-label">{label.splitlines()[0]}</div>
                    <div class="step-sub">{label.splitlines()[1] if len(label.splitlines())>1 else ""}</div>
                    <div class="step-sub" style="margin-top:4px; color:{TEAL if i<=stage else MUTED};">{sub}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.progress((stage + 1) / len(STAGES))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### ✈️ vs 🚢 Freight Route Capital Efficiency Calculator")
        order_value = st.number_input("Order Value (USD)", value=35000, step=1000)
        col_air, col_sea = st.columns(2)
        sea_days, air_days = 30, 3
        with col_sea:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {RED};">
                <div class="section-title">Maritime Freight</div>
                <div class="kpi-value" style="color:{RED};">{sea_days} days</div>
                <div class="section-caption" style="margin-bottom:0;">Transit & Collection Window</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col_air:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GREEN};">
                <div class="section-title">Air Express Freight</div>
                <div class="kpi-value" style="color:{GREEN};">{air_days} days</div>
                <div class="section-caption" style="margin-bottom:0;">Transit & Collection Window</div>
                </div>""",
                unsafe_allow_html=True,
            )
        acceleration = round(sea_days / air_days, 1)
        daily_value_air = order_value / air_days
        daily_value_sea = order_value / sea_days
        st.write("")
        st.markdown(
            kpi_card(
                "Capital Conversion Velocity",
                f"{acceleration}x Faster Acceleration (${daily_value_air:,.0f}/day vs ${daily_value_sea:,.0f}/day)",
                "gold",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================================
# TAB 4 — MARKET EXPANSION & INTELLIGENCE (DEDICATED SEPARATE TAB)
# ==========================================================================
with tab_market:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Middle East & Africa Market Intelligence Engine")
    st.markdown(
        '<div class="section-caption">Comprehensive commercial, distributor, clinical, and regulatory expansion mapping</div>',
        unsafe_allow_html=True,
    )
    
    sub_tab = st.radio(
        "Select Market Analysis Sector:",
        ["🏥 Target Facilities", "🤝 Distributor Network", "👩‍⚕️ Clinical Decision Makers (KOLs)", "⚔️ Competitor Benchmarking", "📋 Regulatory Roadmap"],
        horizontal=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Sub-view 1: Target Facilities
    if sub_tab == "🏥 Target Facilities":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Mapped Hospital Networks & Target Facilities")
        st.markdown('<div class="section-caption">Priority public, private, and military tertiary medical centers in target markets</div>', unsafe_allow_html=True)
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            country_filter = st.multiselect("Filter by Country", options=sorted(FACILITIES_DATA["Country"].unique()), default=sorted(FACILITIES_DATA["Country"].unique()))
        with f_col2:
            sector_filter = st.multiselect("Filter by Sector", options=sorted(FACILITIES_DATA["Sector"].unique()), default=sorted(FACILITIES_DATA["Sector"].unique()))
            
        filtered_fac = FACILITIES_DATA[
            (FACILITIES_DATA["Country"].isin(country_filter)) & 
            (FACILITIES_DATA["Sector"].isin(sector_filter))
        ]
        
        st.dataframe(filtered_fac, use_container_width=True, hide_index=True)
        
        st.write("")
        fig_fac = px.bar(
            filtered_fac, x="Facility Name", y="Country", color="Sector",
            title="Target Healthcare Centers by Jurisdiction & Sector",
            template=PLOTLY_TEMPLATE, color_discrete_sequence=[TEAL, GOLD, "#22D3EE"]
        )
        fig_fac.update_layout(height=320, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_fac, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Sub-view 2: Distributor Network
    elif sub_tab == "🤝 Distributor Network":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Regional Distribution Partners & Channel Network")
        st.markdown('<div class="section-caption">Shortlisted medical device distributors with established tendering and institutional coverage</div>', unsafe_allow_html=True)
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            dist_country = st.multiselect("Filter Partner Country", options=sorted(DISTRIBUTORS_DATA["Country"].unique()), default=sorted(DISTRIBUTORS_DATA["Country"].unique()))
        with d_col2:
            tender_cap = st.selectbox("Tendering Capability Filter", ["All", "Yes", "No"])
            
        filtered_dist = DISTRIBUTORS_DATA[DISTRIBUTORS_DATA["Country"].isin(dist_country)]
        if tender_cap != "All":
            filtered_dist = filtered_dist[filtered_dist["Tendering Capability"] == tender_cap]
            
        st.dataframe(filtered_dist, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Sub-view 3: Clinical Decision Makers (KOLs)
    elif sub_tab == "👩‍⚕️ Clinical Decision Makers (KOLs)":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Departmental Decision Makers & Clinical Positioning")
        st.markdown('<div class="section-caption">Aligning AMECATH technical product value propositions directly with specialty pain points</div>', unsafe_allow_html=True)
        
        st.dataframe(KOLS_DATA, use_container_width=True, hide_index=True)
        
        st.write("")
        st.markdown("##### Clinical Value Alignment Matrix")
        for idx, row in KOLS_DATA.iterrows():
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {TEAL}; padding:14px 18px; margin-bottom:10px;">
                <div style="font-weight:700; color:{WHITE}; font-size:0.95rem;">{row['Department']} — {row['Key Decision Maker']}</div>
                <div style="color:{MUTED}; font-size:0.82rem; margin-top:4px;"><b>Clinical Challenge:</b> {row['Clinical Pain Point']}</div>
                <div style="color:{TEAL}; font-size:0.82rem; margin-top:2px;"><b>AMECATH Value Proposition:</b> {row['Value Proposition']}</div>
                <div style="color:{GOLD}; font-size:0.78rem; margin-top:4px; font-weight:600;">TARGET LINE: {row['Target Product Line']}</div>
                </div>""",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Sub-view 4: Competitor Benchmarking
    elif sub_tab == "⚔️ Competitor Benchmarking":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Institutional Competitive Landscape")
        st.markdown('<div class="section-caption">Comparative evaluation of technical specifications, market positioning, and strategic advantages</div>', unsafe_allow_html=True)
        
        st.dataframe(COMPETITORS_DATA, use_container_width=True, hide_index=True)
        
        st.write("")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {GOLD};">
                <div class="section-title">Tier-1 Multinational Positioning (BD / Teleflex)</div>
                <div class="section-caption" style="margin-bottom:0;">High market awareness but constrained by premium price points and longer delivery schedules. AMECATH offers matching technical material performance at significantly higher capital efficiency.</div>
                </div>""",
                unsafe_allow_html=True
            )
        with c_col2:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {TEAL};">
                <div class="section-title">AMECATH Regional Competitive Edge</div>
                <div class="section-caption" style="margin-bottom:0;">Thermosensitive material formulation, optimized high-flow lumen geometry (>350 mL/min), flexible order quantities, and direct regional air freight fulfillment.</div>
                </div>""",
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Sub-view 5: Regulatory Roadmap
    elif sub_tab == "📋 Regulatory Roadmap":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("#### Market Registration Pathways & Compliance Timelines")
        st.markdown('<div class="section-caption">Regulatory authority requirements, certification routes, and estimated approval timelines</div>', unsafe_allow_html=True)
        
        st.dataframe(REGULATORY_DATA, use_container_width=True, hide_index=True)
        
        st.write("")
        fig_reg = px.bar(
            REGULATORY_DATA, x="Country", y="Estimated Timeline", color="Target Authority",
            title="Estimated Regulatory Approval Timelines by Jurisdiction",
            template=PLOTLY_TEMPLATE, color_discrete_sequence=[TEAL, GOLD, "#22D3EE", "#38BDF8", GREEN]
        )
        fig_reg.update_layout(height=300, xaxis_title="", yaxis_title="Timeframe")
        st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================================
# FOOTER
# ==========================================================================
st.write("")
st.markdown(
    f'<div style="text-align:center; color:{MUTED}; font-size:0.72rem; padding: 10px 0 30px 0;">'
    "AMECATH Operational Turnaround & Strategic Expansion Console &middot; Executive Enterprise Edition"
    "</div>",
    unsafe_allow_html=True,
)
