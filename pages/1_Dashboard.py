"""Training Dashboard — CTL/ATL/TSB, volume, compliance, readiness, insights."""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
from datetime import date, timedelta
from data.store import load_workouts, load_daily_logs, load_athlete
from engine.analytics import (
    calculate_ctl_atl_tsb, calculate_weekly_volume,
    calculate_compliance, calculate_intensity_distribution,
    calculate_zone_distribution_by_sport, calculate_readiness,
    get_current_phase, calculate_ramp_rate, generate_insights,
    calculate_weekly_metrics,
)
from engine.calendar_engine import days_to_race
from config import RACE_DATE, SPORT_COLORS, SPORT_ICONS, TSB_THRESHOLDS
from data.models import DailyLog
from components.charts import (
    create_ctl_atl_tsb_chart, create_weekly_volume_chart,
    create_zone_distribution_chart, create_ramp_rate_chart,
    create_compliance_chart, create_weekly_tss_chart,
)
from components.cards import render_metric_card, render_insight_card

st.set_page_config(page_title="Dashboard | IronPlan", page_icon="📊", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.markdown("## 📊 Dashboard")
st.sidebar.markdown("---")
date_range = st.sidebar.radio("Period", ["All Time", "Last 30 Days", "Last 90 Days", "This Phase"],
                               key="dash_period", horizontal=False)

# --- Load Data ---
workouts = load_workouts()
athlete = load_athlete()
daily_logs = load_daily_logs()
today = date.today()
today_str = str(today)

# Apply date filter
if date_range == "Last 30 Days":
    filtered_workouts = [w for w in workouts if w.date >= str(today - timedelta(days=30))]
elif date_range == "Last 90 Days":
    filtered_workouts = [w for w in workouts if w.date >= str(today - timedelta(days=90))]
elif date_range == "This Phase":
    current_phase = get_current_phase(workouts)
    filtered_workouts = [w for w in workouts if w.phase == current_phase]
else:
    filtered_workouts = workouts

st.markdown("# 📊 Training Dashboard")

# === TOP METRICS ROW ===
metrics_df = calculate_ctl_atl_tsb(workouts)
compliance = calculate_compliance(filtered_workouts)
intensity_dist = calculate_intensity_distribution(filtered_workouts)

if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    ctl_val = latest["ctl"]
    atl_val = latest["atl"]
    tsb_val = latest["tsb"]
else:
    ctl_val = atl_val = tsb_val = 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    render_metric_card("CTL · Fitness", f"{ctl_val:.0f}", "42-day avg", color="#0984E3", icon="💪")
with c2:
    render_metric_card("ATL · Fatigue", f"{atl_val:.0f}", "7-day avg", color="#E17055", icon="🔥")
with c3:
    tsb_color = "#00B894" if tsb_val > 5 else "#D63031" if tsb_val < -10 else "#FDCB6E"
    tsb_label = "Fresh ✅" if tsb_val > 5 else "Fatigued ⚠️" if tsb_val < -10 else "Balanced"
    render_metric_card("TSB · Form", f"{tsb_val:.0f}", tsb_label, color=tsb_color, icon="📈")
with c4:
    render_metric_card("Compliance", f"{compliance['overall']:.0f}%", "", color="#00B894" if compliance['overall'] >= 80 else "#FDCB6E", icon="✅")
with c5:
    dtr = days_to_race(RACE_DATE)
    render_metric_card("Days to Race", str(dtr), RACE_DATE.strftime("%b %d"), icon="🏁")
with c6:
    current_phase = get_current_phase(workouts)
    phase_short = current_phase.split("+")[0].strip() if "+" in current_phase else current_phase[:15]
    render_metric_card("Phase", phase_short, "", icon="🗺️")

st.markdown("---")

# === CTL / ATL / TSB ===
st.markdown("### 📈 Training Load Over Time")
if not metrics_df.empty:
    fig_perf = create_ctl_atl_tsb_chart(metrics_df)
    st.plotly_chart(fig_perf, use_container_width=True)
else:
    st.info("Complete some workouts to see your training load chart.")

# === Weekly Volume + Zone Distribution ===
st.markdown("---")
col_vol, col_dist = st.columns([2, 1])

with col_vol:
    st.markdown("### 📊 Weekly Volume by Sport")
    volume_df = calculate_weekly_volume(filtered_workouts)
    if not volume_df.empty:
        fig_vol = create_weekly_volume_chart(volume_df)
        st.plotly_chart(fig_vol, use_container_width=True)

with col_dist:
    st.markdown("### 🎯 Intensity Distribution")
    if any(v > 0 for v in intensity_dist.values()):
        fig_int = create_zone_distribution_chart(intensity_dist)
        st.plotly_chart(fig_int, use_container_width=True)
        target_text = "✅ Good balance" if intensity_dist["easy"] >= 70 else "⚠️ Too much intensity"
        st.caption(f"80/20 check: {intensity_dist['easy']:.0f}% easy — {target_text}")

# === Ramp Rate + Weekly TSS ===
st.markdown("---")
col_ramp, col_tss = st.columns(2)

with col_ramp:
    st.markdown("### 🔥 Ramp Rate")
    ramp_df = calculate_ramp_rate(workouts)
    if not ramp_df.empty:
        fig_ramp = create_ramp_rate_chart(ramp_df)
        st.plotly_chart(fig_ramp, use_container_width=True)
    else:
        st.caption("Need more data for ramp rate analysis.")

with col_tss:
    st.markdown("### 📊 Weekly TSS")
    if not volume_df.empty:
        fig_tss = create_weekly_tss_chart(volume_df)
        st.plotly_chart(fig_tss, use_container_width=True)

# === Compliance + Zone by Sport ===
st.markdown("---")
col_comp, col_zone_sport = st.columns(2)

with col_comp:
    st.markdown("### ✅ Compliance by Sport")
    fig_comp = create_compliance_chart(compliance)
    st.plotly_chart(fig_comp, use_container_width=True)

with col_zone_sport:
    st.markdown("### 🏅 Zone Distribution by Sport")
    zone_by_sport = calculate_zone_distribution_by_sport(filtered_workouts)
    sport_tab = st.radio("Sport", ["swim", "bike", "run"], horizontal=True, key="zone_sport_tab",
                          label_visibility="collapsed")
    sdist = zone_by_sport.get(sport_tab, {"easy": 0, "moderate": 0, "hard": 0})
    if any(v > 0 for v in sdist.values()):
        fig_sdist = create_zone_distribution_chart(sdist, height=250)
        st.plotly_chart(fig_sdist, use_container_width=True)
    else:
        st.caption(f"No {sport_tab} data yet.")

# === Readiness ===
st.markdown("---")
st.markdown("### 🔋 Today's Readiness")
today_log = daily_logs.get(today_str, DailyLog(date=today_str))
readiness = calculate_readiness(today_log, tsb=tsb_val, rhr_baseline=athlete.resting_hr)

r_col1, r_col2 = st.columns([1, 2])
with r_col1:
    score = readiness["overall"]
    status = readiness["status"]
    color_map = {"ready": "#00B894", "moderate": "#FDCB6E", "fatigued": "#E17055", "overtrained": "#D63031"}
    r_color = color_map.get(status, "#636E72")
    advice = {
        "ready": "Push hard today 💪",
        "moderate": "Train normally, monitor feel",
        "fatigued": "Consider reducing intensity",
        "overtrained": "Rest day recommended ⛔",
    }

    st.markdown(f"""
    <div class="readiness-gauge">
        <div class="readiness-score" style="color:{r_color};">{score:.0f}</div>
        <div style="font-size:1.1rem; color:{r_color}; font-weight:600; text-transform:uppercase;">{status}</div>
        <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:8px;">
            {advice.get(status, '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

with r_col2:
    components = readiness.get("components", {})
    if components:
        fig_r = go.Figure(go.Bar(
            x=list(components.values()),
            y=[k.upper() for k in components.keys()],
            orientation="h",
            marker_color=[
                "#00B894" if v >= 70 else "#FDCB6E" if v >= 40 else "#D63031"
                for v in components.values()
            ],
            text=[f"{v:.0f}" for v in components.values()],
            textposition="auto",
        ))
        fig_r.update_layout(
            template="plotly_dark", height=220,
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(range=[0, 100], title="Score"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Log readiness data to see detailed scores.")

# === Training Insights ===
st.markdown("---")
st.markdown("### 💡 Training Insights")
insights = generate_insights(workouts)
if insights:
    i_cols = st.columns(min(3, len(insights)))
    for idx, insight in enumerate(insights[:6]):
        with i_cols[idx % 3]:
            render_insight_card(insight)
else:
    st.caption("Complete more workouts to unlock training insights.")

st.markdown("---")
st.caption("Dashboard updates automatically as you complete workouts and upload data.")
