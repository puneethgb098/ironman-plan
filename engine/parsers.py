"""Upload parsing engine for workout files.

Supports CSV, TCX, JSON, manual entry, and structured text paste.
FIT file support requires optional `fitparse` dependency.
"""
import csv
import json
import io
import re
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Optional
from data.models import Workout, WorkoutUpload
import uuid


def parse_csv(file_content: str | bytes, filename: str = "upload.csv") -> dict:
    """Parse a CSV file into workout data.

    Auto-detects common column names for duration, distance, HR, power, etc.
    Returns a dict with parsed metrics and list of warnings.
    """
    warnings = []
    metrics = {}

    if isinstance(file_content, bytes):
        file_content = file_content.decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(file_content))
    rows = list(reader)
    if not rows:
        return {"metrics": {}, "warnings": ["CSV file is empty"], "workouts": []}

    columns = [c.lower().strip() for c in reader.fieldnames] if reader.fieldnames else []

    col_map = _detect_csv_columns(columns)
    if not col_map:
        warnings.append("Could not auto-detect column mapping. Using best-effort parsing.")

    workouts = []
    for i, row in enumerate(rows):
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        try:
            w_data = _parse_csv_row(row_lower, col_map, i)
            if w_data:
                workouts.append(w_data)
        except Exception as e:
            warnings.append(f"Row {i+1}: {str(e)}")

    metrics["total_rows"] = len(rows)
    metrics["parsed_workouts"] = len(workouts)
    metrics["columns_detected"] = col_map

    return {"metrics": metrics, "warnings": warnings, "workouts": workouts}


def _detect_csv_columns(columns: list[str]) -> dict:
    """Auto-detect column names from headers."""
    mapping = {}
    patterns = {
        "date": ["date", "workout_date", "day", "timestamp"],
        "sport": ["sport", "activity", "type", "activity_type", "workout_type"],
        "duration": ["duration", "duration_min", "time", "elapsed_time", "moving_time", "duration_minutes"],
        "distance": ["distance", "distance_km", "dist", "distance_mi"],
        "hr_avg": ["hr", "avg_hr", "heart_rate", "hr_avg", "average_heart_rate"],
        "power_avg": ["power", "avg_power", "power_avg", "average_power", "watts"],
        "cadence": ["cadence", "avg_cadence", "cadence_avg"],
        "tss": ["tss", "training_stress", "stress_score"],
        "description": ["description", "title", "name", "workout_name", "workout"],
        "elevation": ["elevation", "elevation_gain", "ascent", "total_ascent"],
        "rpe": ["rpe", "perceived_exertion", "effort"],
        "notes": ["notes", "comment", "comments"],
        "calories": ["calories", "kcal", "cal"],
        "pace": ["pace", "avg_pace"],
        "intensity": ["intensity", "zone", "effort_level"],
    }

    for field, possible_names in patterns.items():
        for col in columns:
            if col in possible_names:
                mapping[field] = col
                break

    return mapping


def _parse_csv_row(row: dict, col_map: dict, row_idx: int) -> Optional[dict]:
    """Parse a single CSV row into workout data."""
    workout = {
        "id": str(uuid.uuid4())[:8],
        "status": "completed",
    }

    # Date
    date_col = col_map.get("date")
    if date_col and date_col in row and row[date_col]:
        try:
            parsed = _parse_date(row[date_col])
            workout["date"] = str(parsed)
        except ValueError:
            workout["date"] = str(date.today())
    else:
        workout["date"] = str(date.today())

    # Sport
    sport_col = col_map.get("sport")
    if sport_col and sport_col in row:
        workout["sport"] = _normalize_sport(row[sport_col])
    else:
        workout["sport"] = "run"

    # Description
    desc_col = col_map.get("description")
    if desc_col and desc_col in row:
        workout["description"] = row[desc_col]
    else:
        workout["description"] = f"Uploaded {workout['sport']} workout"

    # Duration
    dur_col = col_map.get("duration")
    if dur_col and dur_col in row and row[dur_col]:
        workout["actual_duration_min"] = _parse_duration(row[dur_col])
        workout["planned_duration_min"] = workout["actual_duration_min"]
    else:
        workout["planned_duration_min"] = 0
        workout["actual_duration_min"] = 0

    # Distance
    dist_col = col_map.get("distance")
    if dist_col and dist_col in row and row[dist_col]:
        try:
            workout["actual_distance_km"] = round(float(row[dist_col]), 2)
            workout["planned_distance_km"] = workout["actual_distance_km"]
        except ValueError:
            pass

    # HR
    hr_col = col_map.get("hr_avg")
    if hr_col and hr_col in row and row[hr_col]:
        try:
            workout["actual_hr_avg"] = int(float(row[hr_col]))
        except ValueError:
            pass

    # Power
    power_col = col_map.get("power_avg")
    if power_col and power_col in row and row[power_col]:
        try:
            workout["avg_power_watts"] = int(float(row[power_col]))
        except ValueError:
            pass

    # TSS
    tss_col = col_map.get("tss")
    if tss_col and tss_col in row and row[tss_col]:
        try:
            workout["tss_actual"] = int(float(row[tss_col]))
            workout["tss_planned"] = workout["tss_actual"]
        except ValueError:
            pass
    elif workout.get("actual_duration_min"):
        workout["tss_planned"] = int(workout["actual_duration_min"] * 0.8)
        workout["tss_actual"] = workout["tss_planned"]

    # RPE
    rpe_col = col_map.get("rpe")
    if rpe_col and rpe_col in row and row[rpe_col]:
        try:
            workout["rpe"] = min(10, max(1, int(float(row[rpe_col]))))
        except ValueError:
            pass

    # Elevation
    elev_col = col_map.get("elevation")
    if elev_col and elev_col in row and row[elev_col]:
        try:
            workout["elevation_m"] = round(float(row[elev_col]), 1)
        except ValueError:
            pass

    # Notes
    notes_col = col_map.get("notes")
    if notes_col and notes_col in row:
        workout["notes"] = row[notes_col]

    # Intensity
    int_col = col_map.get("intensity")
    if int_col and int_col in row:
        workout["intensity"] = _normalize_intensity(row[int_col])
    else:
        workout["intensity"] = "easy"

    return workout


def parse_tcx(file_content: str | bytes, filename: str = "upload.tcx") -> dict:
    """Parse a TCX (Training Center XML) file."""
    warnings = []
    workouts = []

    if isinstance(file_content, bytes):
        file_content = file_content.decode("utf-8", errors="replace")

    try:
        root = ET.fromstring(file_content)
    except ET.ParseError as e:
        return {"metrics": {}, "warnings": [f"XML parse error: {e}"], "workouts": []}

    ns = {"tcx": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}

    activities = root.findall(".//tcx:Activity", ns)
    if not activities:
        # Try without namespace
        activities = root.findall(".//Activity")

    for activity in activities:
        w_data = {"id": str(uuid.uuid4())[:8], "status": "completed"}

        # Sport
        sport_attr = activity.get("Sport", "Other")
        w_data["sport"] = _normalize_sport(sport_attr)

        # Date from first lap
        laps = activity.findall("tcx:Lap", ns) or activity.findall("Lap")
        total_seconds = 0
        total_distance_m = 0
        hr_values = []
        total_calories = 0

        for lap in laps:
            total_time_el = lap.find("tcx:TotalTimeSeconds", ns) or lap.find("TotalTimeSeconds")
            if total_time_el is not None and total_time_el.text:
                total_seconds += float(total_time_el.text)

            dist_el = lap.find("tcx:DistanceMeters", ns) or lap.find("DistanceMeters")
            if dist_el is not None and dist_el.text:
                total_distance_m += float(dist_el.text)

            hr_el = lap.find("tcx:AverageHeartRateBpm/tcx:Value", ns) or lap.find("AverageHeartRateBpm/Value")
            if hr_el is not None and hr_el.text:
                hr_values.append(int(float(hr_el.text)))

            cal_el = lap.find("tcx:Calories", ns) or lap.find("Calories")
            if cal_el is not None and cal_el.text:
                total_calories += int(float(cal_el.text))

        start_time = laps[0].get("StartTime") if laps else None
        if start_time:
            try:
                dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                w_data["date"] = str(dt.date())
            except ValueError:
                w_data["date"] = str(date.today())
        else:
            w_data["date"] = str(date.today())

        w_data["actual_duration_min"] = int(total_seconds / 60) if total_seconds else 0
        w_data["planned_duration_min"] = w_data["actual_duration_min"]
        w_data["actual_distance_km"] = round(total_distance_m / 1000, 2) if total_distance_m else None
        w_data["actual_hr_avg"] = int(sum(hr_values) / len(hr_values)) if hr_values else None
        w_data["description"] = f"Imported {w_data['sport']} from TCX"
        w_data["intensity"] = "easy"
        w_data["tss_planned"] = int(w_data["actual_duration_min"] * 0.8)
        w_data["tss_actual"] = w_data["tss_planned"]

        workouts.append(w_data)
        if not w_data["actual_duration_min"]:
            warnings.append("Could not parse duration from TCX")

    return {
        "metrics": {"activities_found": len(workouts)},
        "warnings": warnings,
        "workouts": workouts,
    }


def parse_json_workout(file_content: str | bytes, filename: str = "upload.json") -> dict:
    """Parse a JSON workout file."""
    warnings = []

    if isinstance(file_content, bytes):
        file_content = file_content.decode("utf-8", errors="replace")

    try:
        data = json.loads(file_content)
    except json.JSONDecodeError as e:
        return {"metrics": {}, "warnings": [f"JSON parse error: {e}"], "workouts": []}

    workouts = []
    items = data if isinstance(data, list) else [data]

    for item in items:
        if not isinstance(item, dict):
            warnings.append("Non-dict item skipped")
            continue

        w_data = {"id": str(uuid.uuid4())[:8], "status": "completed"}
        w_data.update({k: v for k, v in item.items() if k in Workout.__dataclass_fields__})
        if "id" not in item:
            w_data["id"] = str(uuid.uuid4())[:8]
        if "date" not in w_data or not w_data["date"]:
            w_data["date"] = str(date.today())
        workouts.append(w_data)

    return {
        "metrics": {"items_parsed": len(workouts)},
        "warnings": warnings,
        "workouts": workouts,
    }


def parse_structured_text(text: str) -> dict:
    """Parse structured workout text like '3x800m @4:40 rest 90s'."""
    warnings = []
    workouts = []

    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if not lines:
        return {"metrics": {}, "warnings": ["Empty text"], "workouts": []}

    w_data = {
        "id": str(uuid.uuid4())[:8],
        "status": "planned",
        "date": str(date.today()),
        "sport": "run",
        "description": lines[0][:80],
        "main_set": "\n".join(lines),
        "intensity": "easy",
        "planned_duration_min": 60,
        "tss_planned": 50,
    }

    # Try to detect sport
    text_lower = text.lower()
    if any(w in text_lower for w in ["swim", "pool", "freestyle", "backstroke", "breast"]):
        w_data["sport"] = "swim"
    elif any(w in text_lower for w in ["bike", "ride", "cycling", "spin", "watts", "ftp"]):
        w_data["sport"] = "bike"
    elif any(w in text_lower for w in ["run", "jog", "tempo", "pace/km", "/km", "mile"]):
        w_data["sport"] = "run"

    # Try to detect intensity
    if any(w in text_lower for w in ["interval", "repeat", "vo2", "speed"]):
        w_data["intensity"] = "intervals"
    elif any(w in text_lower for w in ["tempo", "threshold", "lt"]):
        w_data["intensity"] = "tempo"
    elif any(w in text_lower for w in ["easy", "recovery", "z2"]):
        w_data["intensity"] = "easy"
    elif any(w in text_lower for w in ["long"]):
        w_data["intensity"] = "long"

    # Try to extract duration
    dur_match = re.search(r"(\d+)\s*(?:min|minutes)", text_lower)
    if dur_match:
        w_data["planned_duration_min"] = int(dur_match.group(1))

    workouts.append(w_data)

    return {
        "metrics": {"lines_parsed": len(lines)},
        "warnings": warnings,
        "workouts": workouts,
    }


def parse_uploaded_file(file_content: bytes, filename: str) -> dict:
    """Route file to appropriate parser based on extension."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "csv":
        return parse_csv(file_content, filename)
    elif ext == "tcx":
        return parse_tcx(file_content, filename)
    elif ext == "json":
        return parse_json_workout(file_content, filename)
    elif ext == "fit":
        return _parse_fit_file(file_content, filename)
    else:
        return {
            "metrics": {},
            "warnings": [f"Unsupported file format: .{ext}"],
            "workouts": [],
        }


def _parse_fit_file(file_content: bytes, filename: str) -> dict:
    """Parse a FIT file. Requires optional fitparse dependency."""
    try:
        from fitparse import FitFile
    except ImportError:
        return {
            "metrics": {},
            "warnings": [
                "FIT file parsing requires the 'fitparse' package. "
                "Install with: pip install fitparse"
            ],
            "workouts": [],
        }

    try:
        fitfile = FitFile(io.BytesIO(file_content))
        workouts = []
        for record in fitfile.get_messages("session"):
            w_data = {"id": str(uuid.uuid4())[:8], "status": "completed"}
            fields = {f.name: f.value for f in record.fields}

            if "sport" in fields:
                w_data["sport"] = _normalize_sport(str(fields["sport"]))
            if "total_elapsed_time" in fields:
                w_data["actual_duration_min"] = int(fields["total_elapsed_time"] / 60)
                w_data["planned_duration_min"] = w_data["actual_duration_min"]
            if "total_distance" in fields:
                w_data["actual_distance_km"] = round(fields["total_distance"] / 1000, 2)
            if "avg_heart_rate" in fields:
                w_data["actual_hr_avg"] = int(fields["avg_heart_rate"])
            if "avg_power" in fields:
                w_data["avg_power_watts"] = int(fields["avg_power"])
            if "avg_cadence" in fields:
                w_data["avg_cadence"] = int(fields["avg_cadence"])
            if "total_ascent" in fields:
                w_data["elevation_m"] = float(fields["total_ascent"])
            if "start_time" in fields:
                w_data["date"] = str(fields["start_time"].date())
            else:
                w_data["date"] = str(date.today())

            w_data["description"] = f"Imported {w_data.get('sport', 'workout')} from FIT"
            w_data["intensity"] = "easy"
            dur = w_data.get("actual_duration_min", 0)
            w_data["tss_planned"] = int(dur * 0.8)
            w_data["tss_actual"] = w_data["tss_planned"]

            workouts.append(w_data)

        return {
            "metrics": {"sessions_found": len(workouts)},
            "warnings": [],
            "workouts": workouts,
        }
    except Exception as e:
        return {
            "metrics": {},
            "warnings": [f"FIT parse error: {str(e)}"],
            "workouts": [],
        }


# --- Helper functions ---

def _parse_date(value: str) -> date:
    """Try multiple date formats."""
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y", "%B %d, %Y"]:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {value}")


def _parse_duration(value: str) -> int:
    """Parse duration from various formats (minutes, h:mm, h:mm:ss)."""
    value = value.strip()
    # h:mm:ss
    match = re.match(r"(\d+):(\d{2}):(\d{2})", value)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2)) + (1 if int(match.group(3)) > 30 else 0)
    # h:mm or mm:ss
    match = re.match(r"(\d+):(\d{2})", value)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return h * 60 + m if h < 24 else m  # assume h:mm if <24
    # plain number
    try:
        return int(float(value))
    except ValueError:
        return 0


def _normalize_sport(value: str) -> str:
    """Normalize sport name to our internal values."""
    v = value.lower().strip()
    mapping = {
        "swimming": "swim", "swim": "swim", "pool": "swim",
        "cycling": "bike", "bike": "bike", "biking": "bike", "riding": "bike",
        "running": "run", "run": "run", "jogging": "run",
        "weight": "strength", "strength": "strength", "gym": "strength", "weights": "strength",
        "yoga": "mobility", "mobility": "mobility", "stretch": "mobility", "stretching": "mobility",
        "recovery": "recovery", "rest": "rest",
    }
    return mapping.get(v, "run")


def _normalize_intensity(value: str) -> str:
    """Normalize intensity name."""
    v = value.lower().strip()
    mapping = {
        "easy": "easy", "low": "easy", "z1": "easy", "z2": "easy",
        "tempo": "tempo", "moderate": "tempo", "z3": "tempo",
        "threshold": "threshold", "hard": "threshold", "z4": "threshold",
        "intervals": "intervals", "sprint": "intervals", "z5": "intervals",
        "long": "long", "endurance": "long",
        "recovery": "recovery",
    }
    return mapping.get(v, "easy")
