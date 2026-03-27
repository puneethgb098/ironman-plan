"""Training Calendar — Monthly/Weekly/Daily views."""
import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from data.store import load_workouts
from engine.calendar_engine import get_month_calendar, get_week_view, get_phase_dates
from config import SPORT_ICONS, SPORT_COLORS, INTENSITY_COLORS, STATUS_COLORS

st.set_page_config(page_title="Calendar | IronPlan", page_icon="📅", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# 📅 Training Calendar")

workouts = load_workouts()
today = date.today()

view_mode = st.radio("View", ["Monthly", "Weekly"], horizontal=True, label_visibility="collapsed")

if view_mode == "Monthly":
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    if "cal_year" not in st.session_state:
        st.session_state.cal_year = today.year
    if "cal_month" not in st.session_state:
        st.session_state.cal_month = today.month

    with col_nav1:
        if st.button("◀ Previous"):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()

    with col_nav2:
        month_name = date(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")
        st.markdown(f"<h3 style='text-align:center;'>{month_name}</h3>", unsafe_allow_html=True)

    with col_nav3:
        if st.button("Next ▶"):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    cal_data = get_month_calendar(workouts, st.session_state.cal_year, st.session_state.cal_month)

    header_cols = st.columns(7)
    for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        with header_cols[i]:
            st.markdown(f"<div style='text-align:center; font-weight:600; color:var(--text-secondary);'>{day_name}</div>", unsafe_allow_html=True)

    for week_row in cal_data:
        cols = st.columns(7)
        for i, day_data in enumerate(week_row):
            with cols[i]:
                if not day_data["is_current_month"]:
                    opacity = "0.3"
                elif day_data["is_today"]:
                    opacity = "1"
                else:
                    opacity = "0.8"

                border_style = "2px solid #0984E3" if day_data["is_today"] else "1px solid var(--border)"
                bg = "rgba(9,132,227,0.1)" if day_data["is_today"] else "var(--bg-card)"

                icons_html = " ".join(day_data["sport_icons"])
                workout_count = len(day_data["workouts"])

                total_dur = sum(w.planned_duration_min for w in day_data["workouts"])
                dur_text = f"{total_dur}m" if total_dur > 0 else ""

                completed = sum(1 for w in day_data["workouts"] if w.status == "completed")
                status_dots = ""
                for w in day_data["workouts"]:
                    dot_color = STATUS_COLORS.get(w.status, "#636E72")
                    status_dots += f'<span style="color:{dot_color}; font-size:0.6rem;">●</span> '

                st.markdown(f"""
                <div style="
                    background:{bg}; border:{border_style}; border-radius:8px;
                    padding:6px; min-height:75px; opacity:{opacity};
                    transition: all 0.2s ease;
                ">
                    <div style="font-size:0.8rem; font-weight:600;">{day_data['day_num']}</div>
                    <div style="font-size:1rem; margin:2px 0;">{icons_html}</div>
                    <div style="font-size:0.65rem; color:var(--text-muted);">{dur_text}</div>
                    <div>{status_dots}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Day Detail")
    selected_date = st.date_input("Select a date to view details", value=today)
    sel_str = str(selected_date)
    day_workouts = [w for w in workouts if w.date == sel_str]

    if day_workouts:
        for w in day_workouts:
            icon = SPORT_ICONS.get(w.sport, "❓")
            int_color = INTENSITY_COLORS.get(w.intensity, "#636E72")
            stat_color = STATUS_COLORS.get(w.status, "#636E72")

            with st.expander(f"{icon} {w.description} — {w.planned_duration_min}min [{w.status}]", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Sport:** {w.sport.capitalize()}")
                    st.markdown(f"**Type:** {w.workout_type}")
                    st.markdown(f"**Intensity:** {w.intensity}")
                    st.markdown(f"**Phase:** {w.phase}")
                    st.markdown(f"**Week:** {w.week_number}")
                with c2:
                    st.markdown(f"**Duration:** {w.planned_duration_min} min")
                    st.markdown(f"**TSS:** {w.tss_planned}")
                    st.markdown(f"**Status:** :{w.status}[{w.status.upper()}]" if w.status == "completed" else f"**Status:** {w.status.upper()}")
                    if w.rpe:
                        st.markdown(f"**RPE:** {w.rpe}/10")

                st.markdown("---")
                st.markdown(f"**🔥 Warm-up:** {w.warmup}")
                st.markdown(f"**💪 Main Set:** {w.main_set}")
                st.markdown(f"**❄️ Cool-down:** {w.cooldown}")
                st.markdown(f"**🎯 Purpose:** *{w.purpose}*")
                if w.notes:
                    st.markdown(f"**📝 Notes:** {w.notes}")
    else:
        st.info(f"No workouts scheduled for {selected_date.strftime('%A, %B %d')}.")

else:
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    col_w1, col_w2, col_w3 = st.columns([1, 2, 1])
    with col_w1:
        if st.button("◀ Previous Week"):
            st.session_state.week_offset -= 1
            st.rerun()
    with col_w3:
        if st.button("Next Week ▶"):
            st.session_state.week_offset += 1
            st.rerun()

    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.week_offset)
    week_end = week_start + timedelta(days=6)

    with col_w2:
        st.markdown(f"<h3 style='text-align:center;'>{week_start.strftime('%b %d')} — {week_end.strftime('%b %d, %Y')}</h3>", unsafe_allow_html=True)

    week_data = get_week_view(workouts, week_start)
    total_week_dur = sum(d["total_duration_min"] for d in week_data)

    st.markdown(f"**Week total: {total_week_dur // 60}h {total_week_dur % 60}m planned**")

    for day in week_data:
        is_today = day["is_today"]
        border = "border-left: 4px solid #0984E3;" if is_today else ""
        bg = "rgba(9,132,227,0.05)" if is_today else ""
        today_badge = " **← TODAY**" if is_today else ""

        header = f"**{day['day_name']}** — {day['date']}{today_badge}"

        if day["workouts"]:
            icons = " ".join([SPORT_ICONS.get(w.sport, "") for w in day["workouts"]])
            header += f"  {icons}  ({day['total_duration_hr']}h)"

        with st.expander(header, expanded=is_today):
            if day["workouts"]:
                for w in day["workouts"]:
                    icon = SPORT_ICONS.get(w.sport, "❓")
                    int_color = INTENSITY_COLORS.get(w.intensity, "#636E72")
                    stat_color = STATUS_COLORS.get(w.status, "#636E72")

                    st.markdown(f"""
                    <div class="workout-card {w.sport}">
                        <div style="display:flex; justify-content:space-between;">
                            <span>{icon} <strong>{w.description}</strong>
                            <span style="background:{int_color}22; color:{int_color}; padding:2px 8px; border-radius:12px; font-size:0.75rem;">{w.intensity}</span></span>
                            <span style="color:{stat_color}; font-weight:600;">{w.status.upper()} · {w.planned_duration_min}min</span>
                        </div>
                        <div style="margin-top:6px; font-size:0.85rem; color:var(--text-secondary);">{w.purpose}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("🏖️ *Rest day*")
