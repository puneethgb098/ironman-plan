"""Training plan generation engine.

Generates the full workout calendar from athlete profile and phase definitions.
Each phase uses a weekly template populated with specific workouts.
"""
from datetime import date, timedelta
from data.models import Workout
from config import PHASES, PLAN_START_DATE
import random

WEEKLY_TEMPLATES = {
    "Swim Acquisition + Transition": {
        "target_hours": 9.5,
        "sessions": [
            {"day": 0, "sport": "swim", "type": "drill", "duration": 45, "intensity": "easy",
             "desc": "Coached swim lesson", "warmup": "Water comfort drills, floating",
             "main": "Coach-led technique: body position, kick, breathing",
             "cool": "Gentle floating", "purpose": "Water comfort and basic mechanics", "tss": 25},
            {"day": 1, "sport": "run", "type": "easy", "duration": 45, "intensity": "easy",
             "desc": "Easy Zone 2 run", "warmup": "10 min walk",
             "main": "30 min Z2 @ 6:00-6:30/km", "cool": "5 min walk",
             "purpose": "Aerobic base building", "tss": 35},
            {"day": 1, "sport": "strength", "type": "drill", "duration": 45, "intensity": "tempo",
             "desc": "Tri-specific strength (Lower + Core)", "warmup": "5 min dynamic",
             "main": "Split squat, RDL, step-ups, calf raises, core",
             "cool": "5 min stretch", "purpose": "Injury prevention, functional strength", "tss": 30},
            {"day": 2, "sport": "swim", "type": "drill", "duration": 40, "intensity": "easy",
             "desc": "Swim self-practice drills", "warmup": "Water walking, kick with board",
             "main": "Breathing practice, 6×25m freestyle attempts",
             "cool": "5 min floating", "purpose": "Reinforce coached lessons", "tss": 22},
            {"day": 3, "sport": "run", "type": "tempo", "duration": 50, "intensity": "tempo",
             "desc": "Tempo run", "warmup": "10 min easy jog",
             "main": "25 min @ 5:30-5:45/km (RPE 6-7)",
             "cool": "10 min easy + stretch", "purpose": "Lactate threshold development", "tss": 50},
            {"day": 4, "sport": "swim", "type": "drill", "duration": 40, "intensity": "easy",
             "desc": "Swim practice + technique", "warmup": "Kick with board 4×25m",
             "main": "Side breathing, 6×25m freestyle",
             "cool": "Easy floating", "purpose": "Technique development", "tss": 22},
            {"day": 4, "sport": "strength", "type": "drill", "duration": 45, "intensity": "tempo",
             "desc": "Tri-specific strength (Upper + Core)", "warmup": "5 min dynamic",
             "main": "Pull-ups, rows, push-ups, face pulls, plank",
             "cool": "5 min stretch", "purpose": "Swim-specific strength, shoulder health", "tss": 30},
            {"day": 5, "sport": "bike", "type": "long", "duration": 90, "intensity": "easy",
             "desc": "Long easy ride", "warmup": "10 min easy spin",
             "main": "70 min Z2, cadence focus 80-90 rpm",
             "cool": "10 min easy spin", "purpose": "Cycling aerobic base", "tss": 65},
            {"day": 5, "sport": "swim", "type": "easy", "duration": 30, "intensity": "easy",
             "desc": "Easy swim - water comfort", "warmup": "5 min floating",
             "main": "Relaxed kick, floating, gentle movement",
             "cool": "—", "purpose": "Water comfort accumulation", "tss": 15},
            {"day": 6, "sport": "run", "type": "long", "duration": 60, "intensity": "easy",
             "desc": "Long run", "warmup": "10 min easy",
             "main": "45 min @ 6:15-6:30/km",
             "cool": "5 min walk", "purpose": "Aerobic endurance", "tss": 50},
            {"day": 6, "sport": "mobility", "type": "recovery", "duration": 20, "intensity": "easy",
             "desc": "Foam roll + mobility", "warmup": "—",
             "main": "Hip, ankle, thoracic mobility + foam roll",
             "cool": "—", "purpose": "Recovery and flexibility", "tss": 5},
        ]
    },
    "Aerobic Base": {
        "target_hours": 12,
        "sessions": [
            {"day": 0, "sport": "swim", "type": "easy", "duration": 50, "intensity": "easy",
             "desc": "Swim endurance", "warmup": "200m easy + 4×50m drill",
             "main": "4×100m freestyle @ 2:40/100m, 20s rest",
             "cool": "100m easy", "purpose": "Build swim endurance", "tss": 35},
            {"day": 1, "sport": "run", "type": "easy", "duration": 50, "intensity": "easy",
             "desc": "Easy run", "warmup": "10 min walk/jog",
             "main": "35 min Z2 @ 6:00-6:15/km",
             "cool": "5 min walk", "purpose": "Aerobic base", "tss": 40},
            {"day": 1, "sport": "strength", "type": "drill", "duration": 45, "intensity": "tempo",
             "desc": "Tri-specific strength (Lower + Core)", "warmup": "5 min dynamic",
             "main": "Bulgarian split squat, RDL, step-ups, core",
             "cool": "5 min stretch", "purpose": "Functional strength", "tss": 30},
            {"day": 2, "sport": "swim", "type": "drill", "duration": 50, "intensity": "easy",
             "desc": "Swim drills + build", "warmup": "200m easy",
             "main": "8×50m drill (catch-up, fingertip drag) + 4×100m build",
             "cool": "100m easy", "purpose": "Technique refinement", "tss": 35},
            {"day": 2, "sport": "bike", "type": "easy", "duration": 45, "intensity": "easy",
             "desc": "Easy bike spin", "warmup": "10 min easy",
             "main": "30 min Z2, smooth pedaling",
             "cool": "5 min easy", "purpose": "Active recovery + bike volume", "tss": 30},
            {"day": 3, "sport": "run", "type": "tempo", "duration": 55, "intensity": "tempo",
             "desc": "Tempo run", "warmup": "10 min easy",
             "main": "30 min @ 5:20-5:30/km (RPE 6-7)",
             "cool": "10 min easy + stretch", "purpose": "Threshold development", "tss": 55},
            {"day": 4, "sport": "swim", "type": "easy", "duration": 50, "intensity": "easy",
             "desc": "Swim endurance", "warmup": "200m easy",
             "main": "3×200m @ 2:35/100m, 20s rest",
             "cool": "100m easy backstroke", "purpose": "Distance building", "tss": 35},
            {"day": 4, "sport": "strength", "type": "drill", "duration": 45, "intensity": "tempo",
             "desc": "Tri-specific strength (Upper + Core)", "warmup": "5 min dynamic",
             "main": "Pull-ups, rows, push-ups, face pulls, plank",
             "cool": "5 min stretch", "purpose": "Upper body + swim strength", "tss": 30},
            {"day": 5, "sport": "bike", "type": "long", "duration": 150, "intensity": "easy",
             "desc": "Long ride", "warmup": "15 min easy spin",
             "main": "120 min Z2, practice nutrition every 30 min",
             "cool": "15 min easy spin", "purpose": "Cycling endurance", "tss": 100},
            {"day": 6, "sport": "run", "type": "long", "duration": 75, "intensity": "easy",
             "desc": "Long run", "warmup": "10 min easy",
             "main": "60 min @ 6:00-6:15/km",
             "cool": "5 min walk", "purpose": "Run endurance", "tss": 60},
            {"day": 6, "sport": "swim", "type": "easy", "duration": 30, "intensity": "easy",
             "desc": "Easy recovery swim", "warmup": "—",
             "main": "30 min easy freestyle, relaxed",
             "cool": "—", "purpose": "Active recovery + volume", "tss": 18},
        ]
    },
    "Build": {
        "target_hours": 13,
        "sessions": [
            {"day": 0, "sport": "swim", "type": "threshold", "duration": 60, "intensity": "threshold",
             "desc": "Swim threshold sets", "warmup": "200m easy + 4×50m drill",
             "main": "6×150m @ 2:20-2:30/100m, 20s rest",
             "cool": "200m easy backstroke", "purpose": "Swim lactate tolerance", "tss": 55},
            {"day": 1, "sport": "run", "type": "intervals", "duration": 50, "intensity": "threshold",
             "desc": "Run intervals", "warmup": "15 min easy",
             "main": "6×800m @ 4:40-4:50/km, 90s jog rest",
             "cool": "10 min easy", "purpose": "VO2max stimulus", "tss": 60},
            {"day": 1, "sport": "strength", "type": "drill", "duration": 45, "intensity": "tempo",
             "desc": "Strength maintenance (Lower)", "warmup": "5 min dynamic",
             "main": "Split squat, RDL, step-ups, core",
             "cool": "5 min stretch", "purpose": "Maintenance strength", "tss": 25},
            {"day": 2, "sport": "swim", "type": "easy", "duration": 55, "intensity": "easy",
             "desc": "Swim endurance", "warmup": "400m easy",
             "main": "3×400m @ 2:30-2:40/100m, 30s rest",
             "cool": "200m easy", "purpose": "Continuous swim endurance", "tss": 45},
            {"day": 2, "sport": "bike", "type": "tempo", "duration": 60, "intensity": "tempo",
             "desc": "Bike tempo intervals", "warmup": "15 min easy",
             "main": "3×8 min @ RPE 6-7, 4 min easy between",
             "cool": "10 min easy", "purpose": "Cycling threshold", "tss": 55},
            {"day": 3, "sport": "run", "type": "easy", "duration": 45, "intensity": "easy",
             "desc": "Easy recovery run", "warmup": "5 min walk",
             "main": "35 min Z2 @ 6:15-6:30/km",
             "cool": "5 min walk", "purpose": "Recovery + volume", "tss": 30},
            {"day": 4, "sport": "swim", "type": "tempo", "duration": 55, "intensity": "tempo",
             "desc": "Race-pace swim", "warmup": "300m easy",
             "main": "8×100m @ race pace (2:25-2:35/100m), 15s rest",
             "cool": "200m easy", "purpose": "Race-pace familiarity", "tss": 45},
            {"day": 4, "sport": "strength", "type": "drill", "duration": 40, "intensity": "easy",
             "desc": "Strength maintenance (Upper)", "warmup": "5 min dynamic",
             "main": "Pull-ups, rows, face pulls, plank (lighter loads)",
             "cool": "5 min stretch", "purpose": "Maintenance + mobility", "tss": 20},
            {"day": 5, "sport": "bike", "type": "brick", "duration": 110, "intensity": "tempo",
             "desc": "Brick: Bike → Run", "warmup": "10 min easy spin",
             "main": "70 min ride, last 20 min @ race effort → T2 → 30 min run",
             "cool": "—", "purpose": "Multi-sport fatigue adaptation", "tss": 100},
            {"day": 6, "sport": "run", "type": "long", "duration": 80, "intensity": "easy",
             "desc": "Long run w/ fueling", "warmup": "10 min easy",
             "main": "65 min @ 6:00-6:15/km, practice gels",
             "cool": "5 min walk", "purpose": "Endurance + nutrition rehearsal", "tss": 65},
            {"day": 6, "sport": "swim", "type": "easy", "duration": 30, "intensity": "easy",
             "desc": "Easy recovery swim", "warmup": "—",
             "main": "30 min easy freestyle",
             "cool": "—", "purpose": "Active recovery", "tss": 18},
        ]
    },
    "Race-Specific": {
        "target_hours": 13,
        "sessions": [
            {"day": 0, "sport": "swim", "type": "tempo", "duration": 55, "intensity": "tempo",
             "desc": "Race-pace swim sets", "warmup": "300m easy + drills",
             "main": "3×600m @ race pace, 30s rest",
             "cool": "200m easy", "purpose": "Race-pace endurance", "tss": 50},
            {"day": 1, "sport": "run", "type": "tempo", "duration": 55, "intensity": "tempo",
             "desc": "Race-pace tempo run", "warmup": "10 min easy",
             "main": "35 min @ 6:00-6:15/km (race effort)",
             "cool": "10 min easy", "purpose": "Race-pace familiarity", "tss": 55},
            {"day": 1, "sport": "strength", "type": "easy", "duration": 35, "intensity": "easy",
             "desc": "Light strength maintenance", "warmup": "5 min dynamic",
             "main": "Bodyweight exercises, core, mobility",
             "cool": "5 min stretch", "purpose": "Maintenance only", "tss": 15},
            {"day": 2, "sport": "bike", "type": "tempo", "duration": 70, "intensity": "tempo",
             "desc": "Bike race-pace intervals", "warmup": "15 min easy",
             "main": "40 min @ race effort with nutrition practice",
             "cool": "15 min easy", "purpose": "Race simulation", "tss": 65},
            {"day": 2, "sport": "swim", "type": "easy", "duration": 40, "intensity": "easy",
             "desc": "Easy swim + sighting drills", "warmup": "200m easy",
             "main": "8×100m with head-up sighting every 8 strokes",
             "cool": "100m easy", "purpose": "Open-water preparation", "tss": 30},
            {"day": 3, "sport": "run", "type": "easy", "duration": 40, "intensity": "easy",
             "desc": "Easy recovery run", "warmup": "5 min walk",
             "main": "30 min Z2 easy",
             "cool": "5 min walk", "purpose": "Recovery", "tss": 25},
            {"day": 4, "sport": "swim", "type": "easy", "duration": 50, "intensity": "easy",
             "desc": "Swim open-water simulation", "warmup": "200m easy",
             "main": "1900m continuous at race pace",
             "cool": "100m easy", "purpose": "Race distance confidence", "tss": 45},
            {"day": 5, "sport": "bike", "type": "brick", "duration": 270, "intensity": "tempo",
             "desc": "Race simulation brick", "warmup": "15 min easy spin",
             "main": "90 km ride @ race pace → T2 → 15-18 km run @ race effort",
             "cool": "—", "purpose": "Full race simulation with nutrition", "tss": 200},
            {"day": 6, "sport": "mobility", "type": "recovery", "duration": 30, "intensity": "easy",
             "desc": "Recovery + mobility", "warmup": "—",
             "main": "Foam roll, stretching, hip/ankle mobility",
             "cool": "—", "purpose": "Recovery from race simulation", "tss": 5},
            {"day": 6, "sport": "swim", "type": "easy", "duration": 30, "intensity": "easy",
             "desc": "Easy recovery swim", "warmup": "—",
             "main": "30 min easy, relaxed",
             "cool": "—", "purpose": "Active recovery", "tss": 15},
        ]
    },
    "Taper": {
        "target_hours": 7,
        "sessions": [
            {"day": 0, "sport": "swim", "type": "easy", "duration": 30, "intensity": "easy",
             "desc": "Short race-pace intervals", "warmup": "200m easy",
             "main": "4×100m @ race pace, 30s rest",
             "cool": "100m easy", "purpose": "Maintain feel for water", "tss": 20},
            {"day": 1, "sport": "run", "type": "easy", "duration": 35, "intensity": "easy",
             "desc": "Easy run w/ strides", "warmup": "10 min easy",
             "main": "15 min easy + 4×30s strides",
             "cool": "5 min walk", "purpose": "Maintain leg turnover", "tss": 25},
            {"day": 2, "sport": "bike", "type": "easy", "duration": 45, "intensity": "easy",
             "desc": "Easy spin w/ openers", "warmup": "15 min easy",
             "main": "20 min easy + 3×2 min race effort",
             "cool": "10 min easy", "purpose": "Maintain cycling feel", "tss": 30},
            {"day": 3, "sport": "swim", "type": "easy", "duration": 25, "intensity": "easy",
             "desc": "Easy swim", "warmup": "100m easy",
             "main": "400m relaxed freestyle",
             "cool": "—", "purpose": "Water comfort maintenance", "tss": 15},
            {"day": 4, "sport": "run", "type": "easy", "duration": 25, "intensity": "easy",
             "desc": "Short easy run", "warmup": "5 min walk",
             "main": "15 min easy jog",
             "cool": "5 min walk", "purpose": "Keep legs loose", "tss": 15},
            {"day": 5, "sport": "mobility", "type": "recovery", "duration": 20, "intensity": "easy",
             "desc": "Full body mobility", "warmup": "—",
             "main": "Foam roll, stretching, relaxation",
             "cool": "—", "purpose": "Recovery + mental prep", "tss": 5},
            {"day": 6, "sport": "mobility", "type": "recovery", "duration": 15, "intensity": "easy",
             "desc": "Light walk + visualization", "warmup": "—",
             "main": "20 min walk, race visualization",
             "cool": "—", "purpose": "Pre-race rest", "tss": 3},
        ]
    },
}


def generate_plan(start_date: date = PLAN_START_DATE) -> list[Workout]:
    """Generate the full training plan as a list of Workout objects."""
    workouts = []
    current_date = start_date
    week_number = 1

    for phase_info in PHASES:
        phase_name = phase_info["name"]
        phase_weeks = phase_info["weeks"]
        template = WEEKLY_TEMPLATES.get(phase_name, WEEKLY_TEMPLATES["Aerobic Base"])

        for w in range(phase_weeks):
            is_deload = (w + 1) % 4 == 0 and phase_name != "Taper"
            week_start = current_date

            for session in template["sessions"]:
                session_date = week_start + timedelta(days=session["day"])
                planned_dur = session["duration"]
                planned_tss = session["tss"]

                if is_deload:
                    planned_dur = int(planned_dur * 0.6)
                    planned_tss = int(planned_tss * 0.5)

                progression_factor = 1.0 + (w / phase_weeks) * 0.15
                if not is_deload:
                    planned_dur = int(planned_dur * min(progression_factor, 1.15))
                    planned_tss = int(planned_tss * min(progression_factor, 1.15))

                workout = Workout(
                    date=str(session_date),
                    sport=session["sport"],
                    workout_type=session["type"],
                    planned_duration_min=planned_dur,
                    intensity=session["intensity"],
                    description=session["desc"],
                    warmup=session["warmup"],
                    main_set=session["main"],
                    cooldown=session["cool"],
                    purpose=session["purpose"],
                    phase=phase_name,
                    week_number=week_number,
                    is_deload=is_deload,
                    tss_planned=planned_tss,
                )
                workouts.append(workout)

            current_date += timedelta(weeks=1)
            week_number += 1

    return workouts


def generate_sample_completion_data(workouts: list[Workout], up_to_date: date) -> list[Workout]:
    """Add simulated completion data for past workouts (for demo purposes)."""
    random.seed(42)
    for w in workouts:
        w_date = date.fromisoformat(w.date)
        if w_date <= up_to_date:
            roll = random.random()
            if roll < 0.80:
                w.status = "completed"
                w.actual_duration_min = int(w.planned_duration_min * random.uniform(0.85, 1.1))
                w.rpe = random.randint(4, 8)
                w.tss_actual = int(w.tss_planned * random.uniform(0.8, 1.15))
                if w.sport == "run":
                    w.actual_hr_avg = random.randint(135, 165)
                elif w.sport == "bike":
                    w.actual_hr_avg = random.randint(130, 155)
            elif roll < 0.90:
                w.status = "modified"
                w.actual_duration_min = int(w.planned_duration_min * random.uniform(0.5, 0.8))
                w.rpe = random.randint(3, 6)
                w.tss_actual = int(w.tss_planned * random.uniform(0.5, 0.8))
                w.notes = "Modified due to fatigue/time constraint"
            else:
                w.status = "skipped"
                w.notes = "Skipped"
    return workouts
