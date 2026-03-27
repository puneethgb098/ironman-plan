"""Reusable Plotly chart builders for the training dashboard.

All chart functions return Plotly Figure objects styled with the app's dark theme.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import SPORT_COLORS, TSB_THRESHOLDS, HR_ZONES


CHART_TEMPLATE = "plotly_dark"
CHART_BG = "rgba(0,0,0,0)"
CHART_MARGINS = dict(l=20, r=20, t=40, b=20)
LEGEND_STYLE = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)


def create_ctl_atl_tsb_chart(metrics_df: pd.DataFrame, height: int = 400) -> go.Figure:
    """Create the CTL/ATL/TSB performance chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=metrics_df["date"], y=metrics_df["ctl"],
        name="CTL (Fitness)", line=dict(color="#0984E3", width=3),
        fill="tozeroy", fillcolor="rgba(9,132,227,0.08)",
        hovertemplate="CTL: %{y:.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=metrics_df["date"], y=metrics_df["atl"],
        name="ATL (Fatigue)", line=dict(color="#E17055", width=2, dash="dash"),
        hovertemplate="ATL: %{y:.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=metrics_df["date"], y=metrics_df["tsb"],
        name="TSB (Form)", line=dict(color="#00B894", width=2),
        fill="tozeroy", fillcolor="rgba(0,184,148,0.05)",
        hovertemplate="TSB: %{y:.0f}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    fig.add_hline(y=TSB_THRESHOLDS["overreaching"], line_dash="dot",
                  line_color="#D63031", opacity=0.3, annotation_text="Overreach")
    fig.add_hline(y=TSB_THRESHOLDS["race_ready_low"], line_dash="dot",
                  line_color="#00B894", opacity=0.3, annotation_text="Race Ready")

    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        margin=CHART_MARGINS, legend=LEGEND_STYLE,
        xaxis_title="", yaxis_title="Training Stress",
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        hovermode="x unified",
    )
    return fig


def create_weekly_volume_chart(volume_df: pd.DataFrame, height: int = 350) -> go.Figure:
    """Create stacked bar chart of weekly volume by sport."""
    fig = go.Figure()

    for sport in ["swim", "bike", "run", "strength", "mobility"]:
        if sport in volume_df.columns:
            fig.add_trace(go.Bar(
                x=volume_df["week_number"],
                y=volume_df[sport],
                name=sport.capitalize(),
                marker_color=SPORT_COLORS.get(sport, "#636E72"),
                hovertemplate=f"{sport.capitalize()}: " + "%{y:.1f}h<extra></extra>",
            ))

    fig.update_layout(
        barmode="stack", template=CHART_TEMPLATE, height=height,
        margin=CHART_MARGINS, legend=LEGEND_STYLE,
        xaxis_title="Week", yaxis_title="Hours",
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
    )
    return fig


def create_zone_distribution_chart(dist: dict, height: int = 300) -> go.Figure:
    """Create donut chart for intensity zone distribution."""
    fig = go.Figure(go.Pie(
        labels=["Easy (Z1-2)", "Moderate (Z3)", "Hard (Z4-5)"],
        values=[dist.get("easy", 0), dist.get("moderate", 0), dist.get("hard", 0)],
        marker_colors=["#00B894", "#FDCB6E", "#D63031"],
        hole=0.55,
        textinfo="percent+label",
        textfont_size=11,
        hovertemplate="%{label}: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
    )
    return fig


def create_ramp_rate_chart(ramp_df: pd.DataFrame, height: int = 300) -> go.Figure:
    """Create ramp rate line chart with warning thresholds."""
    fig = go.Figure()

    colors = ["#D63031" if r > 7 else "#FDCB6E" if r > 5 else "#00B894"
              for r in ramp_df["ramp_rate"]]

    fig.add_trace(go.Bar(
        x=ramp_df["week_start"], y=ramp_df["ramp_rate"],
        marker_color=colors, name="Ramp Rate",
        hovertemplate="Ramp: %{y:.1f} TSS/wk<extra></extra>",
    ))

    fig.add_hline(y=7, line_dash="dash", line_color="#D63031", opacity=0.5,
                  annotation_text="Risk threshold")
    fig.add_hline(y=5, line_dash="dash", line_color="#FDCB6E", opacity=0.3)

    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        margin=CHART_MARGINS,
        xaxis_title="", yaxis_title="CTL Change / Week",
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
    )
    return fig


def create_compliance_chart(compliance: dict, height: int = 300) -> go.Figure:
    """Create horizontal bar chart for compliance by sport."""
    sports = [s for s in ["swim", "bike", "run", "strength", "mobility"] if s in compliance]
    values = [compliance[s] for s in sports]
    colors = ["#00B894" if v >= 80 else "#FDCB6E" if v >= 60 else "#D63031" for v in values]

    fig = go.Figure(go.Bar(
        y=[s.capitalize() for s in sports],
        x=values,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.0f}%" for v in values],
        textposition="auto",
        hovertemplate="%{y}: %{x:.0f}%<extra></extra>",
    ))

    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(range=[0, 105], title=""),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
    )
    return fig


def create_workout_profile_chart(segments: list, height: int = 150) -> go.Figure:
    """Create a small area chart visualizing workout interval structure."""
    if not segments:
        return go.Figure()

    x_vals = []
    y_vals = []
    colors = []
    pos = 0

    color_map = {
        "warmup": "rgba(253,203,110,0.6)",
        "cooldown": "rgba(129,236,236,0.6)",
        "work": "rgba(9,132,227,0.7)",
        "rest": "rgba(99,110,114,0.4)",
        "recovery": "rgba(129,236,236,0.5)",
    }

    for seg in segments:
        if isinstance(seg, dict):
            dur = seg.get("duration_min", 5)
            intensity = seg.get("intensity_pct", 0.5)
            seg_type = seg.get("segment_type", "work")
            repeat = seg.get("repeat_count", 1)
            ramp = seg.get("ramp_type", "")
        else:
            dur = getattr(seg, "duration_min", 5)
            intensity = getattr(seg, "intensity_pct", 0.5)
            seg_type = getattr(seg, "segment_type", "work")
            repeat = getattr(seg, "repeat_count", 1)
            ramp = getattr(seg, "ramp_type", "")

        for r in range(repeat):
            if ramp == "ramp-up":
                steps = max(3, int(dur / 2))
                for i in range(steps):
                    x_vals.append(pos + dur * i / steps)
                    y_vals.append(intensity * (i + 1) / steps)
            elif ramp == "ramp-down":
                steps = max(3, int(dur / 2))
                for i in range(steps):
                    x_vals.append(pos + dur * i / steps)
                    y_vals.append(intensity * (steps - i) / steps)
            else:
                x_vals.extend([pos, pos + dur])
                y_vals.extend([intensity, intensity])
            pos += dur

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals,
        fill="tozeroy",
        line=dict(color="#0984E3", width=2),
        fillcolor="rgba(9,132,227,0.2)",
        hoverinfo="skip",
    ))

    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        margin=dict(l=10, r=10, t=5, b=20),
        xaxis=dict(title="Duration (min)", showgrid=False),
        yaxis=dict(title="", showticklabels=False, showgrid=False, range=[0, 1.1]),
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        showlegend=False,
    )
    return fig


def create_weekly_tss_chart(volume_df: pd.DataFrame, height: int = 300) -> go.Figure:
    """Create weekly TSS bar chart."""
    if "weekly_tss" not in volume_df.columns:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=volume_df["week_number"],
        y=volume_df["weekly_tss"],
        marker_color="#6C5CE7",
        marker_line_color="#6C5CE7",
        marker_line_width=1,
        opacity=0.8,
        hovertemplate="Week %{x}: %{y:.0f} TSS<extra></extra>",
    ))

    fig.update_layout(
        template=CHART_TEMPLATE, height=height,
        margin=CHART_MARGINS,
        xaxis_title="Week", yaxis_title="TSS",
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
    )
    return fig
