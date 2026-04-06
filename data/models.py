"""Data models for the training plan system.

Provides dataclasses for athlete profile, workouts with structured segments,
daily readiness logging, weekly summaries, comments, file attachments,
uploads, training phases, and daily completion tracking.
"""
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional
import uuid


@dataclass
class AthleteProfile:
    name: str = "Puneeth"
    age: int = 23
    gender: str = "Male"
    height_cm: float = 172
    weight_kg: float = 58.0
    resting_hr: int = 65
    max_hr: int = 197
    smm_kg: float = 28.1
    fat_mass_kg: float = 4.6
    body_fat_pct: float = 7.9
    hm_time_min: int = 130
    five_k_time_min: int = 28
    easy_run_pace: str = "6:00"
    ftp_watts: Optional[int] = None
    swim_pace_100m: Optional[str] = None
    goal: str = "Finish Ironman 70.3 Goa in 6:30-7:30"
    race_date: str = "2026-10-25"
    daily_calories: int = 2800
    protein_target_g: int = 116
    sleep_target_hrs: float = 8.0

    def hr_zone(self, zone_num: int) -> tuple:
        from config import HR_ZONES
        pct_low, pct_high = HR_ZONES[zone_num]["pct_range"]
        low = int(self.resting_hr + (self.max_hr - self.resting_hr) * pct_low)
        high = int(self.resting_hr + (self.max_hr - self.resting_hr) * pct_high)
        return (low, high)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "AthleteProfile":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class WorkoutSegment:
    """A single segment/interval within a workout structure."""
    name: str = ""
    duration_min: float = 0
    target_zone: str = ""
    target_power_low: Optional[int] = None
    target_power_high: Optional[int] = None
    target_pace: Optional[str] = None
    target_hr_low: Optional[int] = None
    target_hr_high: Optional[int] = None
    repeat_count: int = 1
    ramp_type: str = ""  # "", "ramp-up", "ramp-down"
    intensity_pct: float = 0.5  # 0-1 for profile chart rendering
    segment_type: str = "work"  # work, rest, warmup, cooldown, recovery
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "WorkoutSegment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class CommentEntry:
    """A single comment in a workout comment thread."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    author: str = "athlete"
    text: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CommentEntry":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class FileAttachment:
    """File attached to a workout."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    filename: str = ""
    filepath: str = ""
    file_type: str = ""
    size_bytes: int = 0
    upload_date: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "FileAttachment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Workout:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date: str = ""
    sport: str = ""
    workout_type: str = ""
    planned_duration_min: int = 0
    planned_distance_km: Optional[float] = None
    intensity: str = ""
    description: str = ""
    warmup: str = ""
    main_set: str = ""
    cooldown: str = ""
    purpose: str = ""
    phase: str = ""
    week_number: int = 0
    is_deload: bool = False
    status: str = "planned"  # planned, completed, skipped, modified
    actual_duration_min: Optional[int] = None
    actual_distance_km: Optional[float] = None
    actual_hr_avg: Optional[int] = None
    rpe: Optional[int] = None
    notes: str = ""
    tss_planned: int = 0
    tss_actual: Optional[int] = None
    # Extended fields
    segments: list = field(default_factory=list)
    comments: list = field(default_factory=list)
    attachments: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    bookmarked: bool = False
    compliance_score: Optional[float] = None
    elevation_m: Optional[float] = None
    avg_power_watts: Optional[int] = None
    avg_cadence: Optional[int] = None
    coach_notes: str = ""
    edit_history: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Workout":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def get_segments(self) -> list["WorkoutSegment"]:
        """Return segments as WorkoutSegment objects."""
        return [WorkoutSegment.from_dict(s) if isinstance(s, dict) else s for s in self.segments]

    def get_comments(self) -> list["CommentEntry"]:
        """Return comments as CommentEntry objects."""
        return [CommentEntry.from_dict(c) if isinstance(c, dict) else c for c in self.comments]

    def calculate_compliance(self) -> Optional[float]:
        """Calculate compliance score (0-100) based on planned vs actual."""
        if self.status == "skipped":
            return 0.0
        if self.status == "planned":
            return None
        if self.actual_duration_min and self.planned_duration_min > 0:
            dur_ratio = min(float(self.actual_duration_min) / float(self.planned_duration_min), 1.5)
            tss_ratio = 1.0
            if self.tss_actual and self.tss_planned > 0:
                tss_ratio = min(float(self.tss_actual) / float(self.tss_planned), 1.5)
            return round(min(100.0, (dur_ratio * 0.6 + tss_ratio * 0.4) * 100.0), 1)
        return 80.0 if self.status == "completed" else 50.0

    def generate_segments_from_text(self) -> list:
        """Generate structured segments from warmup/main_set/cooldown text."""
        segments = []
        if self.warmup and self.warmup != "—":
            segments.append({
                "name": "Warm-up",
                "duration_min": max(5, self.planned_duration_min * 0.15),
                "target_zone": "Z1-Z2",
                "intensity_pct": 0.3,
                "segment_type": "warmup",
                "repeat_count": 1,
                "ramp_type": "ramp-up",
                "notes": self.warmup,
            })

        if self.main_set:
            main_dur = self.planned_duration_min * 0.7
            intensity_map = {
                "easy": 0.4, "recovery": 0.3, "tempo": 0.6,
                "threshold": 0.75, "intervals": 0.85,
                "long": 0.5, "brick": 0.65, "drill": 0.45,
            }
            base_intensity = intensity_map.get(self.intensity, 0.5)

            if self.workout_type == "intervals" or "×" in self.main_set or "x" in self.main_set.lower():
                segments.append({
                    "name": "Main Set — Intervals",
                    "duration_min": main_dur * 0.7,
                    "target_zone": "Z4-Z5" if self.intensity in ("threshold", "intervals") else "Z3",
                    "intensity_pct": base_intensity + 0.15,
                    "segment_type": "work",
                    "repeat_count": 1,
                    "ramp_type": "",
                    "notes": self.main_set,
                })
                segments.append({
                    "name": "Recovery between intervals",
                    "duration_min": main_dur * 0.3,
                    "target_zone": "Z1",
                    "intensity_pct": 0.25,
                    "segment_type": "recovery",
                    "repeat_count": 1,
                    "ramp_type": "",
                    "notes": "Active recovery between efforts",
                })
            else:
                segments.append({
                    "name": "Main Set",
                    "duration_min": main_dur,
                    "target_zone": f"Z{2 if base_intensity < 0.5 else 3 if base_intensity < 0.7 else 4}",
                    "intensity_pct": base_intensity,
                    "segment_type": "work",
                    "repeat_count": 1,
                    "ramp_type": "",
                    "notes": self.main_set,
                })

        if self.cooldown and self.cooldown != "—":
            segments.append({
                "name": "Cool-down",
                "duration_min": max(5, self.planned_duration_min * 0.15),
                "target_zone": "Z1",
                "intensity_pct": 0.2,
                "segment_type": "cooldown",
                "repeat_count": 1,
                "ramp_type": "ramp-down",
                "notes": self.cooldown,
            })

        return segments


@dataclass
class DailyLog:
    date: str = ""
    morning_rhr: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None  # 1-5
    soreness: Optional[int] = None  # 1-5
    motivation: Optional[int] = None  # 1-5
    weight_kg: Optional[float] = None
    calories_eaten: Optional[int] = None
    protein_g: Optional[int] = None
    water_liters: Optional[float] = None
    notes: str = ""

    def readiness_score(self) -> Optional[float]:
        scores = []
        if self.sleep_quality is not None:
            scores.append(float(self.sleep_quality) / 5.0 * 100.0)
        if self.soreness is not None:
            scores.append(float(6 - self.soreness) / 5.0 * 100.0)
        if self.motivation is not None:
            scores.append(float(self.motivation) / 5.0 * 100.0)
        if not scores:
            return None
        return round(sum(scores) / len(scores), 1)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DailyLog":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class DailyCompletion:
    """Tracks daily completion of training and nutrition targets."""
    date: str = ""
    training_done: bool = False
    nutrition_done: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DailyCompletion":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class WeekSummary:
    week_number: int = 0
    start_date: str = ""
    end_date: str = ""
    phase: str = ""
    is_deload: bool = False
    planned_hours: float = 0
    actual_hours: float = 0
    planned_sessions: int = 0
    completed_sessions: int = 0
    swim_hours: float = 0
    bike_hours: float = 0
    run_hours: float = 0
    strength_hours: float = 0
    avg_rhr: Optional[float] = None
    avg_sleep: Optional[float] = None
    avg_readiness: Optional[float] = None
    total_tss: float = 0

    @property
    def compliance_pct(self) -> float:
        if self.planned_sessions == 0:
            return 0.0
        return round(float(self.completed_sessions) / float(self.planned_sessions) * 100.0, 1)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["compliance_pct"] = self.compliance_pct
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "WeekSummary":
        d.pop("compliance_pct", None)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class WorkoutUpload:
    """Metadata for an uploaded workout file."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    filename: str = ""
    file_format: str = ""  # csv, fit, tcx, json, manual, text
    upload_date: str = field(default_factory=lambda: datetime.now().isoformat())
    workout_id: Optional[str] = None  # linked workout
    parsed_metrics: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    status: str = "pending"  # pending, imported, error

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "WorkoutUpload":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class TrainingPhase:
    """A training phase/block within the annual plan."""
    name: str = ""
    start_date: str = ""
    end_date: str = ""
    start_week: int = 0
    end_week: int = 0
    target_hours: float = 0
    color: str = "#636E72"
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TrainingPhase":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
