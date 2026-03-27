"""IronPlan 70.3 — Main application entry point."""
import streamlit as st
from pathlib import Path
from datetime import date
from config import APP_TITLE, RACE_DATE, RACE_NAME
from data.store import load_workouts, is_plan_generated, save_workouts, load_athlete
from engine.plan_generator import generate_plan, generate_sample_completion_data
from engine.calendar_engine import days_to_race, get_todays_workouts, get_current_week_number, get_phase_dates
from engine.analytics import get_current_phase

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

st.markdown(f"# {APP_TITLE}")

dtrace = days_to_race(RACE_DATE)
workouts = load_workouts()
athlete = load_athlete()
current_phase = get_current_phase(workouts)
current_week = get_current_week_number(workouts)
todays = get_todays_workouts(workouts)
phases = get_phase_dates(workouts)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="countdown-box">
        <div class="countdown-number">{dtrace}</div>
        <div class="countdown-label">Days to {RACE_NAME}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">Week {current_week}</div>
        <div class="metric-label">of 30-Week Plan</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    phase_short = current_phase.split("+")[0].strip() if "+" in current_phase else current_phase
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="font-size:1.4rem">{phase_short}</div>
        <div class="metric-label">Current Phase</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    completed = len([w for w in workouts if w.status == "completed"])
    total = len([w for w in workouts if w.date <= str(date.today())])
    pct = round(completed / total * 100) if total > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct}%</div>
        <div class="metric-label">Overall Compliance</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📅 Today's Training")
if todays:
    for w in todays:
        from config import SPORT_ICONS, INTENSITY_COLORS
        icon = SPORT_ICONS.get(w.sport, "❓")
        status_class = f"status-{w.status}"
        int_color = INTENSITY_COLORS.get(w.intensity, "#636E72")

        st.markdown(f"""
        <div class="workout-card {w.sport}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-size:1.3rem">{icon}</span>
                    <strong>{w.description}</strong>
                    <span style="background:{int_color}22; color:{int_color}; padding:2px 8px; border-radius:12px; font-size:0.75rem; margin-left:8px;">{w.intensity}</span>
                </div>
                <div>
                    <span style="font-size:0.85rem; color:var(--text-secondary);">{w.planned_duration_min} min</span>
                    <span class="{status_class}" style="margin-left:12px; font-weight:600;">{w.status.upper()}</span>
                </div>
            </div>
            <div style="margin-top:8px; font-size:0.85rem; color:var(--text-secondary);">
                <em>{w.purpose}</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("🏖️ No workouts scheduled for today. Rest well!")

st.markdown("---")

st.markdown("### 🗺️ Phase Timeline")
if phases:
    timeline_html = '<div style="display:flex; gap:4px; margin-bottom:20px;">'
    total_weeks = sum(p.get("duration_weeks", 1) for p in phases)
    for p in phases:
        weeks = p.get("duration_weeks", 1)
        width_pct = max(8, (weeks / total_weeks) * 100)
        color = p.get("color", "#636E72")
        is_current = p["name"] == current_phase
        border = f"3px solid white" if is_current else "none"
        opacity = "1" if is_current else "0.6"

        timeline_html += f"""
        <div style="
            flex: {weeks};
            background: {color};
            border-radius: 8px;
            padding: 12px 8px;
            text-align: center;
            opacity: {opacity};
            border: {border};
            transition: opacity 0.3s;
        ">
            <div style="font-size:0.7rem; font-weight:600; color:white; text-transform:uppercase;">
                {p['name'].split('+')[0].strip() if '+' in p['name'] else p['name'][:12]}
            </div>
            <div style="font-size:0.65rem; color:rgba(255,255,255,0.8);">{weeks}w</div>
        </div>
        """
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

st.markdown("### 🎯 Quick Navigation")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.page_link("pages/1_Dashboard.py", label="📊 Training Dashboard", icon="📊")
with col_b:
    st.page_link("pages/2_Calendar.py", label="📅 Training Calendar", icon="📅")
with col_c:
    st.page_link("pages/3_Workout_Log.py", label="✏️ Log Workout", icon="✏️")

col_d, col_e, col_f = st.columns(3)
with col_d:
    st.page_link("pages/4_Profile.py", label="👤 Athlete Profile", icon="👤")
with col_e:
    st.page_link("pages/5_Nutrition.py", label="🍎 Nutrition", icon="🍎")
with col_f:
    st.page_link("pages/6_Race_Strategy.py", label="🏁 Race Strategy", icon="🏁")

st.markdown("---")
st.caption(f"IronPlan 70.3 | Built for {athlete.name} | {RACE_NAME} — {RACE_DATE.strftime('%B %d, %Y')}")
