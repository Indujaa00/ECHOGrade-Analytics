"""
ECHOGrade Analytics
===================
A decision-support platform for planning and operating semester-end
paper recovery campaigns at IIT Madras.

Run with:  streamlit run app.py
"""

import math
import random
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECHOGrade Analytics",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# CUSTOM CSS  – consulting-grade dark-teal palette
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---------- base ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E8F0F2;
}
.stApp { background: #0B1E24; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
    background: #0D2830 !important;
    border-right: 1px solid #1A3D47;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #5CE1C0;
}

/* ---------- headings ---------- */
h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif;
    color: #FFFFFF;
}
h1 { font-size: 2rem; letter-spacing: -0.5px; }

/* ---------- metric cards ---------- */
.metric-card {
    background: linear-gradient(135deg, #0F2D38 0%, #0D3840 100%);
    border: 1px solid #1E5060;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: left;
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7BBFCC;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #5CE1C0;
    line-height: 1.1;
}
.metric-delta {
    font-size: 0.78rem;
    color: #85D9B0;
    margin-top: 4px;
}

/* ---------- section headers ---------- */
.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #5CE1C0;
    border-left: 4px solid #5CE1C0;
    padding-left: 10px;
    margin: 24px 0 12px 0;
}

/* ---------- winner badge ---------- */
.winner-badge {
    background: linear-gradient(90deg, #0F6E50, #0D8A60);
    border: 1px solid #15B078;
    border-radius: 8px;
    padding: 16px 20px;
    font-weight: 600;
    color: #AAFFD8;
}

/* ---------- info box ---------- */
.info-box {
    background: #0A2530;
    border: 1px solid #1A4050;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #A0C8D8;
    margin-bottom: 12px;
}

/* ---------- phase badge ---------- */
.phase-badge {
    display: inline-block;
    background: #14424F;
    border: 1px solid #2A7A8A;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #7ECFE0;
    margin-bottom: 14px;
}

/* ---------- dataframe styling ---------- */
[data-testid="stDataFrame"] { border-radius: 8px; }

/* ---------- plotly charts bg ---------- */
.js-plotly-plot .plotly { background: transparent !important; }

/* ---------- tabs ---------- */
[data-baseweb="tab-list"] { background: #0D2830 !important; border-radius: 8px; }
[data-baseweb="tab"] { color: #7BBFCC !important; }
[aria-selected="true"] { color: #5CE1C0 !important; border-bottom: 2px solid #5CE1C0 !important; }

button[kind="primary"] {
    background: #5CE1C0 !important;
    color: #0B1E24 !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# CONSTANTS & DEFAULTS
# ─────────────────────────────────────────────────────────────────
RANDOM_SEED = 42

# Zone assignments based on IIT Madras campus layout
ZONE_MAP = {
    "Gajendra Circle Zone": ["Ganga", "Godavari", "Jamuna", "Brahmaputra", "Saraswathi", "Sindhu"],
    "Hostel Zone":          ["Alakananda", "Cauvery", "Krishna", "Mahanadhi", "Narmada", "Pampa",
                             "Mandakini", "Tapti"],
    "Taramani Zone":        ["Bhadra", "Sabarmati", "Sarayu", "Sharavathi", "Swarnamukhi",
                             "Tunga", "Tamiraparani"],
}

# Conversion factors for environmental impact
DEFAULT_TREE_PER_KG      = 0.017   # trees per kg paper recycled
DEFAULT_CO2_PER_KG       = 1.084   # kg CO2 saved per kg paper recycled
DEFAULT_LANDFILL_PER_KG  = 1.0     # kg diverted from landfill per kg paper


# ─────────────────────────────────────────────────────────────────
# CORE DATA FUNCTIONS
# ─────────────────────────────────────────────────────────────────

def generate_hostel_data() -> pd.DataFrame:
    """
    Generate a dataframe of IIT Madras hostels with realistic
    synthetic resident counts (300–700 per hostel).
    """
    hostels = [
        "Alakananda", "Brahmaputra", "Cauvery", "Ganga", "Godavari",
        "Jamuna", "Krishna", "Mahanadhi", "Mandakini", "Narmada",
        "Pampa", "Saraswathi", "Sindhu", "Tamiraparani", "Tapti",
        "Bhadra", "Sabarmati", "Sarayu", "Sharavathi", "Swarnamukhi", "Tunga",
    ]
    rng = random.Random(RANDOM_SEED)
    populations = [rng.randint(300, 700) for _ in hostels]

    zones = {}
    for zone, hostel_list in ZONE_MAP.items():
        for h in hostel_list:
            zones[h] = zone

    df = pd.DataFrame({
        "Hostel":     hostels,
        "Population": populations,
        "Zone":       [zones.get(h, "Hostel Zone") for h in hostels],
    })
    return df


def simulate_participation(hostel_df: pd.DataFrame, campus_rate: float) -> pd.DataFrame:
    """
    Assign each hostel a participation rate that varies ±10 pp
    around the campus average, using a fixed random seed for
    reproducibility. Clamps to [0, 1].

    Why ±10 pp?
    -----------
    Real campaigns show hostel-level variation due to block
    culture, warden engagement, and peer effects. A ±10 pp band
    around the campus mean is a conservative but realistic spread.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    n = len(hostel_df)
    # Draw hostel rates within ±10 pp of campus mean
    spread = 0.10
    raw_rates = rng.uniform(campus_rate - spread, campus_rate + spread, size=n)
    hostel_rates = np.clip(raw_rates, 0.0, 1.0)

    df = hostel_df.copy()
    df["Participation Rate (%)"] = (hostel_rates * 100).round(1)
    return df


def calculate_paper_generation(df: pd.DataFrame, avg_paper_kg: float) -> pd.DataFrame:
    """
    For each hostel:
        Participants = Population × (Participation Rate / 100)
        Paper (kg)   = Participants × avg_paper_kg
    """
    df = df.copy()
    df["Participants"]   = (df["Population"] * df["Participation Rate (%)"] / 100).round(0).astype(int)
    df["Paper (kg)"]     = (df["Participants"] * avg_paper_kg).round(2)
    return df


def calculate_trucks(total_paper_kg: float, truck_capacity_kg: float, truck_cost: float) -> dict:
    """
    Total Trucks = ceil(Total Paper / Truck Capacity)
    Returns a dict with trip count, utilisation, and total truck cost.
    """
    trips         = math.ceil(total_paper_kg / truck_capacity_kg) if truck_capacity_kg > 0 else 0
    last_load     = total_paper_kg % truck_capacity_kg
    avg_util      = (total_paper_kg / (trips * truck_capacity_kg) * 100) if trips > 0 else 0
    return {
        "trips":         trips,
        "avg_util_pct":  round(avg_util, 1),
        "total_cost":    trips * truck_cost,
    }


def calculate_workers(total_paper_kg: float, productivity: float,
                      days: int, daily_cost: float) -> dict:
    """
    Workers = ceil(Total Paper / (Productivity × Days))
    Labour Cost = Workers × Days × Daily Cost
    """
    denom   = productivity * days
    workers = math.ceil(total_paper_kg / denom) if denom > 0 else 0
    cost    = workers * days * daily_cost
    return {"workers": workers, "labour_cost": round(cost, 2)}


def evaluate_vendors(paper_kg: float, vendor_df: pd.DataFrame,
                     transport_rate: float) -> pd.DataFrame:
    """
    For each vendor:
        Gross Revenue    = paper_kg × Price (₹/kg)
        Transport Cost   = Distance × transport_rate
        Net Revenue      = Gross Revenue – Transport Cost
    Mark the best (highest Net Revenue) vendor.
    """
    df = vendor_df.copy()
    df["Gross Revenue (₹)"]    = (paper_kg * df["Price (₹/kg)"]).round(2)
    df["Transport Cost (₹)"]   = (df["Distance (km)"] * transport_rate).round(2)
    df["Net Revenue (₹)"]      = (df["Gross Revenue (₹)"] - df["Transport Cost (₹)"]).round(2)
    best_idx                   = df["Net Revenue (₹)"].idxmax()
    df["Optimal?"]             = df.index == best_idx
    return df


def calculate_profitability(paper_kg: float, best_vendor_row: pd.Series,
                            truck_cost: float, labour_cost: float,
                            misc_cost: float) -> dict:
    """
    Revenue       = Net Revenue from best vendor
    Total Cost    = Truck + Labour + Misc
    Net Profit    = Revenue – Total Cost
    Margin        = Net Profit / Revenue × 100
    """
    revenue    = float(best_vendor_row["Net Revenue (₹)"])
    total_cost = truck_cost + labour_cost + misc_cost
    profit     = revenue - total_cost
    margin     = (profit / revenue * 100) if revenue != 0 else 0
    return {
        "revenue":    round(revenue, 2),
        "truck_cost": round(truck_cost, 2),
        "labour_cost": round(labour_cost, 2),
        "misc_cost":  round(misc_cost, 2),
        "total_cost": round(total_cost, 2),
        "profit":     round(profit, 2),
        "margin":     round(margin, 1),
    }


def calculate_environmental_impact(paper_kg: float,
                                   tree_factor: float,
                                   co2_factor: float,
                                   landfill_factor: float) -> dict:
    """
    Trees Saved      = paper_kg × tree_factor
    CO2 Avoided (kg) = paper_kg × co2_factor
    Landfill Diverted= paper_kg × landfill_factor
    """
    return {
        "paper_kg":         round(paper_kg, 2),
        "trees_saved":      round(paper_kg * tree_factor, 1),
        "co2_avoided_kg":   round(paper_kg * co2_factor, 1),
        "landfill_div_kg":  round(paper_kg * landfill_factor, 1),
    }


def forecast_vs_actual(plan_df: pd.DataFrame, actual_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge planned paper (kg) and actual paper (kg) per hostel.
    Compute absolute difference and percentage error.
    """
    merged = plan_df[["Hostel", "Paper (kg)"]].copy()
    merged = merged.rename(columns={"Paper (kg)": "Forecasted (kg)"})
    merged = merged.merge(actual_df[["Hostel", "Actual Paper (kg)"]], on="Hostel", how="left")
    merged["Difference (kg)"]  = (merged["Actual Paper (kg)"] - merged["Forecasted (kg)"]).round(2)
    merged["Error (%)"]        = ((merged["Difference (kg)"].abs() /
                                   merged["Forecasted (kg)"].replace(0, np.nan)) * 100).round(1)
    return merged


# ─────────────────────────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────────────────────────
CHART_BG   = "rgba(0,0,0,0)"
GRID_COLOR = "#1A3D47"
FONT_COLOR = "#A0C8D8"
ACCENT     = "#5CE1C0"
PALETTE    = ["#5CE1C0", "#3AAFAF", "#2A8FA0", "#1A6F80", "#5A9ECC", "#9B7AE0"]


def _base_layout(title="") -> dict:
    return dict(
        title=dict(text=title, font=dict(family="Space Grotesk", size=15, color="#FFFFFF")),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter", color=FONT_COLOR, size=12),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        margin=dict(l=20, r=20, t=50, b=20),
    )


def metric_card(label: str, value: str, delta: str = "") -> str:
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>"""


# ─────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────
def init_state():
    if "hostel_df" not in st.session_state:
        st.session_state.hostel_df = generate_hostel_data()
    if "vendor_df" not in st.session_state:
        st.session_state.vendor_df = pd.DataFrame({
            "Vendor Name":    ["TNPL", "ITC GreenCycle", "Papco", "Local Recycler A", "Local Recycler B"],
            "Distance (km)":  [25, 18, 30, 8, 12],
            "Price (₹/kg)":   [12.5, 13.0, 11.8, 10.5, 11.0],
        })
    if "actual_df" not in st.session_state:
        base = generate_hostel_data()
        base["Actual Paper (kg)"] = 0.0
        st.session_state.actual_df = base[["Hostel", "Actual Paper (kg)"]]


init_state()


# ─────────────────────────────────────────────────────────────────
# SIDEBAR  –  Global Parameters
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ♻️ ECHOGrade")
    st.markdown("<div style='color:#7BBFCC;font-size:0.8rem;margin-bottom:20px;'>IIT Madras · Paper Recovery Platform</div>", unsafe_allow_html=True)

    st.markdown("### 📐 Planning Assumptions")

    campus_rate      = st.slider("Campus Participation Rate (%)", 0, 100, 50, 1) / 100
    avg_paper        = st.slider("Avg Paper / Participating Student (kg)", 0.25, 1.5, 0.75, 0.05)

    st.markdown("---")
    st.markdown("### 🚛 Logistics")

    truck_capacity   = st.number_input("Truck Capacity (kg)", min_value=500, value=3000, step=100)
    truck_cost       = st.number_input("Truck Cost per Trip (₹)", min_value=0, value=15000, step=500)
    collection_days  = st.number_input("Collection Days", min_value=1, value=3, step=1)
    worker_prod      = st.number_input("Worker Productivity (kg/day)", min_value=100, value=500, step=50)
    worker_daily     = st.number_input("Worker Cost per Day (₹)", min_value=0, value=1000, step=100)
    misc_cost        = st.number_input("Miscellaneous Cost (₹)", min_value=0, value=10000, step=500)

    st.markdown("---")
    st.markdown("### 🏭 Vendor Transport")
    transport_rate   = st.number_input("Transport Rate (₹/km)", min_value=1, value=50, step=5)

    st.markdown("---")
    st.markdown("### 🌿 Env. Conversion Factors")
    tree_factor      = st.number_input("Trees saved per kg", value=DEFAULT_TREE_PER_KG, format="%.4f")
    co2_factor       = st.number_input("CO₂ avoided per kg (kg)", value=DEFAULT_CO2_PER_KG, format="%.3f")
    landfill_factor  = st.number_input("Landfill diverted per kg (kg)", value=DEFAULT_LANDFILL_PER_KG, format="%.2f")


# ─────────────────────────────────────────────────────────────────
# COMPUTE PLANNING PHASE
# ─────────────────────────────────────────────────────────────────
hostel_df        = st.session_state.hostel_df.copy()
hostel_part_df   = simulate_participation(hostel_df, campus_rate)
hostel_paper_df  = calculate_paper_generation(hostel_part_df, avg_paper)

total_paper      = hostel_paper_df["Paper (kg)"].sum()
trucks_info      = calculate_trucks(total_paper, truck_capacity, truck_cost)
workers_info     = calculate_workers(total_paper, worker_prod, collection_days, worker_daily)

vendor_df_eval   = evaluate_vendors(total_paper, st.session_state.vendor_df, transport_rate)
best_vendor_row  = vendor_df_eval[vendor_df_eval["Optimal?"]].iloc[0]
profit_info      = calculate_profitability(
    total_paper, best_vendor_row,
    trucks_info["total_cost"], workers_info["labour_cost"], misc_cost
)
env_info         = calculate_environmental_impact(total_paper, tree_factor, co2_factor, landfill_factor)


# ─────────────────────────────────────────────────────────────────
# PAGE NAVIGATION
# ─────────────────────────────────────────────────────────────────
PAGES = [
    "📊 Executive Overview",
    "🏠 Hostel Analytics",
    "🚛 Logistics & Routing",
    "🏭 Vendor Analysis",
    "💰 Financial Analysis",
    "🌿 Environmental Impact",
    "📋 Execution Mode",
    "📈 Forecast vs Actual",
]

with st.sidebar:
    st.markdown("---")
    st.markdown("### 📑 Navigation")
    page = st.radio("", PAGES, label_visibility="collapsed")


# ═══════════════════════════════════════════════════════════════════
# PAGE 1 – EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════
if page == PAGES[0]:
    st.markdown('<div class="phase-badge">PHASE 1 · PLANNING MODE</div>', unsafe_allow_html=True)
    st.title("ECHOGrade Analytics")
    st.markdown("<p style='color:#7BBFCC;font-size:1rem;'>Semester-end paper recovery · IIT Madras</p>", unsafe_allow_html=True)

    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Total Paper Recovered", f"{total_paper:,.0f} kg",
                                f"{total_paper/1000:.2f} metric tonnes"), unsafe_allow_html=True)
    with c2:
        total_students = hostel_paper_df["Population"].sum()
        total_part     = hostel_paper_df["Participants"].sum()
        st.markdown(metric_card("Participating Students",
                                f"{total_part:,}",
                                f"of {total_students:,} total · {campus_rate*100:.0f}% campus rate"),
                    unsafe_allow_html=True)
    with c3:
        sign = "+" if profit_info["profit"] >= 0 else ""
        st.markdown(metric_card("Net Profit",
                                f"₹{abs(profit_info['profit']):,.0f}",
                                f"{sign}{profit_info['margin']:.1f}% margin"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("CO₂ Avoided",
                                f"{env_info['co2_avoided_kg']:,.0f} kg",
                                f"{env_info['trees_saved']:,.0f} trees saved"),
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI Row 2
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Truck Trips", str(trucks_info["trips"]),
                                f"Avg utilisation {trucks_info['avg_util_pct']}%"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Workers Required", str(workers_info["workers"]),
                                f"Over {collection_days} days"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Optimal Vendor", best_vendor_row["Vendor Name"],
                                f"₹{best_vendor_row['Price (₹/kg)']}/kg · {best_vendor_row['Distance (km)']} km away"),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("Total Hostels", str(len(hostel_paper_df)),
                                "Across 3 campus zones"), unsafe_allow_html=True)

    st.markdown("---")

    # Two charts side by side
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-header">Paper by Zone</div>', unsafe_allow_html=True)
        zone_summary = hostel_paper_df.groupby("Zone")["Paper (kg)"].sum().reset_index()
        fig = px.pie(zone_summary, values="Paper (kg)", names="Zone",
                     color_discrete_sequence=PALETTE, hole=0.45)
        fig.update_layout(**_base_layout())
        fig.update_traces(textfont=dict(color="#FFFFFF"))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">Financial Waterfall</div>', unsafe_allow_html=True)
        wf_labels  = ["Revenue", "Truck Cost", "Labour Cost", "Misc Cost", "Net Profit"]
        wf_values  = [profit_info["revenue"],
                      -profit_info["truck_cost"],
                      -profit_info["labour_cost"],
                      -profit_info["misc_cost"],
                      profit_info["profit"]]
        wf_colors  = ["#5CE1C0" if v >= 0 else "#E05C7A" for v in wf_values]
        fig2 = go.Figure(go.Bar(x=wf_labels, y=wf_values,
                                marker_color=wf_colors, text=[f"₹{v:,.0f}" for v in wf_values],
                                textposition="outside", textfont=dict(color="#FFFFFF")))
        fig2.update_layout(**_base_layout())
        st.plotly_chart(fig2, use_container_width=True)

    # Info callout
    st.markdown(f"""
    <div class="info-box">
    <b>How this estimate is generated:</b>
    Each hostel receives a participation rate drawn uniformly from
    [{(campus_rate-0.10)*100:.0f}%, {min((campus_rate+0.10)*100,100):.0f}%]
    around the campus average of {campus_rate*100:.0f}%.
    Paper generation = Participants × {avg_paper} kg.
    Seeds are fixed (seed={RANDOM_SEED}) for reproducibility.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 2 – HOSTEL ANALYTICS
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[1]:
    st.markdown('<div class="phase-badge">PHASE 1 · PLANNING MODE</div>', unsafe_allow_html=True)
    st.title("Hostel Analytics")

    st.markdown('<div class="section-header">Edit Hostel Populations</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">You can edit hostel populations directly. Changes flow through to all calculations.</div>', unsafe_allow_html=True)

    edited = st.data_editor(
        st.session_state.hostel_df[["Hostel", "Population", "Zone"]],
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Population": st.column_config.NumberColumn("Population", min_value=0, step=1),
            "Zone":       st.column_config.SelectboxColumn("Zone", options=list(ZONE_MAP.keys())),
        },
    )
    if not edited.equals(st.session_state.hostel_df[["Hostel", "Population", "Zone"]]):
        st.session_state.hostel_df = edited.copy()
        st.rerun()

    st.markdown('<div class="section-header">Simulated Participation & Paper Generation</div>', unsafe_allow_html=True)
    display_df = hostel_paper_df[["Hostel", "Zone", "Population", "Participation Rate (%)",
                                   "Participants", "Paper (kg)"]].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Bar chart – paper per hostel
    fig = px.bar(hostel_paper_df.sort_values("Paper (kg)", ascending=True),
                 x="Paper (kg)", y="Hostel", orientation="h",
                 color="Zone", color_discrete_sequence=PALETTE, text="Paper (kg)")
    fig.update_traces(texttemplate="%{text:.0f} kg", textposition="outside",
                      textfont=dict(color="#FFFFFF"))
    fig.update_layout(**_base_layout("Paper Generated per Hostel (kg)"), height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Scatter – population vs paper
    fig2 = px.scatter(hostel_paper_df, x="Population", y="Paper (kg)",
                      color="Zone", hover_data=["Hostel"],
                      color_discrete_sequence=PALETTE, size="Paper (kg)")
    fig2.update_layout(**_base_layout("Population vs Paper Generated"))
    st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 3 – LOGISTICS & ROUTING
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[2]:
    st.markdown('<div class="phase-badge">PHASE 1 · PLANNING MODE</div>', unsafe_allow_html=True)
    st.title("Logistics & Truck Routing")

    # Compute per-zone loads
    zone_loads = hostel_paper_df.groupby("Zone")["Paper (kg)"].sum().to_dict()

    c1, c2, c3 = st.columns(3)
    mets = [(c1, "Truck Trips Required", str(trucks_info["trips"]), f"@ {truck_capacity:,} kg capacity"),
            (c2, "Avg Truck Utilisation", f"{trucks_info['avg_util_pct']}%", ""),
            (c3, "Total Truck Cost", f"₹{trucks_info['total_cost']:,}", f"{trucks_info['trips']} trips × ₹{truck_cost:,}")]
    for col, lbl, val, delta in mets:
        with col:
            st.markdown(metric_card(lbl, val, delta), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Zone-wise Truck Routes</div>', unsafe_allow_html=True)

    for zone, hostels in ZONE_MAP.items():
        zone_df     = hostel_paper_df[hostel_paper_df["Zone"] == zone].copy()
        zone_paper  = zone_df["Paper (kg)"].sum()
        zone_trips  = math.ceil(zone_paper / truck_capacity) if truck_capacity > 0 else 0
        zone_util   = (zone_paper / (zone_trips * truck_capacity) * 100) if zone_trips > 0 else 0

        with st.expander(f"🚛  {zone}  —  {zone_paper:,.0f} kg  |  {zone_trips} trips  |  {zone_util:.1f}% utilisation", expanded=True):
            route = " → ".join(
                zone_df.sort_values("Paper (kg)", ascending=False)["Hostel"].tolist()
            )
            st.markdown(f"**Route:** `{route}`")
            st.dataframe(zone_df[["Hostel", "Population", "Participants", "Paper (kg)"]],
                         use_container_width=True, hide_index=True)

    st.markdown("---")

    # Utilisation gauge
    st.markdown('<div class="section-header">Truck Utilisation Overview</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=trucks_info["avg_util_pct"],
        title=dict(text="Average Truck Utilisation (%)", font=dict(color=FONT_COLOR)),
        delta=dict(reference=80, increasing=dict(color="#5CE1C0"), decreasing=dict(color="#E05C7A")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=FONT_COLOR),
            bar=dict(color=ACCENT),
            bgcolor=GRID_COLOR,
            steps=[dict(range=[0, 60], color="#1A3D47"), dict(range=[60, 80], color="#1A5060"),
                   dict(range=[80, 100], color="#0F4050")],
            threshold=dict(line=dict(color="white", width=2), thickness=0.75, value=80),
        ),
        number=dict(font=dict(color=FONT_COLOR), suffix="%"),
    ))
    fig.update_layout(paper_bgcolor=CHART_BG, font=dict(color=FONT_COLOR), height=300,
                      margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # Worker section
    st.markdown("---")
    st.markdown('<div class="section-header">Worker Requirements</div>', unsafe_allow_html=True)

    w1, w2, w3 = st.columns(3)
    with w1:
        st.markdown(metric_card("Workers Required", str(workers_info["workers"]),
                                f"{worker_prod} kg/day productivity"), unsafe_allow_html=True)
    with w2:
        st.markdown(metric_card("Collection Days", str(collection_days), ""), unsafe_allow_html=True)
    with w3:
        st.markdown(metric_card("Total Labour Cost", f"₹{workers_info['labour_cost']:,}",
                                f"₹{worker_daily}/worker/day"), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 4 – VENDOR ANALYSIS
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[3]:
    st.markdown('<div class="phase-badge">PHASE 1 · PLANNING MODE</div>', unsafe_allow_html=True)
    st.title("Vendor Analysis")

    st.markdown('<div class="section-header">Edit Vendor Dataset</div>', unsafe_allow_html=True)

    edited_vendors = st.data_editor(
        st.session_state.vendor_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Distance (km)": st.column_config.NumberColumn(min_value=0),
            "Price (₹/kg)":  st.column_config.NumberColumn(min_value=0.0, format="%.2f"),
        },
    )
    if not edited_vendors.equals(st.session_state.vendor_df):
        st.session_state.vendor_df = edited_vendors.copy()
        st.rerun()

    st.markdown('<div class="section-header">Vendor Profitability Breakdown</div>', unsafe_allow_html=True)

    vendor_results = evaluate_vendors(total_paper, st.session_state.vendor_df, transport_rate)
    best_name      = vendor_results[vendor_results["Optimal?"]]["Vendor Name"].values[0]

    st.markdown(f'<div class="winner-badge">🏆 Optimal Vendor: <b>{best_name}</b>  —  '
                f'Net Revenue ₹{best_vendor_row["Net Revenue (₹)"]:,.0f}</div>',
                unsafe_allow_html=True)

    display_cols = ["Vendor Name", "Distance (km)", "Price (₹/kg)",
                    "Gross Revenue (₹)", "Transport Cost (₹)", "Net Revenue (₹)", "Optimal?"]
    st.dataframe(vendor_results[display_cols], use_container_width=True, hide_index=True)

    # Bar: net revenue comparison
    fig = px.bar(vendor_results, x="Vendor Name", y="Net Revenue (₹)",
                 color="Optimal?",
                 color_discrete_map={True: "#5CE1C0", False: "#3A7080"},
                 text="Net Revenue (₹)")
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside",
                      textfont=dict(color="#FFFFFF"))
    fig.update_layout(**_base_layout("Net Revenue by Vendor"), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Stacked: gross vs transport cost
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=vendor_results["Vendor Name"],
                          y=vendor_results["Gross Revenue (₹)"],
                          name="Gross Revenue", marker_color=PALETTE[0]))
    fig2.add_trace(go.Bar(x=vendor_results["Vendor Name"],
                          y=-vendor_results["Transport Cost (₹)"],
                          name="Transport Cost", marker_color="#E05C7A"))
    fig2.update_layout(**_base_layout("Revenue vs Transport Cost"), barmode="overlay")
    st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 5 – FINANCIAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[4]:
    st.markdown('<div class="phase-badge">PHASE 1 · PLANNING MODE</div>', unsafe_allow_html=True)
    st.title("Financial Analysis")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "Revenue",        f"₹{profit_info['revenue']:,.0f}",       "From optimal vendor"),
        (c2, "Total Cost",     f"₹{profit_info['total_cost']:,.0f}",    "Truck + Labour + Misc"),
        (c3, "Net Profit",     f"₹{profit_info['profit']:,.0f}",        f"{profit_info['margin']}% margin"),
        (c4, "Break-even Load", f"{profit_info['total_cost'] / best_vendor_row['Price (₹/kg)']:.0f} kg",
         "Min paper needed"),
    ]
    for col, lbl, val, delta in kpis:
        with col:
            st.markdown(metric_card(lbl, val, delta), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cost breakdown pie
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section-header">Cost Breakdown</div>', unsafe_allow_html=True)
        cost_df = pd.DataFrame({
            "Category": ["Truck Cost", "Labour Cost", "Misc Cost"],
            "Amount":   [profit_info["truck_cost"], profit_info["labour_cost"], profit_info["misc_cost"]],
        })
        fig = px.pie(cost_df, values="Amount", names="Category",
                     color_discrete_sequence=PALETTE, hole=0.4)
        fig.update_layout(**_base_layout())
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">P&L Summary</div>', unsafe_allow_html=True)
        items  = ["Revenue", "Truck Cost", "Labour Cost", "Misc Cost", "Net Profit"]
        values = [profit_info["revenue"],
                  profit_info["truck_cost"],
                  profit_info["labour_cost"],
                  profit_info["misc_cost"],
                  profit_info["profit"]]
        types  = ["total", "relative", "relative", "relative", "total"]
        colors = {"increasing": {"marker": {"color": "#5CE1C0"}},
                  "decreasing": {"marker": {"color": "#E05C7A"}},
                  "totals":     {"marker": {"color": "#3AAFAF"}}}
        fig2 = go.Figure(go.Waterfall(
            orientation="v",
            measure=types,
            x=items,
            y=[profit_info["revenue"],
               -profit_info["truck_cost"],
               -profit_info["labour_cost"],
               -profit_info["misc_cost"],
               profit_info["profit"]],
            connector=dict(line=dict(color="#3A7080")),
            increasing=dict(marker=dict(color="#5CE1C0")),
            decreasing=dict(marker=dict(color="#E05C7A")),
            totals=dict(marker=dict(color="#3AAFAF")),
        ))
        fig2.update_layout(**_base_layout("Profit & Loss Waterfall"))
        st.plotly_chart(fig2, use_container_width=True)

    # Sensitivity analysis
    st.markdown("---")
    st.markdown('<div class="section-header">Sensitivity: Participation Rate vs Net Profit</div>', unsafe_allow_html=True)
    rates   = [r / 100 for r in range(10, 101, 5)]
    profits = []
    for r in rates:
        tmp_part  = simulate_participation(hostel_df, r)
        tmp_paper = calculate_paper_generation(tmp_part, avg_paper)
        tmp_tp    = tmp_paper["Paper (kg)"].sum()
        tmp_v     = evaluate_vendors(tmp_tp, st.session_state.vendor_df, transport_rate)
        tmp_bv    = tmp_v[tmp_v["Optimal?"]].iloc[0]
        tmp_tr    = calculate_trucks(tmp_tp, truck_capacity, truck_cost)
        tmp_wr    = calculate_workers(tmp_tp, worker_prod, collection_days, worker_daily)
        tmp_pf    = calculate_profitability(tmp_tp, tmp_bv,
                                            tmp_tr["total_cost"], tmp_wr["labour_cost"], misc_cost)
        profits.append(tmp_pf["profit"])

    fig3 = px.line(x=[r * 100 for r in rates], y=profits,
                   labels={"x": "Participation Rate (%)", "y": "Net Profit (₹)"},
                   color_discrete_sequence=[ACCENT])
    fig3.add_hline(y=0, line_dash="dash", line_color="#E05C7A", annotation_text="Break-even")
    fig3.update_layout(**_base_layout())
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 6 – ENVIRONMENTAL IMPACT
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[5]:
    st.markdown('<div class="phase-badge">PHASE 1 · PLANNING MODE</div>', unsafe_allow_html=True)
    st.title("Environmental Impact")

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Paper Recovered",    f"{env_info['paper_kg']:,.0f} kg",          "from 21 hostels"),
        (c2, "Trees Saved",        f"{env_info['trees_saved']:,.0f}",           f"@ {tree_factor} trees/kg"),
        (c3, "CO₂ Avoided",       f"{env_info['co2_avoided_kg']:,.0f} kg",     f"@ {co2_factor} kg CO₂/kg paper"),
        (c4, "Landfill Diverted", f"{env_info['landfill_div_kg']:,.0f} kg",    "kept out of landfill"),
    ]
    for col, lbl, val, delta in cards:
        with col:
            st.markdown(metric_card(lbl, val, delta), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualise impact
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-header">Impact Dashboard</div>', unsafe_allow_html=True)
        categories = ["Trees Saved", "CO₂ Avoided (kg)", "Landfill Div. (kg)"]
        values     = [env_info["trees_saved"], env_info["co2_avoided_kg"], env_info["landfill_div_kg"]]
        fig = go.Figure(go.Bar(
            x=values, y=categories, orientation="h",
            marker=dict(color=PALETTE[:3]),
            text=[f"{v:,.1f}" for v in values], textposition="outside",
            textfont=dict(color="#FFFFFF"),
        ))
        fig.update_layout(**_base_layout(), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">Hostel-wise Environmental Contribution</div>', unsafe_allow_html=True)
        env_df = hostel_paper_df[["Hostel", "Paper (kg)"]].copy()
        env_df["Trees Saved"]    = (env_df["Paper (kg)"] * tree_factor).round(1)
        env_df["CO₂ Avoided (kg)"] = (env_df["Paper (kg)"] * co2_factor).round(1)
        fig2 = px.bar(env_df.sort_values("CO₂ Avoided (kg)", ascending=True),
                      x="CO₂ Avoided (kg)", y="Hostel",
                      orientation="h", color_discrete_sequence=[PALETTE[2]])
        fig2.update_layout(**_base_layout(), height=550)
        st.plotly_chart(fig2, use_container_width=True)

    # Context
    equivalent_cars = env_info["co2_avoided_kg"] / 4600  # avg car emits 4600 kg CO2/year
    st.markdown(f"""
    <div class="info-box">
    <b>Contextualising the impact:</b><br>
    Avoiding <b>{env_info['co2_avoided_kg']:,.0f} kg CO₂</b> is equivalent to taking
    <b>{equivalent_cars:.1f} cars</b> off the road for a year
    (assuming 4,600 kg CO₂/car/year).
    Saving <b>{env_info['trees_saved']:,.0f} trees</b> preserves roughly
    <b>{env_info['trees_saved'] * 0.06:.0f} cubic metres</b> of timber.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 7 – EXECUTION MODE
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[6]:
    st.markdown('<div class="phase-badge">PHASE 2 · EXECUTION MODE</div>', unsafe_allow_html=True)
    st.title("Execution Mode")
    st.markdown('<div class="info-box">Enter the actual paper collected per hostel after the semester-end drive. All analytics below will recalculate using real data.</div>', unsafe_allow_html=True)

    # Editable actual table
    st.markdown('<div class="section-header">Enter Actual Collection Data</div>', unsafe_allow_html=True)
    edited_actual = st.data_editor(
        st.session_state.actual_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Actual Paper (kg)": st.column_config.NumberColumn("Actual Paper (kg)",
                                                                 min_value=0.0, format="%.1f"),
        },
    )
    if not edited_actual.equals(st.session_state.actual_df):
        st.session_state.actual_df = edited_actual.copy()
        st.rerun()

    # ── Recalculate using actual data ──
    actual_total = st.session_state.actual_df["Actual Paper (kg)"].sum()

    if actual_total == 0:
        st.info("Enter actual paper weights above to see Phase 2 analytics.")
    else:
        act_trucks  = calculate_trucks(actual_total, truck_capacity, truck_cost)
        act_workers = calculate_workers(actual_total, worker_prod, collection_days, worker_daily)
        act_vendors = evaluate_vendors(actual_total, st.session_state.vendor_df, transport_rate)
        act_best    = act_vendors[act_vendors["Optimal?"]].iloc[0]
        act_profit  = calculate_profitability(actual_total, act_best,
                                              act_trucks["total_cost"],
                                              act_workers["labour_cost"], misc_cost)
        act_env     = calculate_environmental_impact(actual_total, tree_factor, co2_factor, landfill_factor)

        st.markdown("---")
        st.markdown("### Actual Results")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card("Actual Paper", f"{actual_total:,.0f} kg", ""), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("Trucks Needed", str(act_trucks["trips"]),
                                    f"{act_trucks['avg_util_pct']}% utilisation"), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("Net Profit", f"₹{act_profit['profit']:,.0f}",
                                    f"{act_profit['margin']:.1f}% margin"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("CO₂ Avoided", f"{act_env['co2_avoided_kg']:,.0f} kg",
                                    f"{act_env['trees_saved']:,.0f} trees"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Vendor Rankings (Actual Volume)</div>', unsafe_allow_html=True)
        st.dataframe(act_vendors[["Vendor Name", "Gross Revenue (₹)", "Transport Cost (₹)",
                                   "Net Revenue (₹)", "Optimal?"]],
                     use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 8 – FORECAST VS ACTUAL
# ═══════════════════════════════════════════════════════════════════
elif page == PAGES[7]:
    st.markdown('<div class="phase-badge">PHASE 2 · FORECAST vs ACTUAL</div>', unsafe_allow_html=True)
    st.title("Forecast vs Actual")

    actual_total = st.session_state.actual_df["Actual Paper (kg)"].sum()
    if actual_total == 0:
        st.info("No actual data entered yet. Go to **Execution Mode** (Page 7) to enter collected weights.")
    else:
        fva_df = forecast_vs_actual(hostel_paper_df, st.session_state.actual_df)

        # Summary KPIs
        mae  = fva_df["Difference (kg)"].abs().mean()
        mape = fva_df["Error (%)"].mean()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(metric_card("Forecasted Total", f"{total_paper:,.0f} kg", ""), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("Actual Total", f"{actual_total:,.0f} kg", ""), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("Mean Abs Error", f"{mae:,.1f} kg", "per hostel"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("Mean Abs % Error", f"{mape:.1f}%", "lower = better accuracy"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Table
        st.markdown('<div class="section-header">Hostel-level Comparison</div>', unsafe_allow_html=True)
        st.dataframe(fva_df, use_container_width=True, hide_index=True)

        # Grouped bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Forecasted", x=fva_df["Hostel"], y=fva_df["Forecasted (kg)"],
                             marker_color=PALETTE[0]))
        fig.add_trace(go.Bar(name="Actual",     x=fva_df["Hostel"], y=fva_df["Actual Paper (kg)"],
                             marker_color=PALETTE[2]))
        fig.update_layout(**_base_layout("Forecasted vs Actual Paper per Hostel"),
                          barmode="group", height=500,
                          xaxis=dict(tickangle=-45))
        st.plotly_chart(fig, use_container_width=True)

        # Error bar chart
        fva_sorted = fva_df.sort_values("Error (%)", ascending=False)
        fig2 = px.bar(fva_sorted, x="Hostel", y="Error (%)",
                      color="Error (%)",
                      color_continuous_scale=["#5CE1C0", "#E0A05C", "#E05C7A"])
        fig2.update_layout(**_base_layout("Percentage Error by Hostel"), coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#3A7080;font-size:0.78rem;'>"
    "ECHOGrade Analytics · IIT Madras Paper Recovery Platform · Built with Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
