"""Analytics — Deep-dive performance analysis with per-sport breakdowns and daily completion stats."""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
from datetime import date, timedelta
from data.store import load_workouts, load_daily_completions
from engine.analytics import (
    calculate_ctl_atl_tsb, calculate_weekly_volume,
    calculate_compliance, calculate_intensity_distribution,
    calculate_zone_distribution_by_sport, calculate_ramp_rate,
    detect_build_recovery_weeks, calculate_weekly_metrics,
    calculate_rolling_averages, generate_insights,
    calculate_daily_completion_stats,
)
from config import SPORT_COLORS, SPORT_LABELS
from components.charts import (
    create_ctl_atl_tsb_chart, create_weekly_volume_chart,
    create_zone_distribution_chart, create_ramp_rate_chart,
    create_weekly_tss_chart,
)
from components.cards import render_insight_card

st.set_page_config(page_title="Analytics | IronPlan", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# Deep Analytics")

# --- Sidebar ---
st.sidebar.markdown("## Analysis Controls")
workouts = load_workouts()
completions = load_daily_completions()
today = date.today()

all_phases = list(set(w.phase for w in workouts if w.phase))
selected_phase = st.sidebar.selectbox("Phase", ["All"] + sorted(all_phases), key="anal_phase")
sport_focus = st.sidebar.radio("Sport Focus", ["Combined", "Swim", "Bike", "Run"], key="anal_sport")

# Filter
if selected_phase != "All":
    filtered = [w for w in workouts if w.phase == selected_phase]
else:
    filtered = workouts

if sport_focus != "Combined":
    sport_key = sport_focus.lower()
    sport_filtered = [w for w in filtered if w.sport == sport_key]
else:
    sport_filtered = filtered

# === DAILY COMPLETION OVERVIEW ===
completion_stats = calculate_daily_completion_stats(completions)
if completion_stats["total_days"] > 0:
    st.markdown("### Daily Completion Overview")
    dcs1, dcs2, dcs3, dcs4 = st.columns(4)
    with dcs1:
        st.metric("Days Tracked", completion_stats["total_days"])
    with dcs2:
        st.metric("Training Rate", f"{completion_stats['training_rate']:.0f}%")
    with dcs3:
        st.metric("Nutrition Rate", f"{completion_stats['nutrition_rate']:.0f}%")
    with dcs4:
        st.metric("Current Streak", f"{completion_stats['streak']} days")
    st.markdown("---")

# === CTL/ATL/TSB ===
st.markdown("### Performance Model (CTL / ATL / TSB)")
metrics_df = calculate_ctl_atl_tsb(workouts)  # Always use all workouts for CTL
if not metrics_df.empty:
    fig = create_ctl_atl_tsb_chart(metrics_df, height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Rolling averages
    st.markdown("#### Rolling Averages")
    window = st.slider("Window (days)", 7, 42, 14, key="rolling_window")
    rolling_df = calculate_rolling_averages(workouts, window)
    if not rolling_df.empty:
        fig_roll = go.Figure()
        fig_roll.add_trace(go.Scatter(
            x=rolling_df["date"], y=rolling_df[f"tss_avg_{window}d"].astype(float),
            name=f"TSS ({window}d avg)", line=dict(color="#6C5CE7", width=2),
            fill="tozeroy", fillcolor="rgba(108,92,231,0.1)",
        ))
        fig_roll.update_layout(
            template="plotly_dark", height=250,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="", yaxis_title=f"TSS ({window}d avg)",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_roll, use_container_width=True)
else:
    st.info("No training data available for performance analysis.")

st.markdown("---")

# === Volume Analysis ===
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("### Weekly Volume")
    volume_df = calculate_weekly_volume(sport_filtered)
    if not volume_df.empty:
        fig_vol = create_weekly_volume_chart(volume_df)
        st.plotly_chart(fig_vol, use_container_width=True)

with col_v2:
    st.markdown("### Weekly TSS Progression")
    vol_all = calculate_weekly_volume(filtered)
    if not vol_all.empty:
        fig_tss = create_weekly_tss_chart(vol_all)
        st.plotly_chart(fig_tss, use_container_width=True)

st.markdown("---")

# === Zone Distribution ===
st.markdown("### Zone Distribution Analysis")
z1, z2, z3, z4 = st.columns(4)

with z1:
    st.markdown("**Overall**")
    overall_dist = calculate_intensity_distribution(sport_filtered)
    if any(v > 0 for v in overall_dist.values()):
        st.plotly_chart(create_zone_distribution_chart(overall_dist, 220), use_container_width=True)

zone_by_sport = calculate_zone_distribution_by_sport(filtered)
for i, sport in enumerate(["swim", "bike", "run"]):
    with [z2, z3, z4][i]:
        label = SPORT_LABELS.get(sport, sport.upper())
        st.markdown(f"**{label} ({sport.capitalize()})**")
        sdist = zone_by_sport.get(sport, {})
        if any(v > 0 for v in sdist.values()):
            st.plotly_chart(create_zone_distribution_chart(sdist, 220), use_container_width=True)
        else:
            st.caption("No data")

st.markdown("---")

# === Ramp Rate ===
st.markdown("### Load Progression and Ramp Rate")
ramp_df = calculate_ramp_rate(workouts)
if not ramp_df.empty:
    fig_ramp = create_ramp_rate_chart(ramp_df, height=300)
    st.plotly_chart(fig_ramp, use_container_width=True)

    # Build/Recovery week detection
    st.markdown("#### Build / Recovery Week Pattern")
    week_types = detect_build_recovery_weeks(workouts)
    if week_types:
        # Show as a dataframe
        import pandas as pd
        wt_df = pd.DataFrame(week_types)
        wt_df = wt_df[["week_number", "type", "total_tss", "phase", "is_deload"]]
        wt_df.columns = ["Week", "Type", "Total TSS", "Phase", "Deload"]
        st.dataframe(wt_df, use_container_width=True, hide_index=True)

st.markdown("---")

# === Phase Comparison ===
st.markdown("### Phase-by-Phase Comparison")
if all_phases:
    phase_data = []
    for phase in sorted(all_phases):
        pw = [w for w in workouts if w.phase == phase and w.status != "skipped"]
        if not pw:
            continue
        total_hrs = float(sum(int(w.actual_duration_min or w.planned_duration_min or 0) for w in pw)) / 60.0
        total_tss = int(sum(int(w.tss_actual or w.tss_planned or 0) for w in pw))
        completed = sum(1 for w in pw if w.status in ("completed", "modified"))
        total = len(pw)
        phase_data.append({
            "Phase": phase.split("+")[0].strip()[:20],
            "Sessions": total,
            "Hours": round(total_hrs, 1),
            "TSS": total_tss,
            "Compliance": f"{float(completed)/float(total)*100:.0f}%" if total > 0 else "N/A",
        })

    if phase_data:
        import pandas as pd
        st.dataframe(pd.DataFrame(phase_data), use_container_width=True, hide_index=True)

# === Insights ===
st.markdown("---")
st.markdown("### Performance Insights")
insights = generate_insights(workouts)
if insights:
    for insight in insights:
        render_insight_card(insight)

st.markdown("---")
st.caption("Analytics recalculate from all workout data in real-time.")
