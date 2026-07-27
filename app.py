"""
AMECATH — Turnaround, Recovery & Market Intelligence Console
Run locally with: streamlit run app.py
"""

import hashlib
import random
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================================
# PAGE CONFIG
# ==========================================================================
st.set_page_config(
    page_title="AMECATH | Turnaround & Market Console",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================
# PALETTE & STYLING
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

        .step-node {{ display:flex; flex-direction:column; align-items:center; text-align:center; flex:1; }}
        .step-dot {{ width:22px; height:22px; border-radius:50%; background:{CHARCOAL}; border:3px solid {BORDER}; margin-bottom:8px; }}
        .step-dot.done {{ background:{TEAL}; border-color:{TEAL}; }}
        .step-dot.active {{ background:{GOLD}; border-color:{GOLD}; }}
        .step-label {{ color:{WHITE}; font-size:0.78rem; font-weight:600; }}
        .step-sub {{ color:{MUTED}; font-size:0.68rem; }}

        button[data-baseweb="tab"] {{ font-size: 0.95rem; font-weight: 600; color: {MUTED}; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ color: {TEAL} !important; }}
        div[data-baseweb="tab-highlight"] {{ background-color: {TEAL} !important; }}
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden; }}
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
# DATASETS
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
        "Order ID", "Customer / Market", "Product Line", "Order Value (USD)",
        "Profit Margin %", "Raw Material Need (USD)", "Days to Cash Inflow"
    ],
)
ORDERS_DATA["Cash Velocity Score"] = (ORDERS_DATA["Profit Margin %"] / ORDERS_DATA["Days to Cash Inflow"]).round(2)
ORDERS_DATA["Priority Tag"] = ORDERS_DATA.apply(
    lambda r: "🟢 Quick Cash" if r["Days to Cash Inflow"] <= 14 else "🟡 High Margin, Slower", axis=1
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
STAGES = ["SAP MM\n(Raw Material)", "SAP PP\n(Production)", "SAP QM\n(Sterilization)", "Logistics\n(Freight)", "Delivered"]

# Market Intelligence Data
DISTRIBUTORS_DATA = pd.DataFrame([
    {"Country": "UAE", "Distributor Name": "Zahrawi Group", "Specialty Focus": "Urology, Dialysis, ICU", "Tendering": "Yes", "Status": "Target Partner"},
    {"Country": "Saudi Arabia", "Distributor Name": "Tamer Group", "Specialty Focus": "General Medical, Devices", "Tendering": "Yes", "Status": "Target Partner"},
    {"Country": "Saudi Arabia", "Distributor Name": "Attieh Medico", "Specialty Focus": "ICU/ER, Urology", "Tendering": "Yes", "Status": "Target Partner"},
    {"Country": "Kenya", "Distributor Name": "Crown Healthcare", "Specialty Focus": "General Medical & Critical Care", "Tendering": "Yes", "Status": "Target Partner"},
    {"Country": "Nigeria", "Distributor Name": "JNC International", "Specialty Focus": "Medical Equipment, ICU", "Tendering": "Yes", "Status": "Target Partner"}
])

KOLS_DATA = pd.DataFrame([
    {"Department": "Nephrology / Dialysis", "Key Decision Maker": "Head of Nephrology", "Clinical Pain Point": "High catheter infection (CRBSI) rates", "Target Lines": "Dialysis Catheters"},
    {"Department": "ICU / Critical Care", "Key Decision Maker": "ICU Director", "Clinical Pain Point": "CLABSI infection risks; access speed", "Target Lines": "Central Venous Catheters (CVCs)"},
    {"Department": "Urology Department", "Key Decision Maker": "Head of Urology", "Clinical Pain Point": "Stent encrustation & discomfort", "Target Lines": "Double-J Stents & Sheaths"}
])

# ==========================================================================
# SIDEBAR & HEADER
# ==========================================================================
st.sidebar.markdown(
    f"""
    <div style="padding: 6px 0 18px 0;">
        <div style="color:{WHITE}; font-size:1.25rem; font-weight:700;">AMECATH</div>
        <div style="color:{MUTED}; font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase;">
            Turnaround &amp; Strategy Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.caption("AMECATH · Internal Executive Use")

st.markdown('<div class="dash-title">Operational Turnaround &amp; Strategic Recovery Console</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">Liquidity Recovery · Capacity Governance · MEA Market Intelligence · Live SAP Engine</div>', unsafe_allow_html=True)
st.write("")

# 4 TABS INTERFACE
tab_deck, tab_intel, tab_sim, tab_sap = st.tabs([
    "📊 Executive Presentation Deck",
    "🗺️ MEA Market Intelligence",
    "⚡ Plan B: Cash & Capacity Simulator",
    "🔗 Live SAP Batch Tracker"
])

# ==========================================================================
# TAB 1 — EXECUTIVE PRESENTATION DECK
# ==========================================================================
with tab_deck:
    SLIDES = ["1. Executive Pivot", "2. Immediate Financial Fix", "3. Policy Fixes", "4. Supply Chain Pivot", "5. Strategic Expansion", "6. Live Decision Engine"]
    if "slide_idx" not in st.session_state: st.session_state.slide_idx = 0

    nav_l, nav_mid, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("◀ Previous", use_container_width=True, disabled=st.session_state.slide_idx == 0):
            st.session_state.slide_idx -= 1
    with nav_mid:
        chosen = st.selectbox("Jump to slide", SLIDES, index=st.session_state.slide_idx, label_visibility="collapsed")
        st.session_state.slide_idx = SLIDES.index(chosen)
    with nav_r:
        if st.button("Next ▶", use_container_width=True, disabled=st.session_state.slide_idx == len(SLIDES) - 1):
            st.session_state.slide_idx += 1

    st.progress((st.session_state.slide_idx + 1) / len(SLIDES))
    st.write("")

    idx = st.session_state.slide_idx
    if idx == 0:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🔄 The Pivot: From Expansion Pitch to Liquidity Recovery")
        c1, c2, c3, c4 = st.columns(4)
        for i, (col, step) in enumerate(zip([c1, c2, c3, c4], ["Cash Shortage", "Accept Orders for Deposits", "Capacity Overload", "Delays Worsen"])):
            with col:
                st.markdown(f'<div class="section-card" style="text-align:center; border-top:3px solid {RED};"><div style="color:{MUTED}; font-size:0.72rem;">STEP {i+1}</div><div style="color:{WHITE}; font-weight:600;">{step}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"Slide {idx + 1}: Review strategic principles and operational guidelines in detail.")

# ==========================================================================
# TAB 2 — MEA MARKET INTELLIGENCE
# ==========================================================================
with tab_intel:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Target Distributors & Clinical KOLs")
    st.caption("Channel partners and key decision makers across GCC and East/West Africa.")
    
    col_d, col_k = st.columns(2)
    with col_d:
        st.markdown("##### Key Distribution Partners")
        st.dataframe(DISTRIBUTORS_DATA, use_container_width=True, hide_index=True)
    with col_k:
        st.markdown("##### Clinical Decision Makers (KOLs)")
        st.dataframe(KOLS_DATA, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================================
# TAB 3 — CASH & CAPACITY SIMULATOR
# ==========================================================================
with tab_sim:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Capacity Cap Gauge")
    utilization = st.slider("Plant Capacity Utilization (%)", 0, 100, 78, key="cap_slider")
    
    if utilization >= 85:
        st.markdown('<div class="badge-red">🔴 CAPACITY CAP TRIGGERED — NEW POs LOCKED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-green">🟢 CAPACITY WITHIN SAFE RANGE — NEW POs ACCEPTED</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Cash Velocity Order Prioritizer")
    st.dataframe(ORDERS_DATA.sort_values("Cash Velocity Score", ascending=False), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================================
# TAB 4 — LIVE SAP BATCH TRACKER
# ==========================================================================
with tab_sap:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 SAP Batch / PO Search")
    batch_id = st.text_input("Enter Batch ID", value="SAP-45001298")
    
    info = KNOWN_BATCHES.get(batch_id, {"stage": 2, "product": "Hemodialysis Catheter", "destination": "Saudi Arabia (KSA)", "mode": "Air Freight"})
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi_card("Product Line", info["product"]), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Destination", info["destination"]), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Shipping Mode", info["mode"], "gold"), unsafe_allow_html=True)
    
    st.write("")
    st.progress((info["stage"] + 1) / len(STAGES))
    st.caption(f"Current Status: Stage {info['stage'] + 1} of 5 ({STAGES[info['stage']].replace(chr(10), ' ')})")
    st.markdown('</div>', unsafe_allow_html=True)
