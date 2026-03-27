"""Data models for the training plan system."""
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
    status: str = "planned"
    actual_duration_min: Optional[int] = None
    actual_distance_km: Optional[float] = None
    actual_hr_avg: Optional[int] = None
    rpe: Optional[int] = None
    notes: str = ""
    tss_planned: int = 0
    tss_actual: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Workout":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


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
            scores.append(self.sleep_quality / 5 * 100)
        if self.soreness is not None:
            scores.append((6 - self.soreness) / 5 * 100)
        if self.motivation is not None:
            scores.append(self.motivation / 5 * 100)
        if not scores:
            return None
        return round(sum(scores) / len(scores), 1)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DailyLog":
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
            return 0
        return round(self.completed_sessions / self.planned_sessions * 100, 1)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["compliance_pct"] = self.compliance_pct
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "WeekSummary":
        d.pop("compliance_pct", None)
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
