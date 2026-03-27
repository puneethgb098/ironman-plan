"""Workout detail panel — renders the full drill-down view for a workout."""
import streamlit as st
from data.models import Workout
from data.store import update_workout, delete_workout, duplicate_workout, toggle_bookmark, add_comment
from components.cards import render_segment_block
from components.charts import create_workout_profile_chart
from config import SPORT_ICONS, SPORT_COLORS, INTENSITY_COLORS, STATUS_COLORS, STATUS_ICONS


def render_workout_detail(workout: Workout):
    """Render the full workout detail panel."""
    icon = SPORT_ICONS.get(workout.sport, "❓")
    sport_color = SPORT_COLORS.get(workout.sport, "#636E72")
    stat_color = STATUS_COLORS.get(workout.status, "#636E72")
    stat_icon = STATUS_ICONS.get(workout.status, "")
    int_color = INTENSITY_COLORS.get(workout.intensity, "#636E72")

    # --- Header ---
    st.markdown(f"""
    <div style="border-left:4px solid {sport_color}; padding:16px 20px; background:var(--bg-card);
        border-radius:0 12px 12px 0; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-size:1.6rem;">{icon}</span>
                <span style="font-size:1.3rem; font-weight:700; margin-left:8px;">{workout.description}</span>
                {"⭐" if workout.bookmarked else ""}
            </div>
            <div>
                <span style="color:{stat_color}; font-weight:700; font-size:1rem;">
                    {stat_icon} {workout.status.upper()}
                </span>
            </div>
        </div>
        <div style="margin-top:8px; display:flex; gap:16px; font-size:0.85rem; color:var(--text-secondary);">
            <span>📅 {workout.date}</span>
            <span style="background:{int_color}22; color:{int_color}; padding:1px 10px; border-radius:12px;">
                {workout.intensity}
            </span>
            <span>{workout.sport.capitalize()} · {workout.workout_type}</span>
            <span>Phase: {workout.phase}</span>
            <span>Week {workout.week_number}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Metrics Row ---
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        planned_dur = workout.planned_duration_min
        actual_dur = workout.actual_duration_min
        st.markdown(f"""
        <div class="metric-card" style="padding:12px;">
            <div style="font-size:0.72rem; color:var(--text-muted);">DURATION</div>
            <div style="font-size:1.3rem; font-weight:700;">{actual_dur or planned_dur}min</div>
            {f'<div style="font-size:0.7rem; color:var(--text-muted);">Planned: {planned_dur}min</div>' if actual_dur else ''}
        </div>
        """, unsafe_allow_html=True)
    with m2:
        planned_tss = workout.tss_planned
        actual_tss = workout.tss_actual
        st.markdown(f"""
        <div class="metric-card" style="padding:12px;">
            <div style="font-size:0.72rem; color:var(--text-muted);">TSS</div>
            <div style="font-size:1.3rem; font-weight:700;">{actual_tss or planned_tss}</div>
            {f'<div style="font-size:0.7rem; color:var(--text-muted);">Planned: {planned_tss}</div>' if actual_tss else ''}
        </div>
        """, unsafe_allow_html=True)
    with m3:
        hr_val = workout.actual_hr_avg or "—"
        st.markdown(f"""
        <div class="metric-card" style="padding:12px;">
            <div style="font-size:0.72rem; color:var(--text-muted);">AVG HR</div>
            <div style="font-size:1.3rem; font-weight:700;">{hr_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        rpe_val = f"{workout.rpe}/10" if workout.rpe else "—"
        st.markdown(f"""
        <div class="metric-card" style="padding:12px;">
            <div style="font-size:0.72rem; color:var(--text-muted);">RPE</div>
            <div style="font-size:1.3rem; font-weight:700;">{rpe_val}</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        comp = workout.compliance_score or workout.calculate_compliance()
        comp_text = f"{comp:.0f}%" if comp is not None else "—"
        comp_color = "#00B894" if (comp or 0) >= 80 else "#FDCB6E" if (comp or 0) >= 60 else "#D63031"
        st.markdown(f"""
        <div class="metric-card" style="padding:12px;">
            <div style="font-size:0.72rem; color:var(--text-muted);">COMPLIANCE</div>
            <div style="font-size:1.3rem; font-weight:700; color:{comp_color};">{comp_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Workout Structure ---
    st.markdown("#### 📋 Workout Structure")
    segments = workout.segments or workout.generate_segments_from_text()

    if segments:
        for i, seg in enumerate(segments):
            render_segment_block(seg if isinstance(seg, dict) else seg.to_dict(), i)

        # Profile chart
        st.markdown("#### 📊 Workout Profile")
        fig = create_workout_profile_chart(segments)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback to text display
        if workout.warmup and workout.warmup != "—":
            st.markdown(f"**🔥 Warm-up:** {workout.warmup}")
        st.markdown(f"**💪 Main Set:** {workout.main_set}")
        if workout.cooldown and workout.cooldown != "—":
            st.markdown(f"**❄️ Cool-down:** {workout.cooldown}")

    st.markdown(f"**🎯 Purpose:** *{workout.purpose}*")

    # --- Notes & Comments ---
    st.markdown("---")
    col_notes, col_comments = st.columns(2)

    with col_notes:
        st.markdown("#### 📝 Athlete Notes")
        new_notes = st.text_area("Notes", value=workout.notes, key=f"notes_{workout.id}", height=100,
                                 label_visibility="collapsed")
        if new_notes != workout.notes:
            if st.button("💾 Save Notes", key=f"save_notes_{workout.id}"):
                update_workout(workout.id, {"notes": new_notes})
                st.success("Notes saved!")
                st.rerun()

    with col_comments:
        st.markdown("#### 💬 Session Comments")
        comments = workout.get_comments()
        if comments:
            for c in comments:
                st.markdown(f"""
                <div style="padding:8px 12px; margin-bottom:4px; background:var(--bg-hover); border-radius:8px;">
                    <span style="font-size:0.75rem; color:var(--text-muted);">{c.author} · {c.timestamp[:10]}</span>
                    <div style="font-size:0.85rem; margin-top:2px;">{c.text}</div>
                </div>
                """, unsafe_allow_html=True)
        new_comment = st.text_input("Add comment", key=f"comment_{workout.id}", placeholder="Type a comment...")
        if new_comment and st.button("Post", key=f"post_{workout.id}"):
            add_comment(workout.id, "athlete", new_comment)
            st.rerun()

    # --- Coach Notes ---
    if workout.coach_notes:
        st.markdown("#### 🎓 Coach Notes")
        st.info(workout.coach_notes)

    # --- Actions Row ---
    st.markdown("---")
    a1, a2, a3, a4, a5 = st.columns(5)

    with a1:
        if st.button("✅ Mark Complete", key=f"complete_{workout.id}", type="primary",
                      disabled=workout.status == "completed"):
            update_workout(workout.id, {
                "status": "completed",
                "actual_duration_min": workout.planned_duration_min,
                "tss_actual": workout.tss_planned,
            })
            st.rerun()

    with a2:
        if st.button("📋 Duplicate", key=f"dup_{workout.id}"):
            new_w = duplicate_workout(workout.id)
            if new_w:
                st.success(f"Duplicated! New ID: {new_w.id}")
                st.rerun()

    with a3:
        bookmark_label = "☆ Unbookmark" if workout.bookmarked else "⭐ Bookmark"
        if st.button(bookmark_label, key=f"bm_{workout.id}"):
            toggle_bookmark(workout.id)
            st.rerun()

    with a4:
        new_date = st.date_input("Reschedule to", key=f"resch_date_{workout.id}",
                                 label_visibility="collapsed")
        if st.button("📅 Reschedule", key=f"resch_{workout.id}"):
            from data.store import reschedule_workout
            reschedule_workout(workout.id, str(new_date))
            st.success(f"Moved to {new_date}")
            st.rerun()

    with a5:
        if st.button("🗑️ Delete", key=f"del_{workout.id}"):
            delete_workout(workout.id)
            st.success("Deleted!")
            st.rerun()
