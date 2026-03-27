"""Training Calendar — Interactive monthly/weekly views with clickable workouts."""
import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from data.store import load_workouts, update_workout, delete_workout, duplicate_workout
from engine.calendar_engine import get_month_calendar, get_week_view, get_phase_dates
from config import SPORT_ICONS, SPORT_COLORS, INTENSITY_COLORS, STATUS_COLORS, STATUS_ICONS
from components.workout_detail import render_workout_detail
from components.cards import render_workout_card

st.set_page_config(page_title="Calendar | IronPlan", page_icon="📅", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.markdown("## 🏅 Filters")
sport_options = ["swim", "bike", "run", "strength", "mobility"]
selected_sports = []
for sport in sport_options:
    icon = SPORT_ICONS.get(sport, "❓")
    if st.sidebar.checkbox(f"{icon} {sport.capitalize()}", value=True, key=f"cal_sport_{sport}"):
        selected_sports.append(sport)
if not selected_sports:
    selected_sports = sport_options

st.sidebar.markdown("---")
status_options = ["planned", "completed", "skipped", "modified"]
selected_statuses = []
for status in status_options:
    s_icon = STATUS_ICONS.get(status, "")
    if st.sidebar.checkbox(f"{s_icon} {status.capitalize()}", value=True, key=f"cal_status_{status}"):
        selected_statuses.append(status)
if not selected_statuses:
    selected_statuses = status_options

st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Search", placeholder="Name, notes, tags...", key="cal_search")

# --- Load & Filter ---
all_workouts = load_workouts()


def filter_workouts(wlist):
    filtered = [w for w in wlist if w.sport in selected_sports and w.status in selected_statuses]
    if search_query:
        q = search_query.lower()
        filtered = [w for w in filtered if q in w.description.lower() or q in w.notes.lower()
                     or q in w.purpose.lower() or q in w.sport.lower() or any(q in t.lower() for t in w.tags)]
    return filtered


st.markdown("# 📅 Training Calendar")

today = date.today()
view_mode = st.radio("View", ["Monthly", "Weekly"], horizontal=True, label_visibility="collapsed")

if view_mode == "Monthly":
    # --- Month Navigation ---
    if "cal_year" not in st.session_state:
        st.session_state.cal_year = today.year
    if "cal_month" not in st.session_state:
        st.session_state.cal_month = today.month

    col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
    with col_nav1:
        if st.button("◀ Previous", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col_nav2:
        month_name = date(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")
        st.markdown(f"<h3 style='text-align:center; margin:0;'>{month_name}</h3>", unsafe_allow_html=True)
    with col_nav3:
        if st.button("Next ▶", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # --- Today button ---
    if st.session_state.cal_year != today.year or st.session_state.cal_month != today.month:
        if st.button("📍 Jump to Today", use_container_width=False):
            st.session_state.cal_year = today.year
            st.session_state.cal_month = today.month
            st.rerun()

    cal_data = get_month_calendar(all_workouts, st.session_state.cal_year, st.session_state.cal_month)

    # --- Day Headers ---
    header_cols = st.columns(7)
    for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        with header_cols[i]:
            st.markdown(f"<div style='text-align:center; font-weight:600; font-size:0.8rem; "
                        f"color:var(--text-secondary); padding:4px 0;'>{day_name}</div>",
                        unsafe_allow_html=True)

    # --- Calendar Grid ---
    for week_row in cal_data:
        cols = st.columns(7)
        for i, day_data in enumerate(week_row):
            with cols[i]:
                day_workouts = filter_workouts(day_data["workouts"])

                if not day_data["is_current_month"]:
                    opacity = "0.25"
                elif day_data["is_today"]:
                    opacity = "1"
                else:
                    opacity = "0.85"

                is_today = day_data["is_today"]
                is_past = date.fromisoformat(day_data["date"]) < today
                border_style = "2px solid #0984E3" if is_today else "1px solid var(--border)"
                bg = "rgba(9,132,227,0.12)" if is_today else "var(--bg-card)"

                # Sport color dots
                sport_dots = ""
                for w in day_workouts:
                    sc = SPORT_COLORS.get(w.sport, "#636E72")
                    st_c = STATUS_COLORS.get(w.status, "#636E72")
                    sport_dots += f'<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{sc}; margin:1px; border:1px solid {st_c};"></span>'

                total_dur = sum(w.planned_duration_min for w in day_workouts)
                dur_text = f"{total_dur}m" if total_dur > 0 else ""
                total_tss = sum((w.tss_actual or w.tss_planned) for w in day_workouts)
                tss_text = f"TSS {total_tss}" if total_tss > 0 else ""

                # Missed indicator
                missed = sum(1 for w in day_workouts if w.status == "skipped")
                missed_mark = f'<span style="color:#D63031; font-size:0.6rem;">✗{missed}</span>' if missed else ""

                day_num_style = "font-weight:700; color:#0984E3;" if is_today else "font-weight:500;"

                st.markdown(f"""
                <div style="background:{bg}; border:{border_style}; border-radius:8px;
                    padding:6px; min-height:80px; opacity:{opacity}; transition:all 0.2s ease;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.78rem; {day_num_style}">{day_data['day_num']}</span>
                        {missed_mark}
                    </div>
                    <div style="margin:3px 0;">{sport_dots}</div>
                    <div style="font-size:0.62rem; color:var(--text-muted);">{dur_text}</div>
                    <div style="font-size:0.58rem; color:var(--text-muted);">{tss_text}</div>
                </div>
                """, unsafe_allow_html=True)

    # --- Day Detail Section ---
    st.markdown("---")
    st.markdown("### 📋 Day Detail")
    selected_date = st.date_input("Select a date", value=today, key="cal_selected_date")
    sel_str = str(selected_date)
    day_workouts = filter_workouts([w for w in all_workouts if w.date == sel_str])

    if day_workouts:
        for w in day_workouts:
            render_workout_card(w, clickable=True)
            with st.expander(f"🔍 View Details — {w.description}", expanded=False):
                render_workout_detail(w)
    else:
        d_name = selected_date.strftime("%A, %B %d")
        st.info(f"🏖️ No workouts scheduled for {d_name}.")

else:  # Weekly View
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    col_w1, col_w2, col_w3 = st.columns([1, 3, 1])
    with col_w1:
        if st.button("◀ Previous Week", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    with col_w3:
        if st.button("Next Week ▶", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()

    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.week_offset)
    week_end = week_start + timedelta(days=6)

    with col_w2:
        st.markdown(f"<h3 style='text-align:center; margin:0;'>"
                    f"{week_start.strftime('%b %d')} — {week_end.strftime('%b %d, %Y')}</h3>",
                    unsafe_allow_html=True)

    if st.session_state.week_offset != 0:
        if st.button("📍 Current Week"):
            st.session_state.week_offset = 0
            st.rerun()

    week_data = get_week_view(all_workouts, week_start)
    total_week_dur = sum(d["total_duration_min"] for d in week_data)
    total_week_tss = sum(sum((w.tss_actual or w.tss_planned) for w in d["workouts"]) for d in week_data)

    # Week summary bar
    st.markdown(f"""
    <div style="display:flex; gap:20px; padding:12px 16px; background:var(--bg-card);
        border-radius:10px; margin-bottom:16px; font-size:0.85rem;">
        <span>⏱️ <strong>{total_week_dur // 60}h {total_week_dur % 60}m</strong> planned</span>
        <span>📊 <strong>{total_week_tss}</strong> TSS</span>
        <span>🏋️ <strong>{sum(len(d['workouts']) for d in week_data)}</strong> sessions</span>
    </div>
    """, unsafe_allow_html=True)

    # --- Daily Breakdown ---
    for day in week_data:
        is_today = day["is_today"]
        day_workouts = filter_workouts(day["workouts"])

        # Day header
        day_label = f"**{day['day_name']}** — {day['date']}"
        if is_today:
            day_label += " **← TODAY**"
        if day_workouts:
            icons = " ".join([SPORT_ICONS.get(w.sport, "") for w in day_workouts])
            day_label += f"  {icons}  ({day['total_duration_hr']}h)"

        with st.expander(day_label, expanded=is_today):
            if day_workouts:
                for w in day_workouts:
                    render_workout_card(w, clickable=True)

                    # Quick actions row
                    qa1, qa2, qa3, qa4 = st.columns(4)
                    with qa1:
                        if w.status != "completed" and st.button("✅ Complete", key=f"wk_comp_{w.id}",
                                                                  use_container_width=True):
                            update_workout(w.id, {
                                "status": "completed",
                                "actual_duration_min": w.planned_duration_min,
                                "tss_actual": w.tss_planned,
                            })
                            st.rerun()
                    with qa2:
                        if st.button("🔍 Detail", key=f"wk_det_{w.id}", use_container_width=True):
                            st.session_state[f"show_detail_{w.id}"] = True
                            st.rerun()
                    with qa3:
                        if st.button("📋 Copy", key=f"wk_dup_{w.id}", use_container_width=True):
                            duplicate_workout(w.id)
                            st.success("Duplicated!")
                            st.rerun()
                    with qa4:
                        if st.button("🗑️", key=f"wk_del_{w.id}", use_container_width=True):
                            delete_workout(w.id)
                            st.rerun()

                    # Show detail if toggled
                    if st.session_state.get(f"show_detail_{w.id}", False):
                        render_workout_detail(w)
                        if st.button("Close Detail", key=f"close_det_{w.id}"):
                            st.session_state[f"show_detail_{w.id}"] = False
                            st.rerun()
            else:
                st.markdown("🏖️ *Rest day*")
