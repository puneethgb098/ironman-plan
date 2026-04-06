"""App-wide configuration constants."""
from datetime import date, timedelta

RACE_NAME = "Ironman 70.3 Goa"
RACE_DATE = date(2026, 10, 25)
PLAN_START_DATE = date(2026, 3, 27)

PHASES = [
    {"name": "Swim Acquisition + Transition", "weeks": 6, "color": "#6C5CE7"},
    {"name": "Aerobic Base", "weeks": 8, "color": "#0984E3"},
    {"name": "Build", "weeks": 8, "color": "#00B894"},
    {"name": "Race-Specific", "weeks": 6, "color": "#E17055"},
    {"name": "Taper", "weeks": 2, "color": "#FDCB6E"},
]

SPORTS = ["swim", "bike", "run", "strength", "mobility", "recovery", "race", "rest"]
SPORT_COLORS = {
    "swim": "#0984E3",
    "bike": "#00B894",
    "run": "#E17055",
    "strength": "#6C5CE7",
    "mobility": "#FDCB6E",
    "recovery": "#81ECEC",
    "race": "#E84393",
    "rest": "#636E72",
}
SPORT_LABELS = {
    "swim": "SWIM",
    "bike": "BIKE",
    "run": "RUN",
    "strength": "STR",
    "mobility": "MOB",
    "recovery": "REC",
    "race": "RACE",
    "rest": "REST",
}

INTENSITY_TYPES = ["easy", "tempo", "threshold", "intervals", "long", "brick", "drill", "recovery"]
INTENSITY_COLORS = {
    "easy": "#00B894",
    "tempo": "#0984E3",
    "threshold": "#E17055",
    "intervals": "#D63031",
    "long": "#6C5CE7",
    "brick": "#E84393",
    "drill": "#FDCB6E",
    "recovery": "#81ECEC",
}

WORKOUT_STATUSES = ["planned", "completed", "skipped", "modified"]
STATUS_COLORS = {
    "planned": "#636E72",
    "completed": "#00B894",
    "skipped": "#D63031",
    "modified": "#FDCB6E",
}
STATUS_LABELS = {
    "planned": "PLANNED",
    "completed": "DONE",
    "skipped": "SKIPPED",
    "modified": "MODIFIED",
}

HR_ZONES = {
    1: {"name": "Recovery", "pct_range": (0.50, 0.60), "color": "#81ECEC"},
    2: {"name": "Aerobic", "pct_range": (0.60, 0.70), "color": "#00B894"},
    3: {"name": "Tempo", "pct_range": (0.70, 0.80), "color": "#FDCB6E"},
    4: {"name": "Threshold", "pct_range": (0.80, 0.90), "color": "#E17055"},
    5: {"name": "VO2max", "pct_range": (0.90, 1.00), "color": "#D63031"},
}

TSB_THRESHOLDS = {
    "overreaching": -30,
    "fatigued": -10,
    "balanced_high": 5,
    "fresh": 20,
    "race_ready_low": 15,
    "race_ready_high": 25,
}

CTL_TIME_CONSTANT = 42
ATL_TIME_CONSTANT = 7

DEFAULT_ATHLETE = {
    "name": "Puneeth",
    "age": 23,
    "gender": "Male",
    "height_cm": 172,
    "weight_kg": 58.0,
    "resting_hr": 65,
    "max_hr": 197,
    "smm_kg": 28.1,
    "fat_mass_kg": 4.6,
    "body_fat_pct": 7.9,
    "hm_time_min": 130,
    "five_k_time_min": 28,
    "easy_run_pace": "6:00",
    "ftp_watts": None,
    "swim_pace_100m": None,
    "goal": "Finish Ironman 70.3 Goa in 6:30-7:30",
    "race_date": str(RACE_DATE),
}

APP_TITLE = "IronPlan 70.3"
