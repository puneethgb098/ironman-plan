"""Calendar engine for workout views, rescheduling, and adaptation."""
from datetime import date, timedelta
from data.models import Workout
from typing import Optional
import calendar


def get_month_calendar(workouts: list[Workout], year: int, month: int) -> list[list[dict]]:
    """Build a month calendar grid with workout data.

    Returns a list of week-rows, each containing 7 day-dicts with:
    - date, day_num, is_current_month, workouts
    """
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)
    result = []

    workout_by_date = {}
    for w in workouts:
        workout_by_date.setdefault(w.date, []).append(w)

    for week in month_days:
        week_row = []
        for d in week:
            day_data = {
                "date": str(d),
                "day_num": d.day,
                "is_current_month": d.month == month,
                "is_today": d == date.today(),
                "workouts": workout_by_date.get(str(d), []),
                "sport_icons": [],
            }
            for w in day_data["workouts"]:
                from config import SPORT_LABELS
                label = SPORT_LABELS.get(w.sport, w.sport[:3].upper())
                if label not in day_data["sport_icons"]:
                    day_data["sport_icons"].append(label)
            week_row.append(day_data)
        result.append(week_row)
    return result


def get_week_view(workouts: list[Workout], week_start: date) -> list[dict]:
    """Get a daily breakdown for a specific week (Mon-Sun)."""
    days = []
    workout_by_date = {}
    for w in workouts:
        workout_by_date.setdefault(w.date, []).append(w)

    for i in range(7):
        d = week_start + timedelta(days=i)
        day_workouts = workout_by_date.get(str(d), [])
        total_duration = sum(w.planned_duration_min for w in day_workouts)
        completed = all(w.status == "completed" for w in day_workouts) if day_workouts else False

        days.append({
            "date": str(d),
            "day_name": d.strftime("%A"),
            "workouts": day_workouts,
            "total_duration_min": total_duration,
            "total_duration_hr": round(total_duration / 60, 1),
            "all_completed": completed,
            "is_today": d == date.today(),
            "is_past": d < date.today(),
        })
    return days


def get_upcoming_workouts(workouts: list[Workout], days_ahead: int = 7) -> list[Workout]:
    """Get planned workouts for the next N days."""
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    upcoming = [
        w for w in workouts
        if today <= date.fromisoformat(w.date) <= cutoff
    ]
    return sorted(upcoming, key=lambda w: w.date)


def get_todays_workouts(workouts: list[Workout]) -> list[Workout]:
    """Get workouts scheduled for today."""
    today_str = str(date.today())
    return [w for w in workouts if w.date == today_str]


def get_phase_dates(workouts: list[Workout]) -> list[dict]:
    """Extract phase start/end dates from the workout plan."""
    if not workouts:
        return []

    phases = {}
    for w in workouts:
        if w.phase not in phases:
            phases[w.phase] = {"name": w.phase, "start": w.date, "end": w.date}
        else:
            if w.date < phases[w.phase]["start"]:
                phases[w.phase]["start"] = w.date
            if w.date > phases[w.phase]["end"]:
                phases[w.phase]["end"] = w.date

    from config import PHASES
    phase_order = [p["name"] for p in PHASES]
    result = []
    for name in phase_order:
        if name in phases:
            info = phases[name]
            start = date.fromisoformat(info["start"])
            end = date.fromisoformat(info["end"])
            info["duration_weeks"] = max(1, (end - start).days // 7)
            from config import PHASES as P
            for p in P:
                if p["name"] == name:
                    info["color"] = p["color"]
                    break
            result.append(info)
    return result


def days_to_race(race_date: date) -> int:
    return (race_date - date.today()).days


def get_current_week_number(workouts: list[Workout]) -> Optional[int]:
    today_str = str(date.today())
    for w in workouts:
        if w.date == today_str:
            return w.week_number

    today = date.today()
    closest = None
    min_diff = float("inf")
    for w in workouts:
        diff = abs((date.fromisoformat(w.date) - today).days)
        if diff < min_diff:
            min_diff = diff
            closest = w
    return closest.week_number if closest else 1
