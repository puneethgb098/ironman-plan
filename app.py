"""IronPlan 70.3 — Main application entry point."""
import streamlit as st
from pathlib import Path
from datetime import date
from config import APP_TITLE, RACE_DATE, RACE_NAME, SPORT_LABELS, SPORT_COLORS
from data.store import load_workouts, is_plan_generated, save_workouts, load_athlete
from engine.plan_generator import generate_plan, generate_sample_completion_data
from engine.calendar_engine import days_to_race, get_todays_workouts, get_current_week_number, get_phase_dates
from engine.analytics import get_current_phase, calculate_ctl_atl_tsb, calculate_compliance, generate_insights
from components.cards import render_metric_card, render_workout_card, render_insight_card

st.set_page_config(
    page_title="IronPlan 70.3",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

if not is_plan_generated():
    workouts = generate_plan()
    today = date.today()
    workouts = generate_sample_completion_data(workouts, today)
    save_workouts(workouts)

# --- Sidebar Navigation ---
st.sidebar.markdown("## IronPlan 70.3")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="Home")
st.sidebar.page_link("pages/1_Dashboard.py", label="Dashboard")
st.sidebar.page_link("pages/2_Calendar.py", label="Calendar")
st.sidebar.page_link("pages/3_Workout_Log.py", label="Workout Log")
st.sidebar.page_link("pages/7_Upload.py", label="Upload")
st.sidebar.page_link("pages/8_Analytics.py", label="Analytics")
st.sidebar.page_link("pages/4_Profile.py", label="Profile")
st.sidebar.page_link("pages/5_Nutrition.py", label="Nutrition")
st.sidebar.page_link("pages/6_Race_Strategy.py", label="Race Strategy")

# --- Load Data ---
workouts = load_workouts()
athlete = load_athlete()
dtrace = days_to_race(RACE_DATE)
current_phase = get_current_phase(workouts)
current_week = get_current_week_number(workouts)
todays = get_todays_workouts(workouts)
phases = get_phase_dates(workouts)

# CTL/ATL/TSB
metrics_df = calculate_ctl_atl_tsb(workouts)
if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    ctl_val = float(latest["ctl"])
    atl_val = float(latest["atl"])
    tsb_val = float(latest["tsb"])
else:
    ctl_val = atl_val = tsb_val = 0.0

compliance = calculate_compliance(workouts)

# === HERO SECTION ===
st.title("IronPlan 70.3")
st.markdown(f"**{athlete.name}**'s {RACE_NAME} Training System")

hero1, hero2 = st.columns([3, 1])
with hero2:
    st.metric("Days to Race", int(dtrace))

st.markdown("---")

# === KEY METRICS ===
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Week", int(current_week or 0), delta="of 30")
with col2:
    phase_short = current_phase.split("+")[0].strip() if "+" in current_phase else current_phase[:14]
    st.metric("Phase", phase_short)
with col3:
    st.metric("Fitness (CTL)", f"{ctl_val:.0f}")
with col4:
    st.metric("Form (TSB)", f"{tsb_val:.0f}")
with col5:
    st.metric("Compliance", f"{float(compliance['overall']):.0f}%")
with col6:
    completed = len([w for w in workouts if w.status == "completed"])
    total = len([w for w in workouts if w.date <= str(date.today())])
    st.metric("Sessions", f"{completed}/{total}")

st.markdown("---")

# === TODAY'S TRAINING ===
st.markdown("### Today's Training")
if todays:
    for w in todays:
        render_workout_card(w, clickable=False)
else:
    st.info("No workouts scheduled for today. Rest well.")

st.markdown("---")

# === PHASE TIMELINE ===
st.markdown("### Training Phase Timeline")
if phases:
    phase_cols = st.columns(len(phases))
    for i, p in enumerate(phases):
        with phase_cols[i]:
            is_current = p["name"] == current_phase
            weeks = p.get("duration_weeks", 1)
            name = p["name"].split("+")[0].strip() if "+" in p["name"] else p["name"][:12]
            if is_current:
                st.markdown(f"**>> {name} ({weeks}w) <<**")
            else:
                st.caption(f"{name} ({weeks}w)")

# === INSIGHTS ===
insights = generate_insights(workouts)
if insights:
    st.markdown("### Quick Insights")
    i_cols = st.columns(min(3, len(insights)))
    for idx, insight in enumerate(insights[:3]):
        with i_cols[idx % 3]:
            render_insight_card(insight)

st.markdown("---")

# === QUICK NAV ===
st.markdown("### Quick Navigation")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.page_link("pages/1_Dashboard.py", label="Training Dashboard")
    st.page_link("pages/7_Upload.py", label="Upload Workout")
with col_b:
    st.page_link("pages/2_Calendar.py", label="Training Calendar")
    st.page_link("pages/8_Analytics.py", label="Deep Analytics")
with col_c:
    st.page_link("pages/3_Workout_Log.py", label="Log Workout")
    st.page_link("pages/4_Profile.py", label="Athlete Profile")

st.markdown("---")
st.caption(f"IronPlan 70.3 | Built for {athlete.name} | {RACE_NAME} — {RACE_DATE.strftime('%B %d, %Y')}")
