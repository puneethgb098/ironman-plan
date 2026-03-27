"""Reusable HTML card components for the training UI."""
import streamlit as st
from config import SPORT_ICONS, SPORT_COLORS, INTENSITY_COLORS, STATUS_COLORS, STATUS_ICONS


def render_metric_card(label: str, value: str, subtitle: str = "", color: str = "", icon: str = ""):
    """Render a styled metric card."""
    gradient = f"color: {color};" if color else "background: var(--gradient-blue); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
    st.markdown(f"""
    <div class="metric-card">
        {f'<div style="font-size:1.3rem;">{icon}</div>' if icon else ''}
        <div style="font-size:2rem; font-weight:700; {gradient} line-height:1.2;">{value}</div>
        <div class="metric-label">{label}</div>
        {f'<div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_workout_card(workout, clickable: bool = True, compact: bool = False):
    """Render a workout summary card with sport color coding."""
    icon = SPORT_ICONS.get(workout.sport, "❓")
    int_color = INTENSITY_COLORS.get(workout.intensity, "#636E72")
    stat_color = STATUS_COLORS.get(workout.status, "#636E72")
    stat_icon = STATUS_ICONS.get(workout.status, "")
    sport_color = SPORT_COLORS.get(workout.sport, "#636E72")

    dur = workout.actual_duration_min or workout.planned_duration_min
    tss = workout.tss_actual if workout.tss_actual is not None else workout.tss_planned
    bookmark = "⭐" if workout.bookmarked else ""

    if compact:
        st.markdown(f"""
        <div style="padding:6px 10px; border-left:3px solid {sport_color}; margin-bottom:4px;
            background:var(--bg-card); border-radius:0 6px 6px 0; font-size:0.8rem;
            display:flex; justify-content:space-between; align-items:center;">
            <span>{icon} <strong>{workout.description[:30]}</strong></span>
            <span style="color:{stat_color};">{dur}m · {stat_icon}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="workout-card {workout.sport}" style="cursor:{'pointer' if clickable else 'default'};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-size:1.2rem;">{icon}</span>
                    <strong>{workout.description}</strong>
                    {bookmark}
                    <span style="background:{int_color}22; color:{int_color}; padding:2px 8px;
                        border-radius:12px; font-size:0.72rem; margin-left:6px;">{workout.intensity}</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.82rem; color:var(--text-secondary);">{dur}min</span>
                    <span style="font-size:0.78rem; color:var(--text-muted); margin-left:6px;">TSS {tss}</span>
                    <span style="color:{stat_color}; font-weight:600; margin-left:8px; font-size:0.8rem;">
                        {stat_icon} {workout.status.upper()}
                    </span>
                </div>
            </div>
            <div style="margin-top:6px; font-size:0.82rem; color:var(--text-secondary);">
                <em>{workout.purpose}</em>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_insight_card(insight: dict):
    """Render a training insight card."""
    type_colors = {
        "warning": "#E17055",
        "success": "#00B894",
        "info": "#0984E3",
        "record": "#6C5CE7",
    }
    bg_color = type_colors.get(insight.get("type", "info"), "#636E72")

    st.markdown(f"""
    <div style="padding:10px 14px; border-left:3px solid {bg_color}; margin-bottom:6px;
        background:var(--bg-card); border-radius:0 8px 8px 0;">
        <span style="font-size:1rem;">{insight.get('icon', '💡')}</span>
        <span style="font-size:0.85rem; color:var(--text-primary); margin-left:6px;">
            {insight.get('text', '')}
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_segment_block(segment: dict, index: int = 0):
    """Render a workout segment in the detail view."""
    seg_type = segment.get("segment_type", "work")
    type_colors = {
        "warmup": "#FDCB6E",
        "cooldown": "#81ECEC",
        "work": "#0984E3",
        "rest": "#636E72",
        "recovery": "#81ECEC",
    }
    type_icons = {
        "warmup": "🔥",
        "cooldown": "❄️",
        "work": "💪",
        "rest": "⏸️",
        "recovery": "🔄",
    }
    color = type_colors.get(seg_type, "#636E72")
    icon = type_icons.get(seg_type, "▪️")
    dur = segment.get("duration_min", 0)
    zone = segment.get("target_zone", "")
    repeat = segment.get("repeat_count", 1)
    ramp = segment.get("ramp_type", "")
    notes = segment.get("notes", "")
    name = segment.get("name", f"Segment {index + 1}")

    intensity_bar_width = int(segment.get("intensity_pct", 0.5) * 100)

    repeat_text = f" × {repeat}" if repeat > 1 else ""
    ramp_text = f" ({ramp})" if ramp else ""

    st.markdown(f"""
    <div style="padding:10px 14px; border-left:3px solid {color}; margin-bottom:6px;
        background:var(--bg-card); border-radius:0 8px 8px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span>{icon}</span>
                <strong style="font-size:0.85rem; margin-left:4px;">{name}</strong>
                <span style="font-size:0.72rem; color:var(--text-muted); margin-left:8px;">
                    {dur:.0f}min{repeat_text}{ramp_text}
                </span>
            </div>
            <div>
                {f'<span style="background:{color}22; color:{color}; padding:1px 8px; border-radius:10px; font-size:0.7rem;">{zone}</span>' if zone else ''}
            </div>
        </div>
        <div style="margin-top:6px; height:4px; background: var(--bg-hover); border-radius:2px; overflow:hidden;">
            <div style="width:{intensity_bar_width}%; height:100%; background:{color}; border-radius:2px;"></div>
        </div>
        {f'<div style="margin-top:6px; font-size:0.78rem; color:var(--text-secondary);">{notes}</div>' if notes else ''}
    </div>
    """, unsafe_allow_html=True)
