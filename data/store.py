"""JSON-based data persistence layer."""
import json
import os
from pathlib import Path
from typing import Optional
from data.models import AthleteProfile, Workout, DailyLog

DATA_DIR = Path(__file__).parent.parent / "app_data"


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filename: str) -> dict | list:
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {} if filename != "workouts.json" else []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(filename: str, data):
    _ensure_dir()
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_athlete() -> AthleteProfile:
    data = _load_json("athlete.json")
    if not data:
        return AthleteProfile()
    return AthleteProfile.from_dict(data)


def save_athlete(profile: AthleteProfile):
    _save_json("athlete.json", profile.to_dict())


def load_workouts() -> list[Workout]:
    data = _load_json("workouts.json")
    if not data:
        return []
    return [Workout.from_dict(w) for w in data]


def save_workouts(workouts: list[Workout]):
    _save_json("workouts.json", [w.to_dict() for w in workouts])


def load_daily_logs() -> dict[str, DailyLog]:
    data = _load_json("daily_logs.json")
    if not data:
        return {}
    return {k: DailyLog.from_dict(v) for k, v in data.items()}


def save_daily_logs(logs: dict[str, DailyLog]):
    _save_json("daily_logs.json", {k: v.to_dict() for k, v in logs.items()})


def save_daily_log(log: DailyLog):
    logs = load_daily_logs()
    logs[log.date] = log
    save_daily_logs(logs)


def update_workout(workout_id: str, updates: dict):
    workouts = load_workouts()
    for w in workouts:
        if w.id == workout_id:
            for key, value in updates.items():
                if hasattr(w, key):
                    setattr(w, key, value)
            break
    save_workouts(workouts)


def get_workouts_for_date(dt: str) -> list[Workout]:
    return [w for w in load_workouts() if w.date == dt]


def get_workouts_for_week(start_date: str, end_date: str) -> list[Workout]:
    return [w for w in load_workouts() if start_date <= w.date <= end_date]


def is_plan_generated() -> bool:
    return (DATA_DIR / "workouts.json").exists() and len(load_workouts()) > 0
