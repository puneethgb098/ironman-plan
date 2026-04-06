"""Workout detail panel — renders the full drill-down view for a workout."""
import streamlit as st
from data.models import Workout
from data.store import update_workout, delete_workout, duplicate_workout, toggle_bookmark, add_comment
from components.cards import render_segment_block
from components.charts import create_workout_profile_chart
from config import SPORT_LABELS, SPORT_COLORS, INTENSITY_COLORS, STATUS_COLORS, STATUS_LABELS


def render_workout_detail(workout: Workout):
    """Render the full workout detail panel using native Streamlit components."""
    sport_label = SPORT_LABELS.get(workout.sport, workout.sport.upper())
    stat_label = STATUS_LABELS.get(workout.status, workout.status.upper())

    # --- Header ---
    st.subheader(f"[{sport_label}] {workout.description}")
    st.caption(
        f"{workout.date} | {workout.intensity} | "
        f"{workout.sport.capitalize()} / {workout.workout_type} | "
        f"Phase: {workout.phase} | Week {workout.week_number} | "
        f"Status: {stat_label}"
    )

    # --- Metrics Row ---
    m1, m2, m3, m4, m5 = st.columns(5)
    planned_dur = int(workout.planned_duration_min or 0)
    actual_dur = int(workout.actual_duration_min or 0)
    planned_tss = int(workout.tss_planned or 0)
    actual_tss = int(workout.tss_actual or 0)
    hr_val = int(workout.actual_hr_avg) if workout.actual_hr_avg else None
    rpe_val = int(workout.rpe) if workout.rpe else None
    comp = workout.compliance_score or workout.calculate_compliance()
    comp_text = f"{float(comp):.0f}%" if comp is not None else "N/A"

    with m1:
        delta_dur = f"Planned: {planned_dur}min" if actual_dur and actual_dur != planned_dur else None
        st.metric("Duration", f"{actual_dur or planned_dur} min", delta=delta_dur)
    with m2:
        delta_tss = f"Planned: {planned_tss}" if actual_tss and actual_tss != planned_tss else None
        st.metric("TSS", str(actual_tss or planned_tss), delta=delta_tss)
    with m3:
        st.metric("Avg HR", f"{hr_val} bpm" if hr_val else "N/A")
    with m4:
        st.metric("RPE", f"{rpe_val}/10" if rpe_val else "N/A")
    with m5:
        st.metric("Compliance", comp_text)

    # --- Workout Structure ---
    st.markdown("#### Workout Structure")
    segments = workout.segments or workout.generate_segments_from_text()

    if segments:
        for i, seg in enumerate(segments):
            render_segment_block(seg if isinstance(seg, dict) else seg.to_dict(), i)

        # Profile chart
        st.markdown("#### Workout Profile")
        fig = create_workout_profile_chart(segments)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback to text display
        if workout.warmup and workout.warmup != "—":
            st.markdown(f"**Warm-up:** {workout.warmup}")
        st.markdown(f"**Main Set:** {workout.main_set}")
        if workout.cooldown and workout.cooldown != "—":
            st.markdown(f"**Cool-down:** {workout.cooldown}")

    st.markdown(f"**Purpose:** *{workout.purpose}*")

    # --- Notes & Comments ---
    st.markdown("---")
    col_notes, col_comments = st.columns(2)

    with col_notes:
        st.markdown("#### Athlete Notes")
        new_notes = st.text_area("Notes", value=workout.notes, key=f"notes_{workout.id}", height=100,
                                 label_visibility="collapsed")
        if new_notes != workout.notes:
            if st.button("Save Notes", key=f"save_notes_{workout.id}"):
                update_workout(workout.id, {"notes": new_notes})
                st.success("Notes saved.")
                st.rerun()

    with col_comments:
        st.markdown("#### Session Comments")
        comments = workout.get_comments()
        if comments:
            for c in comments:
                with st.container(border=True):
                    st.caption(f"{c.author} | {c.timestamp[:10]}")
                    st.markdown(c.text)
        new_comment = st.text_input("Add comment", key=f"comment_{workout.id}", placeholder="Type a comment...")
        if new_comment and st.button("Post", key=f"post_{workout.id}"):
            add_comment(workout.id, "athlete", new_comment)
            st.rerun()

    # --- Coach Notes ---
    if workout.coach_notes:
        st.markdown("#### Coach Notes")
        st.info(workout.coach_notes)

    # --- Actions Row ---
    st.markdown("---")
    a1, a2, a3, a4, a5 = st.columns(5)

    with a1:
        if st.button("Mark Complete", key=f"complete_{workout.id}", type="primary",
                      disabled=workout.status == "completed"):
            update_workout(workout.id, {
                "status": "completed",
                "actual_duration_min": workout.planned_duration_min,
                "tss_actual": workout.tss_planned,
            })
            st.rerun()

    with a2:
        if st.button("Duplicate", key=f"dup_{workout.id}"):
            new_w = duplicate_workout(workout.id)
            if new_w:
                st.success(f"Duplicated. New ID: {new_w.id}")
                st.rerun()

    with a3:
        bookmark_label = "Unbookmark" if workout.bookmarked else "Bookmark"
        if st.button(bookmark_label, key=f"bm_{workout.id}"):
            toggle_bookmark(workout.id)
            st.rerun()

    with a4:
        new_date = st.date_input("Reschedule to", key=f"resch_date_{workout.id}",
                                 label_visibility="collapsed")
        if st.button("Reschedule", key=f"resch_{workout.id}"):
            from data.store import reschedule_workout
            reschedule_workout(workout.id, str(new_date))
            st.success(f"Moved to {new_date}")
            st.rerun()

    with a5:
        if st.button("Delete", key=f"del_{workout.id}"):
            delete_workout(workout.id)
            st.success("Deleted.")
            st.rerun()
