"""Training Dashboard — CTL/ATL/TSB, volume, compliance, readiness."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import date
from data.store import load_workouts, load_daily_logs, load_athlete
from engine.analytics import (
    calculate_ctl_atl_tsb, calculate_weekly_volume,
    calculate_compliance, calculate_intensity_distribution,
    calculate_readiness, get_current_phase
)
from engine.calendar_engine import days_to_race
from config import RACE_DATE, SPORT_COLORS, TSB_THRESHOLDS
from data.models import DailyLog

st.set_page_config(page_title="Dashboard | IronPlan", page_icon="📊", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# 📊 Training Dashboard")

workouts = load_workouts()
athlete = load_athlete()
daily_logs = load_daily_logs()
today_str = str(date.today())

# --- Top metrics row ---
col1, col2, col3, col4, col5 = st.columns(5)

metrics_df = calculate_ctl_atl_tsb(workouts)
compliance = calculate_compliance(workouts)
intensity_dist = calculate_intensity_distribution(workouts)

if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    ctl_val = latest["ctl"]
    atl_val = latest["atl"]
    tsb_val = latest["tsb"]
else:
    ctl_val = atl_val = tsb_val = 0

with col1:
    st.metric("CTL (Fitness)", f"{ctl_val:.0f}", help="Chronic Training Load — 42-day avg")
with col2:
    st.metric("ATL (Fatigue)", f"{atl_val:.0f}", help="Acute Training Load — 7-day avg")
with col3:
    tsb_delta = "Fresh ✅" if tsb_val > 5 else ("Fatigued ⚠️" if tsb_val < -10 else "Balanced")
    st.metric("TSB (Form)", f"{tsb_val:.0f}", delta=tsb_delta)
with col4:
    st.metric("Compliance", f"{compliance['overall']:.0f}%")
with col5:
    st.metric("Days to Race", days_to_race(RACE_DATE))

st.markdown("---")

# --- CTL / ATL / TSB Chart ---
st.markdown("### 📈 Training Load Over Time")
if not metrics_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=metrics_df["date"], y=metrics_df["ctl"],
        name="CTL (Fitness)", line=dict(color="#0984E3", width=3),
        fill="tozeroy", fillcolor="rgba(9,132,227,0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=metrics_df["date"], y=metrics_df["atl"],
        name="ATL (Fatigue)", line=dict(color="#E17055", width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=metrics_df["date"], y=metrics_df["tsb"],
        name="TSB (Form)", line=dict(color="#00B894", width=2),
        fill="tozeroy", fillcolor="rgba(0,184,148,0.05)",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    fig.add_hline(y=TSB_THRESHOLDS["overreaching"], line_dash="dot",
                  line_color="#D63031", opacity=0.4, annotation_text="Overreaching")
    fig.add_hline(y=TSB_THRESHOLDS["race_ready_low"], line_dash="dot",
                  line_color="#00B894", opacity=0.4, annotation_text="Race Ready")

    fig.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="", yaxis_title="TSS",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("No training data yet. Complete some workouts to see your training load chart.")

# --- Weekly Volume Chart ---
st.markdown("---")
col_vol, col_dist = st.columns([2, 1])

with col_vol:
    st.markdown("### 📊 Weekly Volume by Sport")
    volume_df = calculate_weekly_volume(workouts)
    if not volume_df.empty:
        fig_vol = go.Figure()
        for sport in ["swim", "bike", "run", "strength", "mobility"]:
            if sport in volume_df.columns:
                fig_vol.add_trace(go.Bar(
                    x=volume_df["week_number"],
                    y=volume_df[sport],
                    name=sport.capitalize(),
                    marker_color=SPORT_COLORS.get(sport, "#636E72"),
                ))
        fig_vol.update_layout(
            barmode="stack",
            template="plotly_dark",
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Week", yaxis_title="Hours",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_vol, width="stretch")

with col_dist:
    st.markdown("### 🎯 Intensity Distribution")
    if any(v > 0 for v in intensity_dist.values()):
        fig_int = go.Figure(go.Pie(
            labels=["Easy (Z1-2)", "Moderate (Z3)", "Hard (Z4-5)"],
            values=[intensity_dist["easy"], intensity_dist["moderate"], intensity_dist["hard"]],
            marker_colors=["#00B894", "#FDCB6E", "#D63031"],
            hole=0.5,
            textinfo="percent+label",
        ))
        fig_int.update_layout(
            template="plotly_dark",
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_int, width="stretch")

        target_text = "✅ Good" if intensity_dist["easy"] >= 70 else "⚠️ Too much intensity"
        st.caption(f"80/20 check: {intensity_dist['easy']:.0f}% easy — {target_text}")

# --- Compliance by Sport ---
st.markdown("---")
st.markdown("### ✅ Compliance by Sport")
comp_cols = st.columns(5)
for i, sport in enumerate(["swim", "bike", "run", "strength", "mobility"]):
    with comp_cols[i]:
        val = compliance.get(sport, 0)
        color = "#00B894" if val >= 80 else ("#FDCB6E" if val >= 60 else "#D63031")
        from config import SPORT_ICONS
        icon = SPORT_ICONS.get(sport, "❓")
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.5rem;">{icon}</div>
            <div style="font-size:1.8rem; font-weight:700; color:{color};">{val:.0f}%</div>
            <div class="metric-label">{sport}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Readiness ---
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

    st.markdown(f"""
    <div class="readiness-gauge">
        <div class="readiness-score" style="color:{r_color};">{score:.0f}</div>
        <div style="font-size:1.1rem; color:{r_color}; font-weight:600; text-transform:uppercase;">{status}</div>
        <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:8px;">
            {"Push hard today 💪" if status == "ready" else
             "Train normally, monitor feel" if status == "moderate" else
             "Consider reducing intensity" if status == "fatigued" else
             "Rest day recommended ⛔"}
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
        ))
        fig_r.update_layout(
            template="plotly_dark", height=250,
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(range=[0, 100], title="Score"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_r, width="stretch")
    else:
        st.info("Log today's readiness data (sleep, soreness, motivation) to see detailed scores.")

st.markdown("---")
st.caption("Dashboard updates as you complete workouts and log daily readiness data.")
