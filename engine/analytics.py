"""Analytics engine for training load metrics.

Implements CTL/ATL/TSB calculations, compliance tracking,
readiness scoring, trend analysis, ramp rate, zone distribution,
rolling averages, and intelligent training insights.
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta
from data.models import Workout, DailyLog, WeekSummary
from config import CTL_TIME_CONSTANT, ATL_TIME_CONSTANT


def calculate_daily_tss(workouts: list[Workout]) -> pd.DataFrame:
    """Calculate daily aggregate TSS from workouts."""
    if not workouts:
        return pd.DataFrame(columns=["date", "tss"])

    records = []
    for w in workouts:
        tss = w.tss_actual if w.tss_actual is not None else (w.tss_planned if w.status != "skipped" else 0)
        records.append({"date": w.date, "tss": tss})

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date")["tss"].sum().reset_index()

    if daily.empty:
        return daily

    all_dates = pd.date_range(daily["date"].min(), daily["date"].max())
    daily = daily.set_index("date").reindex(all_dates, fill_value=0).reset_index()
    daily.columns = ["date", "tss"]
    return daily


def calculate_ctl_atl_tsb(workouts: list[Workout]) -> pd.DataFrame:
    """Calculate CTL, ATL, and TSB using exponential weighted moving averages."""
    daily = calculate_daily_tss(workouts)
    if daily.empty:
        return pd.DataFrame(columns=["date", "tss", "ctl", "atl", "tsb"])

    ctl_decay = 1 - np.exp(-1 / CTL_TIME_CONSTANT)
    atl_decay = 1 - np.exp(-1 / ATL_TIME_CONSTANT)

    ctl_values = []
    atl_values = []
    ctl = 0.0
    atl = 0.0

    for _, row in daily.iterrows():
        ctl = ctl + ctl_decay * (row["tss"] - ctl)
        atl = atl + atl_decay * (row["tss"] - atl)
        ctl_values.append(round(ctl, 1))
        atl_values.append(round(atl, 1))

    daily["ctl"] = ctl_values
    daily["atl"] = atl_values
    daily["tsb"] = daily["ctl"] - daily["atl"]
    daily["tsb"] = daily["tsb"].round(1)
    return daily


def calculate_ramp_rate(workouts: list[Workout]) -> pd.DataFrame:
    """Calculate week-over-week CTL change (ramp rate).

    Ramp rate > 7 TSS/week is considered risky.
    """
    metrics = calculate_ctl_atl_tsb(workouts)
    if metrics.empty:
        return pd.DataFrame(columns=["week_start", "ctl_start", "ctl_end", "ramp_rate"])

    metrics["week"] = metrics["date"].dt.to_period("W")
    weekly_ctl = metrics.groupby("week")["ctl"].last().reset_index()
    weekly_ctl.columns = ["week", "ctl_end"]
    weekly_ctl["ctl_start"] = weekly_ctl["ctl_end"].shift(1, fill_value=0)
    weekly_ctl["ramp_rate"] = (weekly_ctl["ctl_end"] - weekly_ctl["ctl_start"]).round(1)
    weekly_ctl["week_start"] = weekly_ctl["week"].dt.start_time
    return weekly_ctl


def calculate_rolling_averages(workouts: list[Workout], window: int = 7) -> pd.DataFrame:
    """Calculate rolling averages for TSS, duration, and distance."""
    if not workouts:
        return pd.DataFrame()

    records = []
    for w in workouts:
        dur = w.actual_duration_min if w.actual_duration_min else (
            w.planned_duration_min if w.status != "skipped" else 0)
        dist = w.actual_distance_km or w.planned_distance_km or 0
        tss = w.tss_actual if w.tss_actual is not None else (w.tss_planned if w.status != "skipped" else 0)
        records.append({"date": w.date, "duration": dur, "distance": dist, "tss": tss})

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date").agg({"duration": "sum", "distance": "sum", "tss": "sum"}).reset_index()

    all_dates = pd.date_range(daily["date"].min(), daily["date"].max())
    daily = daily.set_index("date").reindex(all_dates, fill_value=0).reset_index()
    daily.columns = ["date", "duration", "distance", "tss"]

    daily[f"tss_avg_{window}d"] = daily["tss"].rolling(window, min_periods=1).mean().round(1)
    daily[f"dur_avg_{window}d"] = daily["duration"].rolling(window, min_periods=1).mean().round(1)
    return daily


def calculate_weekly_volume(workouts: list[Workout]) -> pd.DataFrame:
    """Calculate weekly training volume by sport."""
    if not workouts:
        return pd.DataFrame()

    records = []
    for w in workouts:
        dur = w.actual_duration_min if w.actual_duration_min is not None else (
            w.planned_duration_min if w.status != "skipped" else 0
        )
        tss = w.tss_actual if w.tss_actual is not None else (w.tss_planned if w.status != "skipped" else 0)
        records.append({
            "date": w.date,
            "sport": w.sport,
            "duration_hr": dur / 60,
            "tss": tss,
            "week_number": w.week_number,
            "phase": w.phase,
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df["week_start"] = df["date"].dt.to_period("W").dt.start_time

    pivot = df.pivot_table(
        index=["week_start", "week_number", "phase"],
        columns="sport",
        values="duration_hr",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for sport in ["swim", "bike", "run", "strength", "mobility"]:
        if sport not in pivot.columns:
            pivot[sport] = 0

    pivot["total_hours"] = pivot[["swim", "bike", "run", "strength", "mobility"]].sum(axis=1)

    # Add weekly TSS
    tss_pivot = df.pivot_table(
        index="week_start", values="tss", aggfunc="sum"
    ).reset_index()
    tss_pivot.columns = ["week_start", "weekly_tss"]
    pivot = pivot.merge(tss_pivot, on="week_start", how="left")
    pivot["weekly_tss"] = pivot["weekly_tss"].fillna(0)

    return pivot


def calculate_compliance(workouts: list[Workout], up_to_date: date = None) -> dict:
    """Calculate overall and per-sport compliance rates."""
    if up_to_date is None:
        up_to_date = date.today()

    past_workouts = [w for w in workouts if w.date <= str(up_to_date)]
    if not past_workouts:
        return {"overall": 0, "swim": 0, "bike": 0, "run": 0, "strength": 0, "mobility": 0}

    total = len(past_workouts)
    completed = len([w for w in past_workouts if w.status in ("completed", "modified")])
    overall = round(completed / total * 100, 1) if total > 0 else 0

    by_sport = {}
    for sport in ["swim", "bike", "run", "strength", "mobility"]:
        sport_workouts = [w for w in past_workouts if w.sport == sport]
        sport_completed = [w for w in sport_workouts if w.status in ("completed", "modified")]
        by_sport[sport] = round(len(sport_completed) / len(sport_workouts) * 100, 1) if sport_workouts else 0

    return {"overall": overall, **by_sport}


def calculate_intensity_distribution(workouts: list[Workout], up_to_date: date = None) -> dict:
    """Calculate time spent in each intensity zone."""
    if up_to_date is None:
        up_to_date = date.today()

    past = [w for w in workouts if w.date <= str(up_to_date) and w.status != "skipped"]
    if not past:
        return {"easy": 0, "moderate": 0, "hard": 0}

    easy_dur = sum(w.actual_duration_min or w.planned_duration_min
                   for w in past if w.intensity in ("easy", "recovery"))
    mod_dur = sum(w.actual_duration_min or w.planned_duration_min
                  for w in past if w.intensity in ("tempo",))
    hard_dur = sum(w.actual_duration_min or w.planned_duration_min
                   for w in past if w.intensity in ("threshold", "intervals"))
    other_dur = sum(w.actual_duration_min or w.planned_duration_min
                    for w in past if w.intensity in ("long", "brick", "drill"))

    total = easy_dur + mod_dur + hard_dur + other_dur
    if total == 0:
        return {"easy": 0, "moderate": 0, "hard": 0}

    return {
        "easy": round((easy_dur + other_dur * 0.7) / total * 100, 1),
        "moderate": round((mod_dur + other_dur * 0.3) / total * 100, 1),
        "hard": round(hard_dur / total * 100, 1),
    }


def calculate_zone_distribution_by_sport(workouts: list[Workout], up_to_date: date = None) -> dict:
    """Calculate intensity distribution per sport."""
    if up_to_date is None:
        up_to_date = date.today()

    result = {}
    for sport in ["swim", "bike", "run"]:
        sport_workouts = [w for w in workouts if w.sport == sport and w.date <= str(up_to_date) and w.status != "skipped"]
        if not sport_workouts:
            result[sport] = {"easy": 0, "moderate": 0, "hard": 0}
            continue

        easy = sum(w.actual_duration_min or w.planned_duration_min for w in sport_workouts
                   if w.intensity in ("easy", "recovery", "long", "drill"))
        mod = sum(w.actual_duration_min or w.planned_duration_min for w in sport_workouts
                  if w.intensity in ("tempo", "brick"))
        hard = sum(w.actual_duration_min or w.planned_duration_min for w in sport_workouts
                   if w.intensity in ("threshold", "intervals"))
        total = easy + mod + hard
        if total == 0:
            result[sport] = {"easy": 0, "moderate": 0, "hard": 0}
        else:
            result[sport] = {
                "easy": round(easy / total * 100, 1),
                "moderate": round(mod / total * 100, 1),
                "hard": round(hard / total * 100, 1),
            }
    return result


def calculate_readiness(daily_log: DailyLog, tsb: float = 0, rhr_baseline: int = 65) -> dict:
    """Calculate a composite readiness score from daily log and TSB."""
    scores = {}
    weights = {}

    if daily_log.sleep_quality is not None:
        scores["sleep"] = daily_log.sleep_quality / 5 * 100
        weights["sleep"] = 0.25

    if daily_log.soreness is not None:
        scores["soreness"] = (6 - daily_log.soreness) / 5 * 100
        weights["soreness"] = 0.2

    if daily_log.motivation is not None:
        scores["motivation"] = daily_log.motivation / 5 * 100
        weights["motivation"] = 0.15

    if daily_log.morning_rhr is not None:
        rhr_diff = daily_log.morning_rhr - rhr_baseline
        rhr_score = max(0, min(100, 100 - rhr_diff * 5))
        scores["rhr"] = rhr_score
        weights["rhr"] = 0.2

    tsb_score = max(0, min(100, 50 + tsb * 2))
    scores["tsb"] = tsb_score
    weights["tsb"] = 0.2

    if not scores:
        return {"overall": 50, "components": {}, "status": "unknown"}

    total_weight = sum(weights.values())
    overall = sum(scores[k] * weights[k] / total_weight for k in scores)
    overall = round(overall, 1)

    if overall >= 75:
        status = "ready"
    elif overall >= 50:
        status = "moderate"
    elif overall >= 30:
        status = "fatigued"
    else:
        status = "overtrained"

    return {"overall": overall, "components": scores, "status": status}


def get_current_phase(workouts: list[Workout], target_date: date = None) -> str:
    """Determine which training phase a given date falls in."""
    if target_date is None:
        target_date = date.today()

    target_str = str(target_date)
    matching = [w for w in workouts if w.date == target_str]
    if matching:
        return matching[0].phase

    closest = None
    min_diff = float("inf")
    for w in workouts:
        diff = abs((date.fromisoformat(w.date) - target_date).days)
        if diff < min_diff:
            min_diff = diff
            closest = w
    return closest.phase if closest else "Unknown"


def get_week_summary(workouts: list[Workout], week_num: int) -> WeekSummary:
    """Build a summary for a specific training week."""
    week_workouts = [w for w in workouts if w.week_number == week_num]
    if not week_workouts:
        return WeekSummary(week_number=week_num)

    dates = sorted([w.date for w in week_workouts])
    planned_hrs = sum(w.planned_duration_min for w in week_workouts) / 60
    actual_hrs = sum(
        (w.actual_duration_min or (w.planned_duration_min if w.status != "skipped" else 0))
        for w in week_workouts
    ) / 60

    return WeekSummary(
        week_number=week_num,
        start_date=dates[0],
        end_date=dates[-1],
        phase=week_workouts[0].phase,
        is_deload=week_workouts[0].is_deload,
        planned_hours=round(planned_hrs, 1),
        actual_hours=round(actual_hrs, 1),
        planned_sessions=len(week_workouts),
        completed_sessions=len([w for w in week_workouts if w.status in ("completed", "modified")]),
        swim_hours=round(sum((w.actual_duration_min or w.planned_duration_min) / 60
                             for w in week_workouts if w.sport == "swim" and w.status != "skipped"), 1),
        bike_hours=round(sum((w.actual_duration_min or w.planned_duration_min) / 60
                             for w in week_workouts if w.sport == "bike" and w.status != "skipped"), 1),
        run_hours=round(sum((w.actual_duration_min or w.planned_duration_min) / 60
                            for w in week_workouts if w.sport == "run" and w.status != "skipped"), 1),
        strength_hours=round(sum((w.actual_duration_min or w.planned_duration_min) / 60
                                  for w in week_workouts if w.sport == "strength" and w.status != "skipped"), 1),
        total_tss=sum(w.tss_actual or w.tss_planned for w in week_workouts if w.status != "skipped"),
    )


def detect_build_recovery_weeks(workouts: list[Workout]) -> list[dict]:
    """Classify each week as build, recovery, or normal based on load pattern."""
    weeks = sorted(set(w.week_number for w in workouts))
    results = []

    for wn in weeks:
        ww = [w for w in workouts if w.week_number == wn]
        if not ww:
            continue
        total_tss = sum(w.tss_actual or w.tss_planned for w in ww if w.status != "skipped")
        is_deload = ww[0].is_deload

        week_type = "recovery" if is_deload else "build"
        if not is_deload and wn > 1:
            prev_ww = [w for w in workouts if w.week_number == wn - 1]
            if prev_ww:
                prev_tss = sum(w.tss_actual or w.tss_planned for w in prev_ww if w.status != "skipped")
                if total_tss < prev_tss * 0.7:
                    week_type = "recovery"
                elif total_tss > prev_tss * 1.05:
                    week_type = "build"
                else:
                    week_type = "maintain"

        results.append({
            "week_number": wn,
            "type": week_type,
            "total_tss": total_tss,
            "phase": ww[0].phase,
            "is_deload": is_deload,
        })
    return results


def generate_insights(workouts: list[Workout]) -> list[dict]:
    """Generate auto-text insights about training patterns."""
    insights = []
    today = date.today()
    past = [w for w in workouts if w.date <= str(today)]
    if not past:
        return insights

    # Current week missed sessions
    week_start = today - timedelta(days=today.weekday())
    this_week = [w for w in past if str(week_start) <= w.date <= str(today)]
    missed = [w for w in this_week if w.status == "skipped"]
    if missed:
        insights.append({
            "type": "warning",
            "icon": "⚠️",
            "text": f"{len(missed)} missed session{'s' if len(missed) > 1 else ''} this week",
        })

    # Largest load week
    weeks_data = {}
    for w in past:
        if w.status != "skipped":
            tss = w.tss_actual or w.tss_planned
            weeks_data.setdefault(w.week_number, 0)
            weeks_data[w.week_number] += tss
    if weeks_data:
        max_week = max(weeks_data, key=weeks_data.get)
        insights.append({
            "type": "record",
            "icon": "🏆",
            "text": f"Highest load: Week {max_week} ({weeks_data[max_week]} TSS)",
        })

    # Longest run
    runs = [w for w in past if w.sport == "run" and w.status != "skipped"]
    if runs:
        longest = max(runs, key=lambda w: w.actual_duration_min or w.planned_duration_min)
        dur = longest.actual_duration_min or longest.planned_duration_min
        insights.append({
            "type": "record",
            "icon": "🏃",
            "text": f"Longest run: {dur} min on {longest.date}",
        })

    # Highest bike load
    bikes = [w for w in past if w.sport == "bike" and w.status != "skipped"]
    if bikes:
        highest = max(bikes, key=lambda w: w.tss_actual or w.tss_planned)
        tss = highest.tss_actual or highest.tss_planned
        insights.append({
            "type": "record",
            "icon": "🚴",
            "text": f"Highest bike load: {tss} TSS on {highest.date}",
        })

    # Compliance trend
    compliance = calculate_compliance(past, today)
    pct = compliance["overall"]
    if pct >= 85:
        insights.append({"type": "success", "icon": "✅", "text": f"Excellent compliance: {pct}%"})
    elif pct >= 70:
        insights.append({"type": "info", "icon": "📊", "text": f"Good compliance: {pct}%"})
    else:
        insights.append({"type": "warning", "icon": "⚠️", "text": f"Low compliance: {pct}% — stay consistent!"})

    # Weekly load trend (last 3 weeks)
    recent_weeks = sorted(weeks_data.keys())[-3:]
    if len(recent_weeks) >= 2:
        recent_loads = [weeks_data[w] for w in recent_weeks]
        if recent_loads[-1] > recent_loads[-2] * 1.1:
            insights.append({"type": "info", "icon": "📈", "text": "Training load is trending up"})
        elif recent_loads[-1] < recent_loads[-2] * 0.8:
            insights.append({"type": "info", "icon": "📉", "text": "Training load is decreasing (recovery?)"})

    # Ramp rate warning
    ramp_df = calculate_ramp_rate(workouts)
    if not ramp_df.empty:
        latest_ramp = ramp_df.iloc[-1]["ramp_rate"]
        if latest_ramp > 7:
            insights.append({
                "type": "warning",
                "icon": "🔥",
                "text": f"High ramp rate: {latest_ramp:.1f} TSS/week — risk of overtraining",
            })

    return insights


def calculate_weekly_metrics(workouts: list[Workout]) -> pd.DataFrame:
    """Calculate comprehensive weekly metrics."""
    if not workouts:
        return pd.DataFrame()

    records = []
    for w in workouts:
        dur = w.actual_duration_min if w.actual_duration_min else (
            w.planned_duration_min if w.status != "skipped" else 0)
        dist = w.actual_distance_km or w.planned_distance_km or 0
        tss = w.tss_actual if w.tss_actual is not None else (w.tss_planned if w.status != "skipped" else 0)
        elev = w.elevation_m or 0

        records.append({
            "date": w.date, "sport": w.sport, "duration_min": dur,
            "distance_km": dist, "tss": tss, "elevation_m": elev,
            "week_number": w.week_number, "status": w.status,
        })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df["week_start"] = df["date"].dt.to_period("W").dt.start_time

    weekly = df.groupby("week_start").agg({
        "duration_min": "sum",
        "distance_km": "sum",
        "tss": "sum",
        "elevation_m": "sum",
        "week_number": "first",
    }).reset_index()

    # Add session counts
    sessions = df.groupby("week_start").agg(
        total_sessions=("status", "count"),
        completed_sessions=("status", lambda x: sum(1 for s in x if s in ("completed", "modified"))),
    ).reset_index()

    weekly = weekly.merge(sessions, on="week_start", how="left")
    weekly["compliance_pct"] = (weekly["completed_sessions"] / weekly["total_sessions"] * 100).round(1)
    weekly["duration_hr"] = (weekly["duration_min"] / 60).round(1)

    return weekly
