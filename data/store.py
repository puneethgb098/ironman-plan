"""JSON-based data persistence layer.

Provides CRUD operations for workouts, athlete profiles, daily logs,
and workout uploads with search, duplicate, and reschedule support.
"""
import json
import os
import copy
import uuid
from pathlib import Path
from typing import Optional
from data.models import AthleteProfile, Workout, DailyLog, WorkoutUpload

DATA_DIR = Path(__file__).parent.parent / "app_data"
UPLOADS_DIR = DATA_DIR / "uploads"


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


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


# --- Athlete ---

def load_athlete() -> AthleteProfile:
    data = _load_json("athlete.json")
    if not data:
        return AthleteProfile()
    return AthleteProfile.from_dict(data)


def save_athlete(profile: AthleteProfile):
    _save_json("athlete.json", profile.to_dict())


# --- Workouts ---

def load_workouts() -> list[Workout]:
    data = _load_json("workouts.json")
    if not data:
        return []
    return [Workout.from_dict(w) for w in data]


def save_workouts(workouts: list[Workout]):
    _save_json("workouts.json", [w.to_dict() for w in workouts])


def update_workout(workout_id: str, updates: dict):
    """Update a workout's fields and record in edit history."""
    workouts = load_workouts()
    from datetime import datetime
    for w in workouts:
        if w.id == workout_id:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "changes": {k: getattr(w, k, None) for k in updates if hasattr(w, k)},
            }
            for key, value in updates.items():
                if hasattr(w, key):
                    setattr(w, key, value)
            w.edit_history.append(history_entry)
            w.compliance_score = w.calculate_compliance()
            break
    save_workouts(workouts)


def delete_workout(workout_id: str):
    """Delete a workout by ID."""
    workouts = load_workouts()
    workouts = [w for w in workouts if w.id != workout_id]
    save_workouts(workouts)


def duplicate_workout(workout_id: str, new_date: Optional[str] = None) -> Optional[Workout]:
    """Duplicate a workout, optionally assigning a new date."""
    workouts = load_workouts()
    source = None
    for w in workouts:
        if w.id == workout_id:
            source = w
            break
    if not source:
        return None

    new_data = source.to_dict()
    new_data["id"] = str(uuid.uuid4())[:8]
    new_data["status"] = "planned"
    new_data["actual_duration_min"] = None
    new_data["actual_distance_km"] = None
    new_data["actual_hr_avg"] = None
    new_data["rpe"] = None
    new_data["tss_actual"] = None
    new_data["compliance_score"] = None
    new_data["notes"] = ""
    new_data["comments"] = []
    new_data["edit_history"] = []
    if new_date:
        new_data["date"] = new_date

    new_workout = Workout.from_dict(new_data)
    workouts.append(new_workout)
    save_workouts(workouts)
    return new_workout


def reschedule_workout(workout_id: str, new_date: str):
    """Move a workout to a new date."""
    update_workout(workout_id, {"date": new_date})


def add_workout(workout: Workout):
    """Add a new workout to storage."""
    workouts = load_workouts()
    workouts.append(workout)
    save_workouts(workouts)


def get_workouts_for_date(dt: str) -> list[Workout]:
    return [w for w in load_workouts() if w.date == dt]


def get_workouts_for_week(start_date: str, end_date: str) -> list[Workout]:
    return [w for w in load_workouts() if start_date <= w.date <= end_date]


def get_workouts_for_range(
    start: str, end: str,
    sport_filter: Optional[list[str]] = None,
    status_filter: Optional[list[str]] = None,
) -> list[Workout]:
    """Get workouts in a date range with optional sport and status filters."""
    workouts = load_workouts()
    result = [w for w in workouts if start <= w.date <= end]
    if sport_filter:
        result = [w for w in result if w.sport in sport_filter]
    if status_filter:
        result = [w for w in result if w.status in status_filter]
    return sorted(result, key=lambda w: w.date)


def search_workouts(
    query: str,
    sport_filter: Optional[list[str]] = None,
    status_filter: Optional[list[str]] = None,
    bookmarked_only: bool = False,
) -> list[Workout]:
    """Full-text search across workout fields."""
    workouts = load_workouts()
    query_lower = query.lower().strip()

    results = []
    for w in workouts:
        if sport_filter and w.sport not in sport_filter:
            continue
        if status_filter and w.status not in status_filter:
            continue
        if bookmarked_only and not w.bookmarked:
            continue
        if query_lower:
            searchable = " ".join([
                w.description, w.sport, w.workout_type, w.intensity,
                w.purpose, w.notes, w.main_set, w.phase, w.date,
                " ".join(w.tags),
            ]).lower()
            if query_lower not in searchable:
                continue
        results.append(w)
    return results


def toggle_bookmark(workout_id: str):
    """Toggle the bookmarked state of a workout."""
    workouts = load_workouts()
    for w in workouts:
        if w.id == workout_id:
            w.bookmarked = not w.bookmarked
            break
    save_workouts(workouts)


def add_comment(workout_id: str, author: str, text: str):
    """Add a comment to a workout's comment thread."""
    from data.models import CommentEntry
    workouts = load_workouts()
    for w in workouts:
        if w.id == workout_id:
            comment = CommentEntry(author=author, text=text)
            w.comments.append(comment.to_dict())
            break
    save_workouts(workouts)


# --- Daily Logs ---

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


# --- Uploads ---

def load_uploads() -> list[WorkoutUpload]:
    data = _load_json("uploads.json")
    if not data:
        return []
    return [WorkoutUpload.from_dict(u) for u in data]


def save_upload(upload: WorkoutUpload):
    uploads = load_uploads()
    uploads.append(upload)
    _save_json("uploads.json", [u.to_dict() for u in uploads])


# --- Plan Check ---

def is_plan_generated() -> bool:
    return (DATA_DIR / "workouts.json").exists() and len(load_workouts()) > 0
