"""Workout Log — Log completed workouts, mark status, add RPE and notes."""
import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from data.store import load_workouts, update_workout, save_daily_log
from data.models import DailyLog
from config import SPORT_ICONS, INTENSITY_COLORS, STATUS_COLORS

st.set_page_config(page_title="Workout Log | IronPlan", page_icon="✏️", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# ✏️ Workout Log")

workouts = load_workouts()
today = date.today()

tab1, tab2 = st.tabs(["📝 Log Workouts", "🔋 Daily Readiness"])

with tab1:
    log_date = st.date_input("Date", value=today)
    log_str = str(log_date)
    day_workouts = [w for w in workouts if w.date == log_str]

    if not day_workouts:
        st.info(f"No workouts scheduled for {log_date.strftime('%A, %B %d')}.")
        st.markdown("---")
        st.markdown("#### Log a Custom Workout")
        with st.form("custom_workout"):
            c1, c2 = st.columns(2)
            with c1:
                custom_sport = st.selectbox("Sport", ["swim", "bike", "run", "strength", "mobility"])
                custom_dur = st.number_input("Duration (min)", min_value=0, max_value=600, value=60)
            with c2:
                custom_rpe = st.slider("RPE", 1, 10, 5)
                custom_notes = st.text_area("Notes", height=80)
            if st.form_submit_button("Log Custom Workout"):
                st.success("Custom workout logged!")
    else:
        st.markdown(f"### {log_date.strftime('%A, %B %d')} — {len(day_workouts)} session(s)")

        for w in day_workouts:
            icon = SPORT_ICONS.get(w.sport, "❓")
            int_color = INTENSITY_COLORS.get(w.intensity, "#636E72")

            st.markdown(f"""
            <div class="workout-card {w.sport}">
                <span style="font-size:1.2rem;">{icon}</span>
                <strong>{w.description}</strong>
                <span style="background:{int_color}22; color:{int_color}; padding:2px 8px; border-radius:12px; font-size:0.75rem; margin-left:8px;">{w.intensity}</span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"Details & Log — {w.description}", expanded=w.date == str(today)):
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
                            value=w.actual_duration_min or w.planned_duration_min,
                            key=f"dur_{w.id}"
                        )
                    with lc2:
                        rpe = st.slider("RPE (1-10)", 1, 10, w.rpe or 5, key=f"rpe_{w.id}")
                        actual_hr = st.number_input(
                            "Avg HR (optional)", min_value=0, max_value=220,
                            value=w.actual_hr_avg or 0, key=f"hr_{w.id}"
                        )
                    notes = st.text_area("Notes", value=w.notes, key=f"notes_{w.id}", height=60)

                    if st.form_submit_button("💾 Save", type="primary"):
                        rpe_factor = {3: 0.6, 4: 0.7, 5: 0.85, 6: 1.0, 7: 1.15, 8: 1.35, 9: 1.5, 10: 1.7}
                        actual_tss = int(actual_dur * rpe_factor.get(rpe, 1.0))

                        update_workout(w.id, {
                            "status": new_status,
                            "actual_duration_min": actual_dur,
                            "rpe": rpe,
                            "actual_hr_avg": actual_hr if actual_hr > 0 else None,
                            "notes": notes,
                            "tss_actual": actual_tss,
                        })
                        st.success(f"✅ {w.description} logged as {new_status.upper()}!")
                        st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Recent Activity")
    recent_start = today - timedelta(days=7)
    recent = [w for w in workouts if str(recent_start) <= w.date <= str(today) and w.status != "planned"]
    recent.sort(key=lambda x: x.date, reverse=True)

    if recent:
        for w in recent[:10]:
            icon = SPORT_ICONS.get(w.sport, "❓")
            stat_color = STATUS_COLORS.get(w.status, "#636E72")
            dur_text = f"{w.actual_duration_min or w.planned_duration_min}min"
            rpe_text = f"RPE {w.rpe}" if w.rpe else ""
            st.markdown(f"""
            <div style="padding:8px 16px; border-left:3px solid {stat_color}; margin-bottom:4px; background:var(--bg-card); border-radius:0 8px 8px 0;">
                <span>{icon} <strong>{w.description}</strong></span>
                <span style="float:right; color:{stat_color}; font-size:0.85rem;">{w.status.upper()} · {dur_text} {rpe_text}</span>
                <div style="font-size:0.75rem; color:var(--text-muted);">{w.date}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No completed workouts in the last 7 days.")

with tab2:
    st.markdown("### 🔋 Daily Readiness Check-in")
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

        if st.form_submit_button("💾 Save Readiness Data", type="primary"):
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
            st.success(f"✅ Readiness data saved for {readiness_date.strftime('%B %d')}!")

            score = log.readiness_score()
            if score:
                if score >= 75:
                    st.markdown(f"### 💪 Readiness: **{score:.0f}/100** — You're ready to push!")
                elif score >= 50:
                    st.markdown(f"### ⚡ Readiness: **{score:.0f}/100** — Train normally")
                else:
                    st.markdown(f"### ⚠️ Readiness: **{score:.0f}/100** — Consider an easy day")
