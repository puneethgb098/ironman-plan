"""Workout Log — Log completed workouts, mark status, add RPE and notes."""
import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from data.store import load_workouts, update_workout, save_daily_log, save_daily_completion, get_daily_completion
from data.models import DailyLog, DailyCompletion
from config import SPORT_LABELS, STATUS_LABELS
from components.cards import render_workout_card
from components.workout_detail import render_workout_detail

st.set_page_config(page_title="Workout Log | IronPlan", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# Workout Log")

workouts = load_workouts()
today = date.today()

tab1, tab2 = st.tabs(["Log Workouts", "Daily Readiness"])

with tab1:
    log_date = st.date_input("Date", value=today)
    log_str = str(log_date)
    day_workouts = [w for w in workouts if w.date == log_str]

    # Daily completion toggle
    st.markdown("#### Daily Completion")
    dc = get_daily_completion(log_str)
    dc1, dc2 = st.columns(2)
    with dc1:
        t_done = st.checkbox("Training completed", value=dc.training_done, key=f"log_dc_t_{log_str}")
    with dc2:
        n_done = st.checkbox("Nutrition targets met", value=dc.nutrition_done, key=f"log_dc_n_{log_str}")
    if t_done != dc.training_done or n_done != dc.nutrition_done:
        save_daily_completion(DailyCompletion(date=log_str, training_done=t_done, nutrition_done=n_done))
        st.success("Daily completion updated.")

    st.markdown("---")

    if not day_workouts:
        st.info(f"No workouts scheduled for {log_date.strftime('%A, %B %d')}.")
        st.markdown("Use the **Upload** page to add workouts, or check the **Calendar** for scheduled sessions.")
    else:
        st.markdown(f"### {log_date.strftime('%A, %B %d')} — {len(day_workouts)} session(s)")

        for w in day_workouts:
            render_workout_card(w, clickable=False)

            with st.expander(f"Log — {w.description}", expanded=w.date == str(today)):
                st.markdown(f"**Warm-up:** {w.warmup}")
                st.markdown(f"**Main Set:** {w.main_set}")
                st.markdown(f"**Cool-down:** {w.cooldown}")
                st.markdown(f"**Purpose:** *{w.purpose}*")
                st.markdown(f"**Planned:** {w.planned_duration_min} min | TSS: {w.tss_planned}")

                st.markdown("---")

                with st.form(f"log_{w.id}"):
                    st.markdown("#### Log Completion")
                    lc1, lc2 = st.columns(2)
                    with lc1:
                        new_status = st.selectbox(
                            "Status", ["planned", "completed", "modified", "skipped"],
                            index=["planned", "completed", "modified", "skipped"].index(w.status),
                            key=f"status_{w.id}"
                        )
                        actual_dur = st.number_input(
                            "Actual Duration (min)",
                            min_value=0, max_value=600,
                            value=int(w.actual_duration_min or w.planned_duration_min or 0),
                            key=f"dur_{w.id}"
                        )
                        actual_dist = st.number_input(
                            "Distance (km)",
                            min_value=0.0, max_value=300.0,
                            value=float(w.actual_distance_km or w.planned_distance_km or 0),
                            step=0.1,
                            key=f"dist_{w.id}"
                        )
                    with lc2:
                        rpe = st.slider("RPE (1-10)", 1, 10, int(w.rpe or 5), key=f"rpe_{w.id}")
                        actual_hr = st.number_input(
                            "Avg HR (optional)", min_value=0, max_value=220,
                            value=int(w.actual_hr_avg or 0), key=f"hr_{w.id}"
                        )
                        avg_power = st.number_input(
                            "Avg Power (W, optional)", min_value=0, max_value=500,
                            value=int(w.avg_power_watts or 0), key=f"power_{w.id}"
                        )
                    notes = st.text_area("Notes", value=w.notes, key=f"notes_{w.id}", height=60)

                    if st.form_submit_button("Save", type="primary"):
                        rpe_factor = {3: 0.6, 4: 0.7, 5: 0.85, 6: 1.0, 7: 1.15, 8: 1.35, 9: 1.5, 10: 1.7}
                        actual_tss = int(actual_dur * rpe_factor.get(rpe, 1.0))

                        updates = {
                            "status": new_status,
                            "actual_duration_min": actual_dur,
                            "rpe": rpe,
                            "actual_hr_avg": actual_hr if actual_hr > 0 else None,
                            "avg_power_watts": avg_power if avg_power > 0 else None,
                            "actual_distance_km": actual_dist if actual_dist > 0 else None,
                            "notes": notes,
                            "tss_actual": actual_tss,
                        }
                        update_workout(w.id, updates)
                        st.success(f"{w.description} logged as {new_status.upper()}.")
                        st.rerun()

    # Recent Activity
    st.markdown("---")
    st.markdown("### Recent Activity")
    recent_start = today - timedelta(days=7)
    recent = [w for w in workouts if str(recent_start) <= w.date <= str(today) and w.status != "planned"]
    recent.sort(key=lambda x: x.date, reverse=True)

    if recent:
        for w in recent[:10]:
            render_workout_card(w, clickable=False, compact=True)
    else:
        st.caption("No completed workouts in the last 7 days.")

with tab2:
    st.markdown("### Daily Readiness Check-in")
    st.markdown("Log your morning readiness data to track recovery trends.")

    readiness_date = st.date_input("Date", value=today, key="readiness_date")

    with st.form("readiness_form"):
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            morning_rhr = st.number_input("Morning Resting HR", min_value=40, max_value=120, value=65)
            sleep_hrs = st.number_input("Sleep Hours", min_value=0.0, max_value=14.0, value=7.5, step=0.5)
        with rc2:
            sleep_quality = st.slider("Sleep Quality (1-5)", 1, 5, 4)
            soreness = st.slider("Soreness Level (1-5)", 1, 5, 2)
        with rc3:
            motivation = st.slider("Motivation (1-5)", 1, 5, 4)
            weight = st.number_input("Weight (kg)", min_value=40.0, max_value=120.0, value=58.0, step=0.1)

        r_notes = st.text_input("Notes (optional)")

        if st.form_submit_button("Save Readiness Data", type="primary"):
            log = DailyLog(
                date=str(readiness_date),
                morning_rhr=morning_rhr,
                sleep_hours=sleep_hrs,
                sleep_quality=sleep_quality,
                soreness=soreness,
                motivation=motivation,
                weight_kg=weight,
                notes=r_notes,
            )
            save_daily_log(log)
            st.success(f"Readiness data saved for {readiness_date.strftime('%B %d')}.")

            score = log.readiness_score()
            if score:
                if score >= 75:
                    st.markdown(f"### Readiness: **{score:.0f}/100** — You're ready to push")
                elif score >= 50:
                    st.markdown(f"### Readiness: **{score:.0f}/100** — Train normally")
                else:
                    st.markdown(f"### Readiness: **{score:.0f}/100** — Consider an easy day")
