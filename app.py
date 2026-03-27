"""IronPlan 70.3 — Main application entry point."""
import streamlit as st
from pathlib import Path
from datetime import date
from config import APP_TITLE, RACE_DATE, RACE_NAME, SPORT_ICONS, INTENSITY_COLORS
from data.store import load_workouts, is_plan_generated, save_workouts, load_athlete
from engine.plan_generator import generate_plan, generate_sample_completion_data
from engine.calendar_engine import days_to_race, get_todays_workouts, get_current_week_number, get_phase_dates
from engine.analytics import get_current_phase, calculate_ctl_atl_tsb, calculate_compliance, generate_insights
from components.cards import render_metric_card, render_workout_card, render_insight_card

st.set_page_config(
    page_title="IronPlan 70.3",
    page_icon="🏊",
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
st.sidebar.markdown("## 🏊🚴🏃 IronPlan 70.3")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/1_Dashboard.py", label="📊 Dashboard", icon="📊")
st.sidebar.page_link("pages/2_Calendar.py", label="📅 Calendar", icon="📅")
st.sidebar.page_link("pages/3_Workout_Log.py", label="✏️ Workout Log", icon="✏️")
st.sidebar.page_link("pages/7_Upload.py", label="📤 Upload", icon="📤")
st.sidebar.page_link("pages/8_Analytics.py", label="📈 Analytics", icon="📈")
st.sidebar.page_link("pages/4_Profile.py", label="👤 Profile", icon="👤")
st.sidebar.page_link("pages/5_Nutrition.py", label="🍎 Nutrition", icon="🍎")
st.sidebar.page_link("pages/6_Race_Strategy.py", label="🏁 Race Strategy", icon="🏁")

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
    ctl_val = latest["ctl"]
    atl_val = latest["atl"]
    tsb_val = latest["tsb"]
else:
    ctl_val = atl_val = tsb_val = 0

compliance = calculate_compliance(workouts)

# === HERO SECTION ===
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0984E3, #6C5CE7); border-radius:16px;
    padding:30px 36px; margin-bottom:24px; color:white;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-size:2rem; font-weight:800;">IronPlan 70.3</div>
            <div style="font-size:1rem; opacity:0.9; margin-top:4px;">
                {athlete.name}'s {RACE_NAME} Training System
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:3.5rem; font-weight:800; line-height:1;">{dtrace}</div>
            <div style="font-size:0.9rem; opacity:0.85;">days to race</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# === KEY METRICS ===
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    render_metric_card("Week", str(current_week), "of 30", icon="📅")
with col2:
    phase_short = current_phase.split("+")[0].strip() if "+" in current_phase else current_phase[:14]
    render_metric_card("Phase", phase_short, "", icon="🗺️")
with col3:
    render_metric_card("Fitness", f"{ctl_val:.0f}", "CTL", color="#0984E3", icon="💪")
with col4:
    tsb_color = "#00B894" if tsb_val > 5 else "#D63031" if tsb_val < -10 else "#FDCB6E"
    render_metric_card("Form", f"{tsb_val:.0f}", "TSB", color=tsb_color, icon="📈")
with col5:
    render_metric_card("Compliance", f"{compliance['overall']:.0f}%", "", color="#00B894", icon="✅")
with col6:
    completed = len([w for w in workouts if w.status == "completed"])
    total = len([w for w in workouts if w.date <= str(date.today())])
    render_metric_card("Sessions", f"{completed}/{total}", "completed", icon="🏋️")

st.markdown("---")

# === TODAY'S TRAINING ===
st.markdown("### 📅 Today's Training")
if todays:
    for w in todays:
        render_workout_card(w, clickable=False)
else:
    st.info("🏖️ No workouts scheduled for today. Rest well!")

st.markdown("---")

# === PHASE TIMELINE ===
st.markdown("### 🗺️ Training Phase Timeline")
if phases:
    timeline_html = '<div style="display:flex; gap:4px; margin-bottom:20px;">'
    total_weeks = sum(p.get("duration_weeks", 1) for p in phases)
    for p in phases:
        weeks = p.get("duration_weeks", 1)
        color = p.get("color", "#636E72")
        is_current = p["name"] == current_phase
        border = "3px solid white" if is_current else "none"
        opacity = "1" if is_current else "0.6"
        scale = "1.02" if is_current else "1"

        timeline_html += f"""
        <div style="flex:{weeks}; background:{color}; border-radius:8px; padding:14px 8px;
            text-align:center; opacity:{opacity}; border:{border}; transition:all 0.3s;
            transform:scale({scale});">
            <div style="font-size:0.7rem; font-weight:700; color:white; text-transform:uppercase;">
                {p['name'].split('+')[0].strip() if '+' in p['name'] else p['name'][:12]}
            </div>
            <div style="font-size:0.65rem; color:rgba(255,255,255,0.8);">{weeks}w</div>
        </div>"""
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# === INSIGHTS ===
insights = generate_insights(workouts)
if insights:
    st.markdown("### 💡 Quick Insights")
    i_cols = st.columns(min(3, len(insights)))
    for idx, insight in enumerate(insights[:3]):
        with i_cols[idx % 3]:
            render_insight_card(insight)

st.markdown("---")

# === QUICK NAV ===
st.markdown("### 🎯 Quick Navigation")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.page_link("pages/1_Dashboard.py", label="📊 Training Dashboard", icon="📊")
    st.page_link("pages/7_Upload.py", label="📤 Upload Workout", icon="📤")
with col_b:
    st.page_link("pages/2_Calendar.py", label="📅 Training Calendar", icon="📅")
    st.page_link("pages/8_Analytics.py", label="📈 Deep Analytics", icon="📈")
with col_c:
    st.page_link("pages/3_Workout_Log.py", label="✏️ Log Workout", icon="✏️")
    st.page_link("pages/4_Profile.py", label="👤 Athlete Profile", icon="👤")

st.markdown("---")
st.caption(f"IronPlan 70.3 | Built for {athlete.name} | {RACE_NAME} — {RACE_DATE.strftime('%B %d, %Y')}")
