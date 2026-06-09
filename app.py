
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import joblib
import os
import base64
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="VIO Intelligence Platform",
    page_icon="🛢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── NEW PURPLE BRAND PALETTE ─────────────────────────────────────
VIO_PURPLE_NEON  = "#A832FF"   # Electric Purple — neon glow, logo accents
VIO_PURPLE_MID   = "#4A157D"   # Deep Royal Purple — gradient mid-tone
VIO_PURPLE_DARK  = "#140526"   # Dark Violet / Shadow — near-black base
VIO_PURPLE_CARD  = "#1E0A3C"   # Card background — slightly lighter than base
VIO_PURPLE_GLOW  = "rgba(168,50,255,0.18)"  # For glows and fills
VIO_GREEN        = "#00E676"
VIO_RED          = "#FF1744"
VIO_YELLOW       = "#FFD600"
VIO_ORANGE       = "#FF6B35"
VIO_WHITE        = "#F0E6FF"   # Off-white with purple tint

LOGO_PATH = r"C:\Users\abhij\Desktop\VIO\EMI (28) (1).png"

def get_logo_b64():
    """Load logo as base64 for inline display."""
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

logo_b64 = get_logo_b64()
logo_html = (
    f"<img src='data:image/png;base64,{logo_b64}' "
    f"style='height:48px; margin-right:14px; vertical-align:middle; filter:drop-shadow(0 0 8px {VIO_PURPLE_NEON});'>"
    if logo_b64 else
    f"<span style='font-size:36px; font-weight:900; color:{VIO_PURPLE_NEON}; letter-spacing:4px; vertical-align:middle;'>VIO</span>"
)

sidebar_logo_html = (
    f"<img src='data:image/png;base64,{logo_b64}' "
    f"style='height:56px; display:block; margin:0 auto 8px; filter:drop-shadow(0 0 12px {VIO_PURPLE_NEON});'>"
    if logo_b64 else
    f"<div style='font-size:40px; font-weight:900; color:{VIO_PURPLE_NEON}; letter-spacing:4px;'>VIO</div>"
)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=Space+Grotesk:wght@400;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: linear-gradient(160deg, {VIO_PURPLE_DARK} 0%, #1A0535 50%, {VIO_PURPLE_DARK} 100%) !important;
        color: {VIO_WHITE};
        font-family: 'Inter', sans-serif;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0D011A 0%, {VIO_PURPLE_DARK} 60%, #0D011A 100%) !important;
        border-right: 1.5px solid {VIO_PURPLE_NEON}44;
        box-shadow: 4px 0 32px {VIO_PURPLE_GLOW};
    }}
    [data-testid="stSidebar"] * {{ color: {VIO_WHITE} !important; }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {{ color: #C8A8FF !important; }}

    /* Header */
    .vio-header {{
        background: linear-gradient(120deg, {VIO_PURPLE_DARK} 0%, {VIO_PURPLE_MID} 60%, {VIO_PURPLE_DARK} 100%);
        padding: 22px 30px;
        border-bottom: 2px solid {VIO_PURPLE_NEON}88;
        margin-bottom: 22px;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 4px 32px {VIO_PURPLE_GLOW};
        display: flex;
        align-items: center;
    }}

    /* Metric cards */
    [data-testid="metric-container"] {{
        background: {VIO_PURPLE_CARD} !important;
        border-radius: 12px !important;
        padding: 16px !important;
        border: 1px solid {VIO_PURPLE_NEON}33 !important;
        box-shadow: 0 2px 16px {VIO_PURPLE_GLOW} !important;
    }}
    [data-testid="metric-container"] label {{
        color: #C8A8FF !important;
        font-size: 11px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {VIO_WHITE} !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
    }}

    /* Alert boxes */
    .alert-box-critical {{ background:#2A0015; border:2px solid {VIO_RED}; border-radius:10px; padding:15px; margin:5px 0; box-shadow: 0 0 16px rgba(255,23,68,0.2); }}
    .alert-box-high     {{ background:#2A0F00; border:2px solid {VIO_ORANGE}; border-radius:10px; padding:15px; margin:5px 0; }}
    .alert-box-medium   {{ background:#2A2200; border:2px solid {VIO_YELLOW}; border-radius:10px; padding:15px; margin:5px 0; }}
    .alert-box-normal   {{ background:#001A2A; border:2px solid {VIO_GREEN}; border-radius:10px; padding:15px; margin:5px 0; }}

    /* Prediction cards */
    .pred-card {{
        background: {VIO_PURPLE_CARD};
        border-radius: 14px;
        padding: 22px;
        border: 1px solid {VIO_PURPLE_NEON}44;
        margin: 10px 0;
        box-shadow: 0 4px 24px {VIO_PURPLE_GLOW};
    }}

    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {VIO_PURPLE_MID} 0%, {VIO_PURPLE_NEON} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 2px 16px {VIO_PURPLE_GLOW} !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        box-shadow: 0 4px 28px {VIO_PURPLE_NEON}66 !important;
        transform: translateY(-1px) !important;
    }}

    /* Selectbox / inputs */
    .stSelectbox > div > div,
    .stTextInput > div > div {{
        background: {VIO_PURPLE_CARD} !important;
        border: 1px solid {VIO_PURPLE_NEON}44 !important;
        border-radius: 8px !important;
        color: {VIO_WHITE} !important;
    }}

    /* Dataframe */
    .stDataFrame {{
        border: 1px solid {VIO_PURPLE_NEON}33 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {VIO_PURPLE_CARD} !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #C8A8FF !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {VIO_PURPLE_NEON}33 !important;
        color: white !important;
    }}

    /* Progress bar */
    .stProgress > div > div {{
        background: linear-gradient(90deg, {VIO_PURPLE_MID}, {VIO_PURPLE_NEON}) !important;
    }}

    /* Divider */
    hr {{ border-color: {VIO_PURPLE_NEON}22 !important; }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: {VIO_PURPLE_CARD} !important;
        border: 1px solid {VIO_PURPLE_NEON}33 !important;
        border-radius: 8px !important;
        color: {VIO_WHITE} !important;
    }}

    /* Status indicators */
    .stSuccess {{ background: #001A10 !important; border-color: {VIO_GREEN} !important; }}
    .stWarning {{ background: #1A1000 !important; border-color: {VIO_YELLOW} !important; }}
    .stError   {{ background: #1A0008 !important; border-color: {VIO_RED} !important; }}
    .stInfo    {{ background: #10002A !important; border-color: {VIO_PURPLE_NEON} !important; }}

    /* Glow divider */
    .glow-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, {VIO_PURPLE_NEON}, transparent);
        margin: 18px 0;
        border: none;
    }}

    /* Section titles */
    h3 {{ color: {VIO_WHITE} !important; font-family: 'Space Grotesk', sans-serif !important; }}
    h4 {{ color: #C8A8FF !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important; }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

API_URL      = "http://127.0.0.1:8000"
PARQUET_PATH = r"C:\Users\abhij\Desktop\VIO\processed_data\final_fleet_telemetry.parquet"

@st.cache_data(ttl=300)
def load_data():
    cols = [
        'well_id', 'well_type', 'Log_Date_Time',
        'FTHP', 'CHP', 'ABP', 'GIP', 'FLT',
        'GIR', 'gir_scmd', 'Battery_Voltage'
    ]
    df = pd.read_parquet(PARQUET_PATH, columns=cols)
    df = df.sort_values(['well_id', 'Log_Date_Time']).reset_index(drop=True)
    return df

@st.cache_data(ttl=300)
def load_fleet_benchmarks():
    try:
        r = requests.get(f"{API_URL}/api/v1/fleet/benchmarks", timeout=5)
        if r.status_code == 200:
            return pd.DataFrame(r.json()["wells"])
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_well_data(df, well_id):
    return df[df['well_id'] == well_id].copy()

def plotly_dark_layout(fig, height=400, **kwargs):
    """Apply consistent purple dark theme to plotly figures."""
    fig.update_layout(
        paper_bgcolor=VIO_PURPLE_DARK,
        plot_bgcolor =VIO_PURPLE_CARD,
        font_color   =VIO_WHITE,
        font_family  ="Inter",
        height       =height,
        margin       =dict(l=10, r=10, t=40, b=10),
        legend=dict(
            bgcolor=VIO_PURPLE_CARD,
            bordercolor="rgba(168,50,255,0.27)",
            borderwidth=1
        ),
        xaxis=dict(gridcolor="rgba(168,50,255,0.09)", zerolinecolor="rgba(168,50,255,0.13)"),
        yaxis=dict(gridcolor="rgba(168,50,255,0.09)", zerolinecolor="rgba(168,50,255,0.13)"),
        **kwargs
    )
    return fig

def call_anomaly_api(row, well_id, well_type):
    try:
        payload = {
            "well_id"  : well_id,
            "well_type": well_type,
            "FTHP"     : float(row['FTHP']),
            "CHP"      : float(row['CHP']),
            "ABP"      : float(row['ABP']),
            "GIP"      : float(row.get('GIP', 0)),
            "FLT"      : float(row.get('FLT', 0)),
            "Battery_Voltage" : float(row['Battery_Voltage']),
            "FTHP_delta": 0.0, "CHP_delta": 0.0,
            "FTHP_rmean": float(row['FTHP']),
            "FTHP_rstd" : 0.1,
            "FTHP_zscore": 0.0,
            "CHP_rmean" : float(row['CHP']),
            "CHP_rstd"  : 0.1,
            "CHP_zscore": 0.0,
            "ABP_rmean" : float(row['ABP']),
            "ABP_rstd"  : 0.1,
            "ABP_zscore": 0.0,
            "GIP_rmean" : float(row.get('GIP', 0)),
            "GIP_rstd"  : 0.1,
            "GIP_zscore": 0.0,
            "FLT_rmean" : float(row.get('FLT', 0)),
            "FLT_rstd"  : 0.1,
            "FLT_zscore": 0.0,
            "Battery_Voltage_rmean"  : float(row['Battery_Voltage']),
            "Battery_Voltage_rstd"   : 0.1,
            "Battery_Voltage_zscore" : 0.0,
            "FTHP_CHP_diff" : float(row['FTHP']) - float(row['CHP']),
            "FTHP_ABP_diff" : float(row['FTHP']) - float(row['ABP']),
            "CHP_ABP_diff"  : float(row['CHP'])  - float(row['ABP']),
            "FTHP_lag1" : float(row['FTHP']),
            "CHP_lag1"  : float(row['CHP']),
            "ABP_lag1"  : float(row['ABP']),
            "hour_sin"  : float(np.sin(2 * np.pi * datetime.now().hour / 24)),
            "hour_cos"  : float(np.cos(2 * np.pi * datetime.now().hour / 24)),
            "month_sin" : float(np.sin(2 * np.pi * datetime.now().month / 12)),
            "month_cos" : float(np.cos(2 * np.pi * datetime.now().month / 12)),
        }
        r = requests.post(f"{API_URL}/api/v1/predict/anomaly", json=payload, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        return {"error": str(e)}
    return None

def call_maintenance_api(row, well_id, well_type):
    try:
        bat_v = float(row['Battery_Voltage'])
        payload = {
            "well_id"  : well_id,
            "well_type": well_type,
            "FTHP": float(row['FTHP']),
            "CHP" : float(row['CHP']),
            "ABP" : float(row['ABP']),
            "FLT" : float(row.get('FLT', 25.0)),
            "Battery_Voltage"        : bat_v,
            "battery_rolling_mean_12": bat_v,
            "battery_rolling_min_12" : bat_v * 0.98,
            "battery_trend"          : 0.0,
            "battery_health_score"   : (bat_v / 14.0) * 100,
            "FTHP_mean_24": float(row['FTHP']),
            "FTHP_std_24" : 0.5,
            "FTHP_roc"    : 0.0,
            "CHP_mean_24" : float(row['CHP']),
            "CHP_std_24"  : 0.5,
            "CHP_roc"     : 0.0,
            "ABP_mean_24" : float(row['ABP']),
            "ABP_std_24"  : 0.5,
            "ABP_roc"     : 0.0,
            "FLT_mean_24" : float(row.get('FLT', 25.0)),
            "FLT_std_24"  : 0.5,
            "FLT_roc"     : 0.0,
            "FTHP_drop_flag"      : 0,
            "CHP_drop_flag"       : 0,
            "FTHP_consec_drops"   : 0.0,
            "pressure_instability": 0.5,
            "FLT_high_flag"       : 0,
            "health_index"        : 1 - (bat_v / 14.0)
        }
        r = requests.post(f"{API_URL}/api/v1/predict/maintenance", json=payload, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        return {"error": str(e)}
    return None

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:22px 0 14px;'>
        {sidebar_logo_html}
        <div style='font-size:10px; color:#C8A8FF; letter-spacing:3px; text-transform:uppercase; margin-top:4px;'>Intelligence Platform</div>
        <div style='height:1px; background:linear-gradient(90deg,transparent,{VIO_PURPLE_NEON},transparent); margin:12px 0;'></div>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox("Select Module", [
        "Fleet Overview",
        "AI-01: Anomaly Detection",
        "AI-02: Predictive Maintenance",
        "AI-03: Gas Lift Optimization",
        "AI-04: Leak & Integrity",
        "AI-05: Production Optimization",
        "Fleet Alert Center",
        "Work Orders (CMMS)",
        "Feedback & Model Improvement",
        "API Documentation"
    ])

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    well_type_filter = st.selectbox("Flow Regime", ["All", "Self flow", "Gas lift"])
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    try:
        r = requests.get(f"{API_URL}/", timeout=3)
        if r.status_code == 200:
            st.success("VIO API Online")
        else:
            st.error("API Error")
    except:
        st.error("API Offline — Start server first")

    st.markdown(f"""
    <div style='margin-top:16px; padding:12px; background:{VIO_PURPLE_DARK}; border-radius:10px;
         border:1px solid {VIO_PURPLE_NEON}22; font-size:11px; color:#C8A8FF;'>
        <div style='margin-bottom:4px;'>Platform: VIO v2.0.0</div>
        <div style='margin-bottom:4px;'>Wells: 139 &nbsp;|&nbsp; Models: 5</div>
        <div style='color:{VIO_PURPLE_NEON}; font-weight:600; letter-spacing:1px;'>⬡ AI CAPABILITIES ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

with st.spinner("Loading VIO data..."):
    df = load_data()

if well_type_filter != "All":
    df_filtered = df[df['well_type'] == well_type_filter]
else:
    df_filtered = df

well_list = sorted(df_filtered['well_id'].unique().tolist())

def page_header(subtitle, badge="", icon=""):
    """Render a consistent page header with logo."""
    badge_html = f"<span style='float:right; font-size:11px; color:#C8A8FF; margin-top:6px;'>{badge}</span>" if badge else ""
    st.markdown(f"""
    <div class='vio-header'>
        {logo_html}
        <div style='display:inline-block; vertical-align:middle;'>
            <div style='font-size:11px; color:{VIO_PURPLE_NEON}; letter-spacing:2px; text-transform:uppercase; margin-bottom:2px;'>{icon}</div>
            <div style='font-size:24px; font-weight:800; color:{VIO_WHITE}; font-family:"Space Grotesk",sans-serif; letter-spacing:-0.5px;'>{subtitle}</div>
        </div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)



# ═════════════════════════════════════════════════════════════════
# PAGE 5: LEAK & INTEGRITY
# ═════════════════════════════════════════════════════════════════
if page == "AI-04: Leak & Integrity":
    page_header("Leak & Integrity Detection", icon="AI Capability 04")

    selected_well = st.selectbox("Select Well", well_list)
    well_data     = get_well_data(df, selected_well)
    latest        = well_data.iloc[-1]
    recent        = well_data.tail(300).copy()

    m1,m2,m3,m4 = st.columns(4)
    with m1: st.metric("FTHP", f"{latest['FTHP']:.1f} psi")
    with m2: st.metric("CHP",  f"{latest['CHP']:.1f} psi")
    with m3: st.metric("ABP",  f"{latest['ABP']:.1f} psi")
    with m4:
        scp = "YES" if latest['CHP'] > latest['FTHP'] * 1.5 else "NO"
        st.metric("SCP Alert", scp)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    recent['CHP_FTHP_diff'] = recent['CHP'] - recent['FTHP']
    recent['FTHP_diff']     = recent['FTHP'].diff().fillna(0)
    recent['sudden_drop']   = recent['FTHP_diff'] < -5

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Casing-Tubing Pressure Differential")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=recent['Log_Date_Time'], y=recent['CHP_FTHP_diff'], mode='lines', fill='tozeroy', fillcolor='rgba(255,23,68,0.1)', line=dict(color=VIO_RED, width=1.5), name='CHP-FTHP Diff'))
        fig.add_hline(y=0, line_color=VIO_WHITE, line_dash='dash')
        plotly_dark_layout(fig, height=320, yaxis_title="Differential (psi)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### FTHP Sudden Drop Events")
        drop_events = recent[recent['sudden_drop']]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=recent['Log_Date_Time'], y=recent['FTHP'], mode='lines', line=dict(color=VIO_PURPLE_NEON, width=1.5), name='FTHP'))
        if len(drop_events) > 0:
            fig2.add_trace(go.Scatter(x=drop_events['Log_Date_Time'], y=drop_events['FTHP'], mode='markers', marker=dict(color=VIO_RED, size=10, symbol='x'), name='Sudden Drop'))
        plotly_dark_layout(fig2, height=320, yaxis_title="FTHP (psi)")
        st.plotly_chart(fig2, use_container_width=True)

    scp_count  = int((recent['CHP'] > recent['FTHP'] * 1.5).sum())
    drop_count = int(recent['sudden_drop'].sum())
    flt_mean   = recent['FLT'].mean()
    flt_std    = recent['FLT'].std()
    cross_zone = int((((recent['FLT'] - flt_mean)/(flt_std+1e-6)).abs() > 2.5).sum())

    i1,i2,i3,i4 = st.columns(4)
    with i1: st.metric("SCP Events",       scp_count)
    with i2: st.metric("Sudden Drops",     drop_count)
    with i3: st.metric("Cross-Zone Flags", cross_zone)
    with i4:
        total_risk = scp_count + drop_count + cross_zone
        risk = "CRITICAL" if total_risk>50 else "HIGH" if total_risk>20 else "MEDIUM" if total_risk>5 else "LOW"
        st.metric("Overall Risk", risk)

# ═════════════════════════════════════════════════════════════════
# PAGE: API DOCUMENTATION
# ═════════════════════════════════════════════════════════════════
elif page == "API Documentation":
    page_header("VIO API Documentation")

    st.markdown("""
    ### Base URL
    `http://127.0.0.1:8000`

    ### Authentication
    Header: `X-API-Key: VIO-2024-SECRET-KEY`

    ### Endpoints
    | Method | Endpoint | Description |
    |--------|----------|-------------|
    | GET  | `/` | Health check |
    | POST | `/api/v1/predict/anomaly` | Anomaly Detection |
    | POST | `/api/v1/predict/maintenance` | Maintenance + RUL |
    | POST | `/api/v1/predict/gaslift` | Gas Lift Optimization |
    | POST | `/api/v1/predict/leak` | Leak & Integrity |
    | POST | `/api/v1/predict/production` | Production Optimization |
    | GET  | `/api/v1/fleet/benchmarks` | Fleet Benchmarks |
    | GET  | `/api/v1/fleet/summary` | Fleet Summary |

    ### Interactive Docs
    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    """)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("### Live API Tests")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Test Health Check"):
            try:
                r = requests.get(f"{API_URL}/", timeout=5)
                st.json(r.json())
            except Exception as e:
                st.error(str(e))
    with c2:
        if st.button("Test Fleet Summary"):
            try:
                r = requests.get(f"{API_URL}/api/v1/fleet/summary", timeout=5)
                st.json(r.json())
            except Exception as e:
                st.error(str(e))

