import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="AMECATH | FDA-Backed MEA Expansion Engine",
    page_icon="🩺",
    layout="wide",
)

NAVY = "#0F172A"
CHARCOAL = "#1E293B"
TEAL = "#0EA5E9"
GOLD = "#D97706"
WHITE = "#FFFFFF"
MUTED = "#94A3B8"
CARD_BG = "#152238"
BORDER = "rgba(148, 163, 184, 0.15)"

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background: linear-gradient(180deg, {NAVY} 0%, #0B1220 100%); color: {WHITE}; }}
        section[data-testid="stSidebar"] {{ background: {CHARCOAL}; border-right: 1px solid {BORDER}; }}
        section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
        .kpi-card {{
            background: {CARD_BG}; border: 1px solid {BORDER};
            border-radius: 12px; padding: 18px; text-align: center;
        }}
        .kpi-value {{ font-size: 1.6rem; font-weight: 700; color: {TEAL}; }}
        .kpi-label {{ font-size: 0.8rem; color: {MUTED}; text-transform: uppercase; }}
        .badge-fda {{
            background: rgba(217, 119, 6, 0.2); border: 1px solid {GOLD};
            color: {GOLD}; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 0.85rem;
            display: inline-block; margin-right: 8px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# DATASETS
# ==========================================
MARKET_DATA = pd.DataFrame([
    ["Saudi Arabia (KSA)", "Registered", "US FDA / Health Canada / SFDA", 12, 350000],
    ["UAE", "Registered", "US FDA / CE Mark", 6, 180000],
    ["Kenya", "Registered", "US FDA / Health Canada", 8, 120000],
    ["Qatar", "Registered", "US FDA / SFDA Equivalent", 4, 90000],
    ["Nigeria", "Registered", "US FDA / Health Canada", 8, 64000],
], columns=["Country", "Registration Status", "Active Credentials", "Target Hospitals", "Year 1 Revenue Potential ($)"])

SAP_BATCHES = {
    "SAP-FDA-9001": {"stage": 2, "product": "Hemodialysis Catheter", "destination": "KSA — MoH Tender", "cert": "US FDA Cleared"},
    "SAP-FDA-9014": {"stage": 1, "product": "Triple Lumen CVC", "destination": "Kenya — National Hospital", "cert": "Health Canada Cleared"},
    "SAP-FDA-9022": {"stage": 3, "product": "Urology Stent", "destination": "UAE — Specialty Group", "cert": "US FDA / CE Mark"},
}
STAGES = ["SAP MM\n(Raw Material)", "SAP PP\n(Cleanroom)", "SAP QM\n(FDA QA Release)", "SAP SD\n(Global Logistics)", "Delivered"]

# ==========================================
# HEADER & NAVIGATION
# ==========================================
st.title("AMECATH — FDA-Backed MEA Expansion & SAP Engine")
st.markdown('<span class="badge-fda">🇺🇸 US FDA Cleared</span> <span class="badge-fda">🇨🇦 Health Canada Approved</span> <span class="badge-fda">🇪🇺 CE Mark & SFDA</span>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Executive Expansion Strategy", "🏥 Registered Markets & Tenders", "🔗 SAP FDA Engine Tracker"])

# TAB 1: PRESENTATION OVERVIEW
with tab1:
    st.header("Global Quality Approvals ➔ Immediate MEA Scale-Up")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Regulatory Barrier</div><div class="kpi-value" style="color:#22C55E;">ZERO (Registered)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Active Credentials</div><div class="kpi-value">FDA / Health Canada</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Baseline Target</div><div class="kpi-value">$804,000</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Strategic Growth Pillars")
    st.write("1. **Instant Tender Qualification:** Active registrations and FDA status grant top priority in government healthcare bids.")
    st.write("2. **Premium Market Positioning:** Competing as a Tier-1 global brand against local and lower-tier international suppliers.")
    st.write("3. **SAP S/4HANA Automated Governance:** Automated compliance checks linking FDA certificate data directly to order dispatch.")

# TAB 2: MARKET MAPPING
with tab2:
    st.header("Pre-Registered Target Markets")
    st.dataframe(MARKET_DATA, use_container_width=True)
    
    fig = px.bar(
        MARKET_DATA, x="Country", y="Year 1 Revenue Potential ($)", color="Active Credentials",
        title="Year 1 Revenue Potential by Market & Credentials",
        color_discrete_sequence=[TEAL, GOLD, "#38BDF8"]
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=WHITE))
    st.plotly_chart(fig, use_container_width=True)

# TAB 3: SAP TRACKER
with tab3:
    st.header("SAP S/4HANA FDA Batch & License Tracker")
    
    selected_batch = st.selectbox("Select Active SAP Order / Batch ID", list(SAP_BATCHES.keys()))
    b_data = SAP_BATCHES[selected_batch]
    
    st.write(f"**Product:** {b_data['product']} | **Destination:** {b_data['destination']} | **License Clearance:** `{b_data['cert']}`")
    
    stage = b_data["stage"]
    cols = st.columns(len(STAGES))
    for idx, (c, name) in enumerate(zip(cols, STAGES)):
        with c:
            status_color = TEAL if idx <= stage else MUTED
            st.markdown(f"**{name.splitlines()[0]}**\n\n<span style='color:{status_color}'>{'Done' if idx < stage else ('Active' if idx == stage else 'Pending')}</span>", unsafe_allow_html=True)
    
    st.progress((stage + 1) / len(STAGES))

st.markdown("---")
st.caption("AMECATH Commercial Console · FDA & Global Registration Compliance Engine")
