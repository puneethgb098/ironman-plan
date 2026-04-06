"""Reusable native Streamlit card components for the training UI.

All rendering uses native Streamlit components instead of raw HTML
to prevent rendering failures and ensure clean display.
"""
import streamlit as st
from config import SPORT_LABELS, SPORT_COLORS, INTENSITY_COLORS, STATUS_COLORS, STATUS_LABELS


def render_metric_card(label: str, value: str, subtitle: str = "", color: str = ""):
    """Render a metric using native st.metric."""
    st.metric(label=label, value=value, delta=subtitle if subtitle else None)


def render_workout_card(workout, clickable: bool = True, compact: bool = False):
    """Render a workout summary using native Streamlit components."""
    sport_label = SPORT_LABELS.get(workout.sport, workout.sport.upper())
    stat_label = STATUS_LABELS.get(workout.status, workout.status.upper())
    sport_color = SPORT_COLORS.get(workout.sport, "#636E72")
    stat_color = STATUS_COLORS.get(workout.status, "#636E72")

    dur = int(workout.actual_duration_min or workout.planned_duration_min or 0)
    tss = int(workout.tss_actual if workout.tss_actual is not None else (workout.tss_planned or 0))

    if compact:
        st.markdown(
            f"**[{sport_label}]** {workout.description[:40]} — "
            f"{dur}min | {stat_label}"
        )
    else:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(
                    f"**[{sport_label}] {workout.description}** "
                    f"&nbsp; `{workout.intensity}`"
                )
                if workout.purpose:
                    st.caption(workout.purpose)
            with c2:
                st.markdown(
                    f"**{dur}** min &nbsp;|&nbsp; TSS **{tss}**  \n"
                    f"**{stat_label}**"
                )


def render_insight_card(insight: dict):
    """Render a training insight using native Streamlit alert components."""
    text = insight.get("text", "")
    insight_type = insight.get("type", "info")

    if insight_type == "warning":
        st.warning(text)
    elif insight_type == "success":
        st.success(text)
    elif insight_type == "record":
        st.info(text)
    else:
        st.info(text)


def render_segment_block(segment: dict, index: int = 0):
    """Render a workout segment using native Streamlit components."""
    seg_type = segment.get("segment_type", "work")
    dur = float(segment.get("duration_min", 0))
    zone = segment.get("target_zone", "")
    repeat = int(segment.get("repeat_count", 1))
    ramp = segment.get("ramp_type", "")
    notes = segment.get("notes", "")
    name = segment.get("name", f"Segment {index + 1}")
    intensity_pct = float(segment.get("intensity_pct", 0.5))

    repeat_text = f" x{repeat}" if repeat > 1 else ""
    ramp_text = f" ({ramp})" if ramp else ""
    zone_text = f" | {zone}" if zone else ""

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{name}** — {seg_type.upper()}{repeat_text}{ramp_text}")
            if notes:
                st.caption(notes)
        with c2:
            st.markdown(f"**{dur:.0f}** min{zone_text}")
        st.progress(min(1.0, intensity_pct))
