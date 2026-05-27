import sys
import os

# Ensure project root is on path regardless of where streamlit is run from
_PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJ_ROOT not in sys.path:
    sys.path.insert(0, _PROJ_ROOT)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

st.set_page_config(page_title="Smart Ride AI", page_icon="🚗", layout="wide")

st.markdown("""
<style>
.stApp{background:#07070f;color:#c8c8e8}
.kpi{background:#0d0d1a;border:1px solid #2a2a4a;border-radius:10px;padding:14px;text-align:center}
.kv{font-size:2rem;font-weight:700}
.kl{font-size:0.7rem;color:#666;letter-spacing:1.5px;text-transform:uppercase}
.ac{background:#1a0505;border-left:3px solid #ff2222;padding:6px 10px;border-radius:3px;margin:3px 0;font-size:0.82rem}
.aw{background:#1a1005;border-left:3px solid #ff9900;padding:6px 10px;border-radius:3px;margin:3px 0;font-size:0.82rem}
.ai{background:#05050f;border-left:3px solid #00aaff;padding:6px 10px;border-radius:3px;margin:3px 0;font-size:0.82rem}
h1,h2,h3{color:#00ffcc !important}
</style>
""", unsafe_allow_html=True)

# Resolve data directory relative to this file
_DATA_DIR = os.path.join(_PROJ_ROOT, "smart_ride_ai", "data")


@st.cache_data
def load():
    susp_path  = os.path.join(_DATA_DIR, "suspension_data.csv")
    alert_path = os.path.join(_DATA_DIR, "alerts.csv")
    mem_path   = os.path.join(_DATA_DIR, "road_memory.json")

    if not os.path.exists(susp_path):
        st.error(
            f"Data not found at: {susp_path}\n\n"
            "**Run the Colab notebook first** to generate simulation data, "
            "then re-launch the dashboard."
        )
        st.stop()

    df  = pd.read_csv(susp_path)
    al  = pd.read_csv(alert_path) if os.path.exists(alert_path) else pd.DataFrame()
    mem = {}
    if os.path.exists(mem_path):
        with open(mem_path) as f:
            mem = json.load(f)
    return df, al, mem


df, df_al, mem = load()

st.sidebar.title("control panel")
tr = st.sidebar.slider(
    "time window (s)",
    float(df.ts.min()), float(df.ts.max()),
    (float(df.ts.min()), float(df.ts.max()))
)
show_s = st.sidebar.checkbox("suspension comparison", True)
show_h = st.sidebar.checkbox("road heatmap", True)
show_m = st.sidebar.checkbox("road memory", True)

dv = df[(df.ts >= tr[0]) & (df.ts <= tr[1])]

st.title("Smart Ride AI")
st.caption("road condition · vibration · adaptive suspension · predictive alerts")
st.divider()

c1, c2, c3, c4, c5 = st.columns(5)


def kpi(col, val, label, good_thresh):
    try:
        numeric = float(str(val).replace("+", ""))
        clr = "#00ff88" if numeric > good_thresh else "#ff2222"
    except ValueError:
        clr = "#aaaaaa"
    col.markdown(
        f'<div class="kpi"><div class="kv" style="color:{clr}">{val}</div>'
        f'<div class="kl">{label}</div></div>',
        unsafe_allow_html=True
    )


kpi(c1, f"{dv.pred_comfort.mean():.0f}",    "avg comfort",   60)
kpi(c2, f"{dv.rms.mean():.2f}",             "vibration rms", 99)
kpi(c3, f"{int(dv.pothole_count.sum())}",   "total potholes", 99)
kpi(c4, f"+{dv.gain.mean():.1f}",           "comfort gain",  0)
kpi(c5, f"{int((dv.roughness > 80).sum())}", "critical zones", 99)

st.divider()
cl, cr = st.columns([2, 1])

with cl:
    st.subheader("ride intelligence timeline")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("comfort score", "vibration RMS", "roughness"))
    fig.add_trace(go.Scatter(x=dv.ts, y=dv.pred_comfort, fill="tozeroy",
                             line_color="#00ffcc", fillcolor="rgba(0,255,204,0.08)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=dv.ts, y=dv.rms, fill="tozeroy",
                             line_color="#ff4466", fillcolor="rgba(255,68,102,0.08)"), row=2, col=1)
    fig.add_trace(go.Scatter(x=dv.ts, y=dv.roughness, fill="tozeroy",
                             line_color="#ff9900", fillcolor="rgba(255,153,0,0.08)"), row=3, col=1)
    fig.update_layout(height=400, paper_bgcolor="#0a0a0f", plot_bgcolor="#111118",
                      font_color="#aaa", showlegend=False)
    fig.update_xaxes(gridcolor="#1a1a2e")
    fig.update_yaxes(gridcolor="#1a1a2e")
    st.plotly_chart(fig, use_container_width=True)

with cr:
    st.subheader("live alerts")
    if not df_al.empty:
        filtered = df_al[(df_al.ts >= tr[0]) & (df_al.ts <= tr[1])].tail(14)
        for _, row in filtered.iterrows():
            css = "ac" if row.sev == "CRITICAL" else "aw" if row.sev == "WARNING" else "ai"
            st.markdown(
                f'<div class="{css}"><small>{row.ts:.1f}s</small>  {row.alert}</div>',
                unsafe_allow_html=True
            )
    else:
        st.info("no alerts in range")

st.divider()

if show_s:
    st.subheader("adaptive vs passive suspension")
    f2 = go.Figure()
    f2.add_trace(go.Scatter(x=dv.ts, y=dv.adaptive_c, name="adaptive",
                            line=dict(color="#00ffcc", width=2)))
    f2.add_trace(go.Scatter(x=dv.ts, y=dv.passive_c, name="passive",
                            line=dict(color="#ff4466", width=1.5, dash="dash")))
    f2.update_layout(height=280, paper_bgcolor="#0a0a0f", plot_bgcolor="#111118", font_color="#aaa")
    f2.update_xaxes(gridcolor="#1a1a2e", title="time s")
    f2.update_yaxes(gridcolor="#1a1a2e", title="comfort")
    st.plotly_chart(f2, use_container_width=True)

if show_h:
    st.subheader("road roughness heatmap")
    pv = dv.copy()
    pv["lane"] = (pv["pothole_count"] % 5).astype(int)
    f3 = px.density_heatmap(pv, x="ts", y="lane", z="roughness", nbinsx=60, nbinsy=5,
                             color_continuous_scale=["#050510", "#003311", "#00ff44",
                                                     "#ffdd00", "#ff4400", "#ff0000"])
    f3.update_layout(height=220, paper_bgcolor="#0a0a0f", font_color="#aaa")
    st.plotly_chart(f3, use_container_width=True)

if show_m and mem.get("segments"):
    st.subheader("road memory")
    segs = pd.DataFrame(mem["segments"])
    ca, cb = st.columns([2, 1])
    with ca:
        st.dataframe(segs[["id", "ts", "roughness", "potholes", "comfort", "severity"]], height=280)
    with cb:
        vc = segs["severity"].value_counts()
        f4 = px.pie(values=vc.values, names=vc.index, hole=0.4,
                    color_discrete_map={"CRITICAL": "#ff2222", "WARNING": "#ff9900", "CAUTION": "#ffdd00"})
        f4.update_layout(paper_bgcolor="#0a0a0f", font_color="#aaa", height=260)
        st.plotly_chart(f4, use_container_width=True)

st.divider()
st.caption("Smart Ride AI · OpenCV · scikit-learn · Streamlit · Plotly")
