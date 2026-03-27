"""Sidebar filter components for the training app."""
import streamlit as st
from datetime import date, timedelta
from config import SPORTS, SPORT_ICONS, WORKOUT_STATUSES, STATUS_ICONS


def render_sport_filters(key_prefix: str = "filter") -> list[str]:
    """Render sport filter checkboxes in sidebar. Returns selected sports."""
    st.sidebar.markdown("### 🏅 Sport Filter")
    selected = []
    for sport in ["swim", "bike", "run", "strength", "mobility"]:
        icon = SPORT_ICONS.get(sport, "❓")
        if st.sidebar.checkbox(f"{icon} {sport.capitalize()}", value=True, key=f"{key_prefix}_sport_{sport}"):
            selected.append(sport)
    return selected if selected else ["swim", "bike", "run", "strength", "mobility"]


def render_status_filters(key_prefix: str = "filter") -> list[str]:
    """Render status filter checkboxes in sidebar."""
    st.sidebar.markdown("### 📋 Status Filter")
    selected = []
    for status in WORKOUT_STATUSES:
        icon = STATUS_ICONS.get(status, "")
        if st.sidebar.checkbox(f"{icon} {status.capitalize()}", value=True, key=f"{key_prefix}_status_{status}"):
            selected.append(status)
    return selected if selected else WORKOUT_STATUSES


def render_date_range_filter(key_prefix: str = "filter") -> tuple[date, date]:
    """Render date range filter in sidebar."""
    st.sidebar.markdown("### 📅 Date Range")
    today = date.today()
    start = st.sidebar.date_input("From", value=today - timedelta(days=90), key=f"{key_prefix}_from")
    end = st.sidebar.date_input("To", value=today, key=f"{key_prefix}_to")
    return start, end


def render_search_box(key_prefix: str = "filter") -> str:
    """Render search input in sidebar. Returns query string."""
    return st.sidebar.text_input("🔍 Search workouts", key=f"{key_prefix}_search",
                                 placeholder="Name, tag, notes...")
