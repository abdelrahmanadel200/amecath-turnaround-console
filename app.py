"""
AMECATH — Operational Turnaround & Strategic Recovery Console
Run with: streamlit run app.py

Three integrated tabs:
  1. Executive Interactive Presentation Deck (6-slide turnaround narrative)
  2. Plan B: Cash Flow & Capacity Simulator
  3. Live SAP S/4HANA Batch & Delivery Tracker

All data below is embedded mock/demo data for presentation purposes — see the
inline notes marked "DEMO DATA" wherever a number would need to be replaced
with a real SAP export before this goes into daily operational use.
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
    page_title="AMECATH | Turnaround & Recovery Console",
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

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulseGlow {{
            0%   {{ box-shadow: 0 0 0px rgba(14,165,233,0.4); }}
            50%  {{ box-shadow: 0 0 18px rgba(14,165,233,0.65); }}
            100% {{ box-shadow: 0 0 0px rgba(14,165,233,0.4); }}
        }}
        @keyframes pulseRed {{
            0%   {{ box-shadow: 0 0 0px rgba(239,68,68,0.5); }}
            50%  {{ box-shadow: 0 0 20px rgba(239,68,68,0.85); }}
            100% {{ box-shadow: 0 0 0px rgba(239,68,68,0.5); }}
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
        .kpi-value {{ color: {WHITE}; font-size: 1.9rem; font-weight: 700; line-height: 1.1; }}
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
            animation: pulseRed 1.6s infinite;
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
        .step-dot.done {{ background:{TEAL}; border-color:{TEAL}; animation: pulseGlow 1.8s infinite; }}
        .step-dot.active {{ background:{GOLD}; border-color:{GOLD}; animation: pulseGlow 1.2s infinite; }}
        .step-label {{ color:{WHITE}; font-size:0.78rem; font-weight:600; }}
        .step-sub {{ color:{MUTED}; font-size:0.68rem; }}
        .step-line {{ flex:1; height:3px; background:{BORDER}; margin-top:11px; }}
        .step-line.done {{ background:{TEAL}; }}

        button[data-baseweb="tab"] {{ font-size: 0.95rem; font-weight: 600; color: {MUTED}; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ color: {TEAL} !important; }}
        div[data-baseweb="tab-highlight"] {{ background-color: {TEAL} !important; }}
        [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden; }}
        span[data-baseweb="tag"] {{ background-color: {TEAL} !important; }}
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
# MOCK DATA  (DEMO DATA — replace with live SAP exports before production use)
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

# Pre-set demo batches so the tracker always has a few "known good" IDs to try
KNOWN_BATCHES = {
    "SAP-45001298": {"stage": 2, "product": "Hemodialysis Catheter", "destination": "Saudi Arabia (KSA)", "mode": "Air Freight"},
    "SAP-45001310": {"stage": 3, "product": "Triple Lumen CVC", "destination": "Kenya", "mode": "Air Freight"},
    "SAP-45001325": {"stage": 0, "product": "Urology Stent", "destination": "UAE", "mode": "Sea Freight"},
    "SAP-45001340": {"stage": 4, "product": "Foley Catheter", "destination": "Nigeria", "mode": "Air Freight"},
}
STAGES = ["SAP MM\n(Raw Material)", "SAP PP\n(Cleanroom Production)", "SAP QM\n(Sterilization)", "Logistics\n(Freight)", "Delivered"]

# ==========================================================================
# SIDEBAR
# ==========================================================================
st.sidebar.markdown(
    f"""
    <div style="padding: 6px 0 18px 0;">
        <div style="color:{WHITE}; font-size:1.25rem; font-weight:700;">AMECATH</div>
        <div style="color:{MUTED}; font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase;">
            Turnaround &amp; Recovery Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    f"""<div style="color:{MUTED}; font-size:0.75rem; line-height:1.5;">
    This console unifies the executive narrative, the Plan B cash/capacity simulator,
    and a live SAP batch tracker into a single tool for the CEO meeting.
    <br><br>
    All SAP figures shown are <b>demo data</b> — wire up a real SAP export before using
    this operationally.
    </div>""",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.caption("AMECATH · Internal Use Only")

# ==========================================================================
# HEADER
# ==========================================================================
st.markdown('<div class="dash-title">Operational Turnaround &amp; Strategic Recovery Console</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dash-subtitle">Liquidity Recovery · Capacity Governance · Supply Chain Pivot · Regional Expansion</div>',
    unsafe_allow_html=True,
)
st.write("")

tab_deck, tab_sim, tab_sap = st.tabs(
    ["📊 Executive Presentation Deck", "⚡ Plan B: Cash &amp; Capacity Simulator", "🔗 Live SAP Batch Tracker"]
)

# ==========================================================================
# TAB 1 — EXECUTIVE PRESENTATION DECK
# ==========================================================================
with tab_deck:
    SLIDES = [
        "1. Executive Pivot",
        "2. Immediate Financial Fix (Plan A & B)",
        "3. Permanent Policy Fixes",
        "4. Supply Chain Pivot",
        "5. Strategic Market Expansion",
        "6. Live SAP Decision Engine",
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

    # ---- SLIDE 1 ----
    if idx == 0:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🔄 The Pivot: From Expansion Pitch to Liquidity &amp; Capacity Recovery")
        st.markdown(
            f"""<div class="section-caption" style="font-size:0.95rem; margin-bottom:18px;">
            What started as a regional market-expansion study surfaced a more urgent priority: an
            <b style="color:{GOLD};">operational death spiral</b> that needs to be closed before any new growth is layered on top.
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("#### The Cycle We're In")
        c1, c2, c3, c4 = st.columns(4)
        steps = ["Cash Shortage", "Accept New Orders for Deposits", "Capacity Overload", "Delivery Delays Worsen"]
        for col, step, i in zip([c1, c2, c3, c4], steps, range(4)):
            with col:
                st.markdown(
                    f"""<div class="section-card" style="text-align:center; border-top:3px solid {RED};">
                    <div style="color:{MUTED}; font-size:0.72rem;">STEP {i+1}</div>
                    <div style="color:{WHITE}; font-weight:600; margin-top:4px;">{step}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.markdown(
            f"""<div style="text-align:center; color:{MUTED}; margin: 6px 0 16px 0;">
            ↻ &nbsp; the cycle feeds back into Step 1 — cash gets tighter every rotation
            </div>""",
            unsafe_allow_html=True,
        )
        with st.expander("🗒️ Speaker notes"):
            st.write(
                "بص حضرتك، أنا البداية كانت فكرة توسع في إفريقيا والخليج، لكن وأنا بدرس الأرقام التشغيلية "
                "اكتشفت إن الشركة محبوسة جوه دائرة مغلقة: بنقبل أوردرات جديدة عشان ناخد ديبوزيت نشتري بيه خامات "
                "لأوردرات قديمة متأخرة، فالطاقة الإنتاجية تتخنق، والتسليم يتأخر أكتر، والنزيف المالي يزيد. "
                "علشان كده حولت العرض النهارده لخطة إنقاذ سيولة عاجلة، وبعدين توسع استراتيجي."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- SLIDE 2 ----
    elif idx == 1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Immediate Financial Fix — Plan A &amp; Plan B")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {TEAL};">
                <div class="section-title">Plan A — Shareholder Bridge Loan</div>
                <div class="section-caption" style="margin-bottom:0;">
                Working capital injection, <b>earmarked exclusively for raw materials on the
                existing open backlog</b> — not new growth. Zero market risk: every order it
                funds already has a paying customer waiting. Repaid with a return on capital
                as soon as each shipment is collected.
                </div></div>""",
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GOLD};">
                <div class="section-title">Plan B — Self-Funded Recovery</div>
                <div class="section-caption" style="margin-bottom:0;">
                If owners prefer not to inject new cash: micro-batch raw-material purchasing,
                cash-velocity order prioritization, and dead-stock monetization — all modeled
                live in the next tab.
                </div></div>""",
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown("#### 🎚️ Simulate: Cash-First Prioritization Uplift")
        uplift = st.slider(
            "Estimated cash-cycle acceleration from re-prioritizing orders by cash velocity (%)",
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
                kpi_card("Estimated Bridge Loan Needed", f"${bridge_need_adjusted:,.0f} (was ${bridge_need_base:,.0f})", "gold"),
                unsafe_allow_html=True,
            )
        st.caption(
            "Illustrative sensitivity model for discussion purposes — not a substitute for a full "
            "treasury cash-flow forecast."
        )
        with st.expander("🗒️ Speaker notes"):
            st.write(
                "عشان نخرج من أزمة السيولة، عندنا حلين. الحل الأول Plan A، بريدج لون من الشركاء مخصص "
                "حصريًا لخامات الأوردرات المفتوحة بس، ده تمويل شبه مضمون لأن فيه عميل مستني بالفعل، وبيرجع "
                "بمجرد ما نحصّل. الحل التاني Plan B، لو الملاك مش عايزين يضخوا كاش جديد، هنعتمد على تمويل "
                "ذاتي من جوه: دفعات خامات مصغرة، ترتيب الأوردرات حسب سرعة تحصيل الكاش، وتسييل المخزون الميت."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- SLIDE 3 ----
    elif idx == 2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🛡️ Permanent Policy Fixes — Stopping the Cycle From Recurring")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {TEAL};">
                <div class="section-title">Capacity Cap (85-90%)</div>
                <div class="section-caption" style="margin-bottom:0;">No new POs accepted once plant
                utilization crosses the cap — enforced live in SAP, modeled in the next tab.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {GOLD};">
                <div class="section-title">100% Raw Material Deposit</div>
                <div class="section-caption" style="margin-bottom:0;">Every new customer covers 100%
                of their own order's raw-material cost upfront, tracked as an independent SAP line —
                so no order's deposit ever funds another order's backlog again.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""<div class="section-card" style="border-top:3px solid {GREEN};">
                <div class="section-title">Revolving Raw Material Reserve</div>
                <div class="section-caption" style="margin-bottom:0;">A small percentage of profit
                from every completed order feeds a standing reserve — future raw-material purchases
                stop depending on the next customer's deposit.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with st.expander("🗒️ Speaker notes"):
            st.write(
                "وعشان الأزمة دي ماتتكررش تاني، هنطبق 3 قواعد دائمة. أول حاجة سقف إنتاجي 85 لـ90 بالميه، "
                "ممنوع نقبل أوردر جديد لو المصنع مضغوط. تاني حاجة، كل عميل جديد لازم يدفع 100% من تكلفة "
                "الخامات بتاعته في بند مستقل على الـ SAP، مش هيتلخبط مع خامات أوردرات تانية. تالت حاجة، "
                "نقتطع نسبة من أرباح كل أوردر يتسلم في صندوق طوارئ خامات دائم."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- SLIDE 4 ----
    elif idx == 3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🚢➔✈️ Supply Chain Pivot — Bypassing the Strait of Hormuz")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {RED};">
                <div class="section-title">Sea Freight to Asia (Current Risk)</div>
                <div class="kpi-value" style="font-size:2.4rem; color:{RED};">28-35 days</div>
                <div class="section-caption" style="margin-bottom:0;">Elevated cost and risk exposure
                tied to Strait of Hormuz transit disruption; ties up cash for a month or more per order.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GREEN};">
                <div class="section-title">Air Freight to GCC &amp; Africa (Proposed)</div>
                <div class="kpi-value" style="font-size:2.4rem; color:{GREEN};">2-4 days</div>
                <div class="section-caption" style="margin-bottom:0;">Short-haul lanes to the new
                priority markets — avoids Hormuz entirely and collects cash roughly 5x faster.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        st.write("")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=["Sea Freight (Asia)"], x=[31], orientation="h", marker_color=RED, name="Sea"))
        fig.add_trace(go.Bar(y=["Air Freight (GCC/Africa)"], x=[3], orientation="h", marker_color=GREEN, name="Air"))
        fig.update_layout(
            template=PLOTLY_TEMPLATE, height=200, showlegend=False,
            xaxis_title="Lead Time (Days)", margin=dict(l=10, r=10, t=10, b=30),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with st.expander("🗒️ Speaker notes"):
            st.write(
                "بعد ما حلينا مشكلة الكاش، ندخل على المشكلة اللوجستية. الشحن البحري لآسيا دلوقتي فيه "
                "مخاطرة وتكلفة عالية بسبب أزمة هرمز، وإحنا أصلاً معندناش ستوك يكفينا ننتظر. الحل إننا "
                "نتحول فورًا للشحن الجوي للأسواق القريبة، الخليج وإفريقيا، وده بيقطع مشكلة هرمز تمامًا، "
                "وبينزل الـ lead time من 30 يوم بحري لـ2 لـ4 أيام جوي، يعني تحصيل الكاش أسرع بـ5 أضعاف."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- SLIDE 5 ----
    elif idx == 4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🌍 Strategic Market Expansion — GCC &amp; MEA")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi_card("Target Hospitals", "38"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Countries Mapped", "8"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Year-1 Baseline (Hemodialysis Only)", "$804K", "gold"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi_card("Regulatory Access Timeline", "3-9 months"), unsafe_allow_html=True)
        st.markdown(
            f"""<div class="section-card" style="border-left:3px solid {GOLD}; margin-top:14px;">
            <div class="section-caption" style="margin-bottom:0;">
            ⚠️ The $804K figure is a <b>conservative, planning-stage bottom-up estimate</b>
            (Dialysis Beds × Sessions/Week × 52 × Penetration Rate) — hemodialysis only, excluding
            ICU/Urology/CVC upside. It is not verified sales data; treat it as a floor for discussion,
            not a committed number.
            </div></div>""",
            unsafe_allow_html=True,
        )
        with st.expander("🗒️ Speaker notes"):
            st.write(
                "بناءً على حل أزمة الكاش والتحول للشحن الجوي، تيجي خطة التوسع في أسواق الخليج وإفريقيا "
                "القريبة لوجستيًا. جهزت دراسة كاملة: حصرت المستشفيات المستهدفة وقسمتها حسب الأسرة، والموزعين "
                "المعتمدين، والأطباء المؤثرين. وعملت توقع مبيعات تصاعدي مبني على احتياج أسرة الغسيل الكلوي "
                "بس، كبداية تحفظية جدًا، ~804 ألف دولار في السنة الأولى."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- SLIDE 6 ----
    elif idx == 5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 🔗 Live SAP S/4HANA Decision Engine")
        st.markdown(
            f"""<div class="section-caption" style="font-size:0.95rem;">
            Everything on this deck runs live, not just on paper — the next two tabs are a working
            simulator, not mockup screenshots.
            </div>""",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {TEAL};">
                <div class="section-title">⚡ Plan B: Cash &amp; Capacity Simulator</div>
                <div class="section-caption" style="margin-bottom:0;">Capacity cap gauge, cash-velocity
                order prioritizer, dead-stock monetization toggle — switch to the next tab to try it live.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GOLD};">
                <div class="section-title">🔗 Live SAP Batch Tracker</div>
                <div class="section-caption" style="margin-bottom:0;">Enter a batch/PO ID and watch it
                move through MM → PP → QM → Logistics in real time, with an Air vs. Sea comparison.</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with st.expander("🗒️ Speaker notes"):
            st.write(
                "وعشان الكلام ده كله مايبقاش مجرد حبر على ورق، حولت الخطة دي لأداة تفاعلية حية مربوطة "
                "برؤية كاملة لـ SAP: MM وPP وSD. فيه شاشة بتفلتر الأوردرات أوتوماتيك حسب سرعة تحصيل الكاش "
                "وأعلى هامش ربح، وفيه تتبع لحظي للشحنات بدل الإيميلات والتقارير اليدوية — حضرتك دلوقتي "
                "هتشوفها شغالة قدامك مش على السلايد بس."
            )

        st.write("")
        summary_lines = [
            "AMECATH — Operational Turnaround & Strategic Recovery Plan — Executive Summary",
            "=" * 70,
            "",
            "1. EXECUTIVE PIVOT",
            "   From market-expansion pitch to liquidity & capacity recovery.",
            "   Core issue: an operational cycle where new-order deposits fund old backlog",
            "   raw materials, straining capacity and delaying delivery further each cycle.",
            "",
            "2. IMMEDIATE FINANCIAL FIX",
            "   Plan A: Shareholder bridge loan, earmarked for existing backlog raw materials only.",
            "   Plan B: Self-funded recovery via micro-batch purchasing, cash-velocity order",
            "   prioritization, and dead-stock monetization.",
            "",
            "3. PERMANENT POLICY FIXES",
            "   - Capacity Cap: no new POs accepted above 85-90% plant utilization.",
            "   - 100% Raw Material Deposit Policy for all new customers, tracked as an",
            "     independent SAP line item.",
            "   - Revolving Raw Material Reserve funded by a share of completed-order profit.",
            "",
            "4. SUPPLY CHAIN PIVOT",
            "   Shift from sea freight to Asia (28-35 days, Hormuz-exposed) to air freight",
            "   into GCC & Africa (2-4 days) - roughly 5x faster cash collection.",
            "",
            "5. STRATEGIC MARKET EXPANSION",
            "   38 target hospitals across 8 GCC/Africa countries. Year-1 hemodialysis-only",
            "   baseline: $804K (conservative, planning-stage bottom-up estimate - excludes",
            "   ICU/Urology/CVC upside; not verified sales data).",
            "",
            "6. LIVE SAP DECISION ENGINE",
            "   Cash & capacity simulator + live batch tracker, both operational in this console.",
            "",
            "IMMEDIATE NEXT STEP: Authorize outreach to Top-10 shortlisted distributors",
            "in Saudi Arabia & Kenya. Next executive update within 30 days of first responses.",
        ]
        st.download_button(
            "⬇ Download Executive Deck Summary (.txt)",
            data="\n".join(summary_lines),
            file_name="AMECATH_Turnaround_Summary.txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.caption(
            "Text export shown here; wiring this to a formatted PDF would need an extra library "
            "(e.g. fpdf2/reportlab) not included in this build."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close slide-wrap

# ==========================================================================
# TAB 2 — PLAN B: CASH FLOW & CAPACITY SIMULATOR
# ==========================================================================
with tab_sim:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Capacity Cap Gauge")
    st.markdown(
        '<div class="section-caption">Drag to simulate current plant utilization</div>',
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
                '<div class="badge-red">🔴 CAPACITY CAP TRIGGERED<br>NEW POs LOCKED</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="badge-green">🟢 CAPACITY WITHIN SAFE RANGE<br>NEW POs ACCEPTED</div>',
                unsafe_allow_html=True,
            )
        st.caption(f"Cap threshold: 85% · Current: {utilization}%")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Cash Velocity Order Prioritizer")
    st.markdown(
        '<div class="section-caption">Simulated SAP open-order book — filter and sort by what actually gets cash in the door fastest</div>',
        unsafe_allow_html=True,
    )

    sort_mode = st.radio(
        "Prioritize by", ["Cash Velocity (Margin ÷ Days to Cash)", "Profit Margin %", "Days to Cash Inflow"],
        horizontal=True,
    )
    sort_col = {
        "Cash Velocity (Margin ÷ Days to Cash)": "Cash Velocity Score",
        "Profit Margin %": "Profit Margin %",
        "Days to Cash Inflow": "Days to Cash Inflow",
    }[sort_mode]
    ascending = sort_col == "Days to Cash Inflow"
    orders_sorted = ORDERS_DATA.sort_values(sort_col, ascending=ascending).reset_index(drop=True)

    min_margin = st.slider("Minimum Profit Margin % filter", 0, 50, 0, key="margin_filter")
    orders_view = orders_sorted[orders_sorted["Profit Margin %"] >= min_margin]

    st.dataframe(orders_view, use_container_width=True, height=340)

    fig_pri = px.bar(
        orders_view, x="Order ID", y="Cash Velocity Score", color="Priority Tag",
        template=PLOTLY_TEMPLATE, color_discrete_map={"🟢 Quick Cash": TEAL, "🟡 High Margin, Slower": GOLD},
    )
    fig_pri.update_layout(height=300, xaxis_title="", yaxis_title="Cash Velocity Score")
    st.plotly_chart(fig_pri, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📦 Dead Stock Monetization")
    st.markdown(
        '<div class="section-caption">Select idle raw materials to reallocate or liquidate — see instant cash impact</div>',
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
        kpi_card("Instant Cash Unlocked from Selection", f"${unlocked_value:,.0f}", "green" if unlocked_value else "teal"),
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================================
# TAB 3 — LIVE SAP BATCH & DELIVERY TRACKER
# ==========================================================================
with tab_sap:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 SAP Batch / PO Search")
    st.markdown(
        f'<div class="section-caption">Try a known demo ID — {", ".join(KNOWN_BATCHES.keys())} — or type any '
        "ID to generate a simulated live status.</div>",
        unsafe_allow_html=True,
    )
    batch_id = st.text_input("Batch / PO ID", value="SAP-45001298", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if batch_id.strip():
        if batch_id in KNOWN_BATCHES:
            info = KNOWN_BATCHES[batch_id]
        else:
            # Deterministic pseudo-status so any typed ID still gives a stable, plausible demo result
            seed = int(hashlib.md5(batch_id.encode()).hexdigest(), 16)
            rnd = random.Random(seed)
            info = {
                "stage": rnd.randint(0, 4),
                "product": rnd.choice(["Hemodialysis Catheter", "Triple Lumen CVC", "Urology Stent", "Foley Catheter"]),
                "destination": rnd.choice(["Saudi Arabia (KSA)", "Kenya", "UAE", "Nigeria", "Ghana"]),
                "mode": rnd.choice(["Air Freight", "Sea Freight"]),
            }

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### 📦 Batch `{batch_id}`")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Product Line", info["product"]), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Destination", info["destination"]), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("Shipping Mode", info["mode"], "gold"), unsafe_allow_html=True)

        st.write("")
        st.markdown("#### Real-Time Progress Pipeline")
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
        st.markdown("### ✈️ vs 🚢 Freight Comparison — Cash Acceleration Calculator")
        order_value = st.number_input("Order Value (USD)", value=35000, step=1000)
        col_air, col_sea = st.columns(2)
        sea_days, air_days = 30, 3
        with col_sea:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {RED};">
                <div class="section-title">Sea Freight</div>
                <div class="kpi-value" style="color:{RED};">{sea_days} days</div>
                <div class="section-caption" style="margin-bottom:0;">Cash collected on day {sea_days}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col_air:
            st.markdown(
                f"""<div class="section-card" style="border-left:3px solid {GREEN};">
                <div class="section-title">Air Freight</div>
                <div class="kpi-value" style="color:{GREEN};">{air_days} days</div>
                <div class="section-caption" style="margin-bottom:0;">Cash collected on day {air_days}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        acceleration = round(sea_days / air_days, 1)
        daily_value_air = order_value / air_days
        daily_value_sea = order_value / sea_days
        st.write("")
        st.markdown(
            kpi_card(
                "Cash Collection Acceleration",
                f"{acceleration}x faster (${daily_value_air:,.0f}/day vs ${daily_value_sea:,.0f}/day)",
                "gold",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown(
    f'<div style="text-align:center; color:{MUTED}; font-size:0.72rem; padding: 10px 0 30px 0;">'
    "AMECATH Turnaround &amp; Recovery Console &middot; Internal Use Only &middot; All SAP data shown is simulated"
    "</div>",
    unsafe_allow_html=True,
)
