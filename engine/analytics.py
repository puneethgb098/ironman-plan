"""Analytics engine for training load metrics.

Implements CTL/ATL/TSB calculations, compliance tracking,
readiness scoring, and trend analysis.
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


def calculate_weekly_volume(workouts: list[Workout]) -> pd.DataFrame:
    """Calculate weekly training volume by sport."""
    if not workouts:
        return pd.DataFrame()

    records = []
    for w in workouts:
        dur = w.actual_duration_min if w.actual_duration_min is not None else (
            w.planned_duration_min if w.status != "skipped" else 0
        )
        records.append({
            "date": w.date,
            "sport": w.sport,
            "duration_hr": dur / 60,
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
    return pivot


def calculate_compliance(workouts: list[Workout], up_to_date: date = None) -> dict:
    """Calculate overall and per-sport compliance rates."""
    if up_to_date is None:
        up_to_date = date.today()

    past_workouts = [w for w in workouts if w.date <= str(up_to_date)]
    if not past_workouts:
        return {"overall": 0, "swim": 0, "bike": 0, "run": 0, "strength": 0}

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

    total = easy_dur + mod_dur + hard_dur
    if total == 0:
        return {"easy": 0, "moderate": 0, "hard": 0}

    return {
        "easy": round(easy_dur / total * 100, 1),
        "moderate": round(mod_dur / total * 100, 1),
        "hard": round(hard_dur / total * 100, 1),
    }


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
