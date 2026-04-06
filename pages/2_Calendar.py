"""Training Calendar — Interactive monthly/weekly views with daily completion tracking."""
import streamlit as st
from pathlib import Path
from datetime import date, timedelta
from data.store import (
    load_workouts, update_workout, delete_workout, duplicate_workout,
    save_daily_completion, get_daily_completion,
)
from data.models import DailyCompletion
from engine.calendar_engine import get_month_calendar, get_week_view, get_phase_dates
from config import SPORT_LABELS, SPORT_COLORS, STATUS_LABELS, STATUS_COLORS
from components.workout_detail import render_workout_detail
from components.cards import render_workout_card

st.set_page_config(page_title="Calendar | IronPlan", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --- Sidebar Filters ---
st.sidebar.markdown("## Filters")
sport_options = ["swim", "bike", "run", "strength", "mobility"]
selected_sports = []
for sport in sport_options:
    label = SPORT_LABELS.get(sport, sport.capitalize())
    if st.sidebar.checkbox(f"{label} ({sport})", value=True, key=f"cal_sport_{sport}"):
        selected_sports.append(sport)
if not selected_sports:
    selected_sports = sport_options

st.sidebar.markdown("---")
status_options = ["planned", "completed", "skipped", "modified"]
selected_statuses = []
for status in status_options:
    s_label = STATUS_LABELS.get(status, status.capitalize())
    if st.sidebar.checkbox(f"{s_label}", value=True, key=f"cal_status_{status}"):
        selected_statuses.append(status)
if not selected_statuses:
    selected_statuses = status_options

st.sidebar.markdown("---")
search_query = st.sidebar.text_input("Search", placeholder="Name, notes, tags...", key="cal_search")

# --- Load & Filter ---
all_workouts = load_workouts()


def filter_workouts(wlist):
    filtered = [w for w in wlist if w.sport in selected_sports and w.status in selected_statuses]
    if search_query:
        q = search_query.lower()
        filtered = [w for w in filtered if q in w.description.lower() or q in w.notes.lower()
                     or q in w.purpose.lower() or q in w.sport.lower() or any(q in t.lower() for t in w.tags)]
    return filtered


st.markdown("# Training Calendar")

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
        if st.button("Previous", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col_nav2:
        month_name = date(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")
        st.markdown(f"### {month_name}")
    with col_nav3:
        if st.button("Next", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # --- Today button ---
    if st.session_state.cal_year != today.year or st.session_state.cal_month != today.month:
        if st.button("Jump to Today", use_container_width=False):
            st.session_state.cal_year = today.year
            st.session_state.cal_month = today.month
            st.rerun()

    cal_data = get_month_calendar(all_workouts, st.session_state.cal_year, st.session_state.cal_month)

    # --- Day Headers ---
    header_cols = st.columns(7)
    for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        with header_cols[i]:
            st.markdown(f"**{day_name}**")

    # --- Calendar Grid ---
    for week_row in cal_data:
        cols = st.columns(7)
        for i, day_data in enumerate(week_row):
            with cols[i]:
                day_workouts = filter_workouts(day_data["workouts"])
                is_today = day_data["is_today"]
                is_current = day_data["is_current_month"]

                if not is_current:
                    st.caption(f"{day_data['day_num']}")
                    continue

                # Sport labels for the day
                sport_labels = [SPORT_LABELS.get(w.sport, "?") for w in day_workouts]
                total_dur = sum(int(w.planned_duration_min or 0) for w in day_workouts)
                missed = sum(1 for w in day_workouts if w.status == "skipped")

                prefix = ">> " if is_today else ""
                day_text = f"**{prefix}{day_data['day_num']}**"
                if sport_labels:
                    day_text += f"  \n{' '.join(sport_labels)}"
                if total_dur > 0:
                    day_text += f"  \n{total_dur}m"
                if missed:
                    day_text += f"  \n{missed} missed"

                st.markdown(day_text)

    # --- Day Detail Section ---
    st.markdown("---")
    st.markdown("### Day Detail")
    selected_date = st.date_input("Select a date", value=today, key="cal_selected_date")
    sel_str = str(selected_date)
    day_workouts = filter_workouts([w for w in all_workouts if w.date == sel_str])

    # --- Daily Completion Toggle ---
    st.markdown("#### Daily Completion")
    day_completion = get_daily_completion(sel_str)
    dc1, dc2 = st.columns(2)
    with dc1:
        training_done = st.checkbox(
            "Training completed",
            value=day_completion.training_done,
            key=f"dc_train_{sel_str}",
        )
    with dc2:
        nutrition_done = st.checkbox(
            "Nutrition targets met",
            value=day_completion.nutrition_done,
            key=f"dc_nut_{sel_str}",
        )

    if training_done != day_completion.training_done or nutrition_done != day_completion.nutrition_done:
        updated = DailyCompletion(
            date=sel_str,
            training_done=training_done,
            nutrition_done=nutrition_done,
            notes=day_completion.notes,
        )
        save_daily_completion(updated)
        st.success("Daily completion updated.")

    if day_workouts:
        for w in day_workouts:
            render_workout_card(w, clickable=True)
            with st.expander(f"View Details — {w.description}", expanded=False):
                render_workout_detail(w)
    else:
        d_name = selected_date.strftime("%A, %B %d")
        st.info(f"No workouts scheduled for {d_name}.")

else:  # Weekly View
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    col_w1, col_w2, col_w3 = st.columns([1, 3, 1])
    with col_w1:
        if st.button("Previous Week", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    with col_w3:
        if st.button("Next Week", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()

    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.week_offset)
    week_end = week_start + timedelta(days=6)

    with col_w2:
        st.markdown(f"### {week_start.strftime('%b %d')} — {week_end.strftime('%b %d, %Y')}")

    if st.session_state.week_offset != 0:
        if st.button("Current Week"):
            st.session_state.week_offset = 0
            st.rerun()

    week_data = get_week_view(all_workouts, week_start)
    total_week_dur = sum(d["total_duration_min"] for d in week_data)
    total_week_tss = sum(
        sum(int(w.tss_actual or w.tss_planned or 0) for w in d["workouts"]) for d in week_data
    )

    # Week summary
    ws1, ws2, ws3 = st.columns(3)
    with ws1:
        st.metric("Planned Time", f"{total_week_dur // 60}h {total_week_dur % 60}m")
    with ws2:
        st.metric("Weekly TSS", int(total_week_tss))
    with ws3:
        st.metric("Sessions", sum(len(d["workouts"]) for d in week_data))

    # --- Daily Breakdown ---
    for day in week_data:
        is_today = day["is_today"]
        day_workouts = filter_workouts(day["workouts"])
        day_str = day["date"]

        # Day header
        day_label = f"**{day['day_name']}** — {day_str}"
        if is_today:
            day_label += " (TODAY)"
        if day_workouts:
            labels = " ".join([SPORT_LABELS.get(w.sport, "") for w in day_workouts])
            day_label += f"  {labels}  ({day['total_duration_hr']}h)"

        with st.expander(day_label, expanded=is_today):
            # Daily completion checkboxes
            dc_comp = get_daily_completion(day_str)
            dcc1, dcc2 = st.columns(2)
            with dcc1:
                t_done = st.checkbox(
                    "Training done", value=dc_comp.training_done,
                    key=f"wk_dc_t_{day_str}",
                )
            with dcc2:
                n_done = st.checkbox(
                    "Nutrition done", value=dc_comp.nutrition_done,
                    key=f"wk_dc_n_{day_str}",
                )
            if t_done != dc_comp.training_done or n_done != dc_comp.nutrition_done:
                save_daily_completion(DailyCompletion(
                    date=day_str, training_done=t_done, nutrition_done=n_done,
                ))

            if day_workouts:
                for w in day_workouts:
                    render_workout_card(w, clickable=True)

                    # Quick actions row
                    qa1, qa2, qa3, qa4 = st.columns(4)
                    with qa1:
                        if w.status != "completed" and st.button("Complete", key=f"wk_comp_{w.id}",
                                                                  use_container_width=True):
                            update_workout(w.id, {
                                "status": "completed",
                                "actual_duration_min": w.planned_duration_min,
                                "tss_actual": w.tss_planned,
                            })
                            st.rerun()
                    with qa2:
                        if st.button("Detail", key=f"wk_det_{w.id}", use_container_width=True):
                            st.session_state[f"show_detail_{w.id}"] = True
                            st.rerun()
                    with qa3:
                        if st.button("Copy", key=f"wk_dup_{w.id}", use_container_width=True):
                            duplicate_workout(w.id)
                            st.success("Duplicated.")
                            st.rerun()
                    with qa4:
                        if st.button("Delete", key=f"wk_del_{w.id}", use_container_width=True):
                            delete_workout(w.id)
                            st.rerun()

                    # Show detail if toggled
                    if st.session_state.get(f"show_detail_{w.id}", False):
                        render_workout_detail(w)
                        if st.button("Close Detail", key=f"close_det_{w.id}"):
                            st.session_state[f"show_detail_{w.id}"] = False
                            st.rerun()
            else:
                st.markdown("*Rest day*")
