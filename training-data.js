/* ═══════════════════════════════════════════════════════════════
   IRONPLAN 70.3 — Training Data Engine
   30-week periodized plan · 80/20 polarized · science-based
   ═══════════════════════════════════════════════════════════════ */

const TrainingData = (() => {

    // ── Athlete Profile ──────────────────────────────────────────
    const ATHLETE = {
        name: "Puneeth",
        age: 23,
        gender: "Male",
        heightCm: 172,
        weightKg: 58.0,
        restingHR: 65,
        maxHR: 197,
        smmKg: 28.1,
        fatMassKg: 4.6,
        bodyFatPct: 7.9,
        fiveKPB: "27:30",
        fiveKPace: "5:30",       // min/km
        cyclingRange: 20,         // km/hr avg
        swimLevel: 0,             // 0-10
        ftpWatts: null,
        swimPace100m: null,
        easyRunPace: "6:00",
        goal: "Finish Ironman 70.3 Goa in 6:30–7:30",
        dailyCalories: 2800,
        proteinTargetG: 116,
        sleepTargetHrs: 8.0,
    };

    // ── HR Zones (Karvonen method) ───────────────────────────────
    const HR_ZONES = {
        1: { name: "Recovery", pctLow: 0.50, pctHigh: 0.60, color: "#81ECEC" },
        2: { name: "Aerobic", pctLow: 0.60, pctHigh: 0.70, color: "#00B894" },
        3: { name: "Tempo", pctLow: 0.70, pctHigh: 0.80, color: "#FDCB6E" },
        4: { name: "Threshold", pctLow: 0.80, pctHigh: 0.90, color: "#E17055" },
        5: { name: "VO2max", pctLow: 0.90, pctHigh: 1.00, color: "#D63031" },
    };

    function getHRZone(zone) {
        const z = HR_ZONES[zone];
        const reserve = ATHLETE.maxHR - ATHLETE.restingHR;
        return {
            ...z,
            low: Math.round(ATHLETE.restingHR + reserve * z.pctLow),
            high: Math.round(ATHLETE.restingHR + reserve * z.pctHigh),
        };
    }

    // ── Race & Plan Config ───────────────────────────────────────
    const RACE_NAME = "Ironman 70.3 Goa";
    const RACE_DATE = new Date(2026, 9, 25); // Oct 25, 2026
    const PLAN_START = new Date(2026, 2, 27); // Mar 27, 2026

    // ── Sport & Intensity Colors ─────────────────────────────────
    const SPORT_COLORS = {
        swim: "#0984E3",
        bike: "#00B894",
        run: "#E17055",
        strength: "#6C5CE7",
        mobility: "#FDCB6E",
        recovery: "#81ECEC",
        race: "#E84393",
        rest: "#636E72",
    };

    const SPORT_ICONS = {
        swim: "🏊", bike: "🚴", run: "🏃", strength: "🏋️",
        mobility: "🧘", recovery: "💤", race: "🏁", rest: "😴",
    };

    const INTENSITY_COLORS = {
        easy: "#00B894",
        tempo: "#0984E3",
        threshold: "#E17055",
        intervals: "#D63031",
        long: "#6C5CE7",
        brick: "#E84393",
        drill: "#FDCB6E",
        recovery: "#81ECEC",
    };

    // ── Phase Definitions ────────────────────────────────────────
    const PHASES = [
        {
            name: "Swim Acquisition + Transition", weeks: 6, color: "#6C5CE7",
            desc: "Build water comfort, establish aerobic base in run/bike, introduce tri-specific strength"
        },
        {
            name: "Aerobic Base", weeks: 8, color: "#0984E3",
            desc: "80/20 polarized focus — high-volume Z2 across all three disciplines, technique refinement"
        },
        {
            name: "Build", weeks: 8, color: "#00B894",
            desc: "Introduce threshold & VO2max work, brick sessions, race-pace familiarity"
        },
        {
            name: "Race-Specific", weeks: 6, color: "#E17055",
            desc: "Race simulations, open-water prep, nutrition rehearsal, peak fitness"
        },
        {
            name: "Taper", weeks: 2, color: "#FDCB6E",
            desc: "Volume reduction, maintain intensity, race-day mental preparation"
        },
    ];

    // ── Weekly Templates ─────────────────────────────────────────
    const WEEKLY_TEMPLATES = {

        // ── PHASE 1: SWIM ACQUISITION + TRANSITION (6 weeks) ──────
        "Swim Acquisition + Transition": {
            targetHours: 9.5,
            sessions: [
                // Monday
                {
                    day: 0, sport: "swim", type: "drill", duration: 45, intensity: "easy", tss: 25,
                    desc: "Coached swim lesson",
                    warmup: "Water comfort drills, floating, wall kicks",
                    main: "Coach-led technique: body position, kick, bilateral breathing",
                    cooldown: "5 min gentle floating, relaxation",
                    purpose: "Water comfort and basic freestyle mechanics",
                    zones: "Z1-Z2", rpe: "3-4"
                },

                // Tuesday
                {
                    day: 1, sport: "run", type: "easy", duration: 45, intensity: "easy", tss: 35,
                    desc: "Easy Zone 2 run",
                    warmup: "10 min walk → easy jog",
                    main: "30 min Z2 @ 6:00-6:30/km (conversational pace)",
                    cooldown: "5 min walk + dynamic stretch",
                    purpose: "Aerobic base building — fat oxidation, capillary density",
                    zones: "Z2", rpe: "4-5"
                },

                {
                    day: 1, sport: "strength", type: "drill", duration: 50, intensity: "tempo", tss: 30,
                    desc: "Gym Session 1: Strength / Lower + Core",
                    warmup: "5 min dynamic: leg swings, hip circles, band walks",
                    main: "Back Squat 3×8 @RPE7 | Bulgarian Split Squat 3×10/leg | RDL 3×10 @RPE7 | Standing Calf Raise 3×15 | Hanging Leg Raise 3×12 | Pallof Press 3×10/side",
                    cooldown: "5 min static stretch: quads, hammies, hip flexors",
                    purpose: "Lower body strength, posterior chain development, core stability",
                    zones: "N/A", rpe: "7"
                },

                // Wednesday
                {
                    day: 2, sport: "swim", type: "drill", duration: 40, intensity: "easy", tss: 22,
                    desc: "Swim self-practice drills",
                    warmup: "Water walking, kick with board 4×25m",
                    main: "Breathing practice (6×25m freestyle attempts, 30s rest) + side-kick drill 4×25m",
                    cooldown: "5 min floating + relaxation",
                    purpose: "Reinforce coached lessons, build water confidence",
                    zones: "Z1", rpe: "3-4"
                },

                // Thursday
                {
                    day: 3, sport: "run", type: "tempo", duration: 50, intensity: "tempo", tss: 50,
                    desc: "Tempo run — lactate threshold",
                    warmup: "10 min easy jog + 4× strides",
                    main: "25 min @ 5:20-5:30/km (RPE 6-7) — just below threshold",
                    cooldown: "10 min easy jog + stretch",
                    purpose: "Lactate threshold development, teach body to clear lactate",
                    zones: "Z3", rpe: "6-7"
                },

                {
                    day: 3, sport: "strength", type: "drill", duration: 50, intensity: "tempo", tss: 30,
                    desc: "Gym Session 2: Hypertrophy / Upper + Core",
                    warmup: "5 min dynamic: arm circles, band pull-aparts, scap push-ups",
                    main: "Pull-ups 3×8 @RPE7 | Incline DB Press 3×10 | Cable Row 3×12 | DB Lateral Raise 3×15 | Face Pulls 3×15 | DB Bicep Curl 3×12 | Tricep Pushdown 3×12 | Plank 3×45s",
                    cooldown: "5 min stretch: lats, shoulders, chest",
                    purpose: "Upper body hypertrophy, swim-specific pulling strength, aesthetic physique",
                    zones: "N/A", rpe: "7"
                },

                // Friday
                {
                    day: 4, sport: "swim", type: "drill", duration: 40, intensity: "easy", tss: 22,
                    desc: "Swim practice + technique focus",
                    warmup: "Kick with board 4×25m, side-kick 4×25m",
                    main: "Side breathing practice, 6×25m freestyle with rest, fingertip drag drill 4×25m",
                    cooldown: "Easy floating 5 min",
                    purpose: "Technique development, stroke refinement",
                    zones: "Z1", rpe: "3-4"
                },

                // Saturday
                {
                    day: 5, sport: "bike", type: "long", duration: 90, intensity: "easy", tss: 65,
                    desc: "Long easy ride — aerobic base",
                    warmup: "10 min easy spin, cadence 75-80 rpm",
                    main: "70 min Z2, cadence focus 80-90 rpm, stay seated on climbs",
                    cooldown: "10 min easy spin + stretch",
                    purpose: "Cycling aerobic base, pedaling efficiency, fat oxidation",
                    zones: "Z2", rpe: "4-5"
                },

                {
                    day: 5, sport: "strength", type: "drill", duration: 45, intensity: "tempo", tss: 25,
                    desc: "Gym Session 3: Power / Full-Body",
                    warmup: "5 min dynamic: inchworms, world's greatest stretch, jump squats",
                    main: "Trap Bar Deadlift 3×6 @RPE8 | Push Press 3×6 | Weighted Dips 3×8 | Single-Arm DB Row 3×10/side | Lateral Raise 2×15 | Ab Wheel Rollout 3×10",
                    cooldown: "5 min mobility: thoracic, hips, ankles",
                    purpose: "Power development, full-body strength, lean mass maintenance",
                    zones: "N/A", rpe: "7-8"
                },

                // Sunday
                {
                    day: 6, sport: "run", type: "long", duration: 60, intensity: "easy", tss: 50,
                    desc: "Long easy run — endurance",
                    warmup: "10 min easy walk/jog",
                    main: "45 min @ 6:15-6:30/km — fully conversational",
                    cooldown: "5 min walk + foam roll",
                    purpose: "Aerobic endurance, teach body to burn fat at easy pace",
                    zones: "Z2", rpe: "4-5"
                },

                {
                    day: 6, sport: "mobility", type: "recovery", duration: 20, intensity: "easy", tss: 5,
                    desc: "Foam roll + mobility",
                    warmup: "—",
                    main: "Hip 90/90, ankle dorsiflexion, thoracic rotation, foam roll ITB/quads/calves",
                    cooldown: "—",
                    purpose: "Recovery, flexibility, injury prevention",
                    zones: "Z1", rpe: "2"
                },
            ]
        },

        // ── PHASE 2: AEROBIC BASE (8 weeks) ────────────────────────
        "Aerobic Base": {
            targetHours: 12,
            sessions: [
                {
                    day: 0, sport: "swim", type: "easy", duration: 50, intensity: "easy", tss: 35,
                    desc: "Swim endurance — continuous freestyle",
                    warmup: "200m easy + 4×50m drill (catch-up, fingertip drag)",
                    main: "4×100m freestyle @ 2:40/100m, 20s rest | 4×50m kick, 15s rest",
                    cooldown: "100m easy backstroke",
                    purpose: "Build swim endurance, stroke efficiency",
                    zones: "Z2", rpe: "4-5"
                },

                {
                    day: 1, sport: "run", type: "easy", duration: 50, intensity: "easy", tss: 40,
                    desc: "Easy aerobic run",
                    warmup: "10 min walk/easy jog",
                    main: "35 min Z2 @ 5:50-6:10/km — nasal breathing if possible",
                    cooldown: "5 min walk + stretch",
                    purpose: "Aerobic base, mitochondrial density, fat adaptation",
                    zones: "Z2", rpe: "4-5"
                },

                {
                    day: 1, sport: "strength", type: "drill", duration: 55, intensity: "tempo", tss: 35,
                    desc: "Gym Session 1: Strength / Lower + Core",
                    warmup: "5 min dynamic warm-up",
                    main: "Back Squat 4×6 @RPE7.5 | Walking Lunges 3×12/leg | RDL 3×8 @RPE7.5 | Leg Press 3×12 | Standing Calf Raise 4×15 | Hanging Leg Raise 3×15 | Side Plank 3×30s/side",
                    cooldown: "5 min static stretch",
                    purpose: "Progressive strength, posterior chain, injury prevention",
                    zones: "N/A", rpe: "7-8"
                },

                {
                    day: 2, sport: "swim", type: "drill", duration: 50, intensity: "easy", tss: 35,
                    desc: "Swim drills + build sets",
                    warmup: "200m easy mixed stroke",
                    main: "8×50m drill (catch-up, fingertip drag, fist swim) + 4×100m build (easy→moderate)",
                    cooldown: "100m easy",
                    purpose: "Technique refinement, stroke efficiency, feel for water",
                    zones: "Z1-Z2", rpe: "4-5"
                },

                {
                    day: 2, sport: "bike", type: "easy", duration: 45, intensity: "easy", tss: 30,
                    desc: "Easy recovery spin",
                    warmup: "10 min easy",
                    main: "30 min Z2, smooth pedaling, single-leg focus drills",
                    cooldown: "5 min easy spin",
                    purpose: "Active recovery + bike volume accumulation",
                    zones: "Z2", rpe: "3-4"
                },

                {
                    day: 3, sport: "run", type: "tempo", duration: 55, intensity: "tempo", tss: 55,
                    desc: "Tempo run — lactate clearance",
                    warmup: "10 min easy jog + 4× strides",
                    main: "30 min @ 5:15-5:25/km (RPE 6-7) — comfortably hard",
                    cooldown: "10 min easy + stretch",
                    purpose: "Threshold development, lactate clearance rate improvement",
                    zones: "Z3", rpe: "6-7"
                },

                {
                    day: 3, sport: "strength", type: "drill", duration: 55, intensity: "tempo", tss: 35,
                    desc: "Gym Session 2: Hypertrophy / Upper + Core",
                    warmup: "5 min dynamic: band pull-aparts, arm circles",
                    main: "Weighted Pull-ups 3×8 @RPE7 | Flat DB Bench Press 3×10 | Seated Cable Row 3×12 | Arnold Press 3×10 | Face Pulls 3×15 | EZ Bar Curl 3×12 | Overhead Tricep Extension 3×12 | Cable Crunch 3×15",
                    cooldown: "5 min stretch",
                    purpose: "Upper body hypertrophy, swim-specific strength, shoulder health",
                    zones: "N/A", rpe: "7-8"
                },

                {
                    day: 4, sport: "swim", type: "easy", duration: 50, intensity: "easy", tss: 35,
                    desc: "Swim endurance sets",
                    warmup: "200m easy",
                    main: "3×200m freestyle @ 2:35/100m, 20s rest | 200m pull buoy easy",
                    cooldown: "100m easy backstroke",
                    purpose: "Distance building, continuous swim adaptation",
                    zones: "Z2", rpe: "5"
                },

                {
                    day: 5, sport: "bike", type: "long", duration: 150, intensity: "easy", tss: 100,
                    desc: "Long ride — cycling endurance",
                    warmup: "15 min easy spin",
                    main: "120 min Z2, practice nutrition every 30 min (gel/bottle), cadence 85-95 rpm",
                    cooldown: "15 min easy spin + stretch",
                    purpose: "Cycling endurance, nutrition strategy rehearsal, aerobic adaptation",
                    zones: "Z2", rpe: "4-5"
                },

                {
                    day: 5, sport: "strength", type: "drill", duration: 50, intensity: "tempo", tss: 30,
                    desc: "Gym Session 3: Power / Full-Body",
                    warmup: "5 min dynamic warm-up",
                    main: "Front Squat 3×6 @RPE7.5 | Barbell Row 3×8 | Overhead Press 3×8 | Weighted Chin-ups 3×6 | Lateral Raise 3×15 | Rear Delt Fly 3×15 | Plank 3×60s",
                    cooldown: "5 min mobility",
                    purpose: "Full-body power, maintain lean mass, structural balance",
                    zones: "N/A", rpe: "7-8"
                },

                {
                    day: 6, sport: "run", type: "long", duration: 75, intensity: "easy", tss: 60,
                    desc: "Long run — endurance progression",
                    warmup: "10 min easy",
                    main: "60 min @ 5:55-6:10/km — practice mid-run fueling (gel at 40 min)",
                    cooldown: "5 min walk",
                    purpose: "Run endurance, fat oxidation, mental toughness",
                    zones: "Z2", rpe: "5"
                },

                {
                    day: 6, sport: "swim", type: "easy", duration: 30, intensity: "easy", tss: 18,
                    desc: "Easy recovery swim",
                    warmup: "—",
                    main: "30 min easy freestyle, focus on long strokes, relaxed breathing",
                    cooldown: "—",
                    purpose: "Active recovery + swim volume accumulation",
                    zones: "Z1", rpe: "3"
                },
            ]
        },

        // ── PHASE 3: BUILD (8 weeks) ───────────────────────────────
        "Build": {
            targetHours: 13,
            sessions: [
                {
                    day: 0, sport: "swim", type: "threshold", duration: 60, intensity: "threshold", tss: 55,
                    desc: "Swim threshold sets",
                    warmup: "200m easy + 4×50m drill",
                    main: "6×150m @ 2:20-2:30/100m, 20s rest — push the pace",
                    cooldown: "200m easy backstroke",
                    purpose: "Swim lactate tolerance, race-pace development",
                    zones: "Z3-Z4", rpe: "6-7"
                },

                {
                    day: 1, sport: "run", type: "intervals", duration: 55, intensity: "threshold", tss: 60,
                    desc: "VO2max intervals",
                    warmup: "15 min easy + 4× strides",
                    main: "6×800m @ 4:40-4:50/km, 90s jog recovery — hard but controlled",
                    cooldown: "10 min easy jog",
                    purpose: "VO2max stimulus, running economy, speed endurance",
                    zones: "Z4-Z5", rpe: "8"
                },

                {
                    day: 1, sport: "strength", type: "drill", duration: 50, intensity: "tempo", tss: 28,
                    desc: "Gym Session 1: Strength Maintenance / Lower",
                    warmup: "5 min dynamic warm-up",
                    main: "Back Squat 3×5 @RPE7 | Split Squat 3×8/leg | Hamstring Curl 3×12 | Calf Raise 3×15 | Hanging Leg Raise 3×12 | Pallof Press 3×10/side",
                    cooldown: "5 min stretch",
                    purpose: "Maintain lower body strength, reduce volume to support race training",
                    zones: "N/A", rpe: "7"
                },

                {
                    day: 2, sport: "swim", type: "easy", duration: 55, intensity: "easy", tss: 45,
                    desc: "Swim endurance — continuous",
                    warmup: "400m easy mixed",
                    main: "3×400m @ 2:30-2:40/100m, 30s rest — continuous effort",
                    cooldown: "200m easy pull buoy",
                    purpose: "Continuous swim endurance, race-distance confidence",
                    zones: "Z2", rpe: "5"
                },

                {
                    day: 2, sport: "bike", type: "tempo", duration: 60, intensity: "tempo", tss: 55,
                    desc: "Bike tempo intervals",
                    warmup: "15 min easy spin",
                    main: "3×8 min @ RPE 6-7 (threshold effort), 4 min easy between",
                    cooldown: "10 min easy spin",
                    purpose: "Cycling threshold, power at pace, FTP development",
                    zones: "Z3-Z4", rpe: "6-7"
                },

                {
                    day: 3, sport: "run", type: "easy", duration: 45, intensity: "easy", tss: 30,
                    desc: "Easy recovery run",
                    warmup: "5 min walk",
                    main: "35 min Z2 @ 6:10-6:30/km — truly easy, recovery focus",
                    cooldown: "5 min walk + foam roll",
                    purpose: "Recovery, maintain volume without added stress",
                    zones: "Z2", rpe: "3-4"
                },

                {
                    day: 3, sport: "strength", type: "drill", duration: 45, intensity: "tempo", tss: 22,
                    desc: "Gym Session 2: Maintenance / Upper",
                    warmup: "5 min dynamic warm-up",
                    main: "Pull-ups 3×6 | DB Bench Press 3×8 | Cable Row 3×10 | Face Pulls 3×12 | DB Curl 2×12 | Tricep Dip 2×10 | Plank 3×45s",
                    cooldown: "5 min stretch",
                    purpose: "Maintain upper body, reduced volume in build phase",
                    zones: "N/A", rpe: "6-7"
                },

                {
                    day: 4, sport: "swim", type: "tempo", duration: 55, intensity: "tempo", tss: 45,
                    desc: "Race-pace swim practice",
                    warmup: "300m easy",
                    main: "8×100m @ race pace (2:25-2:35/100m), 15s rest — simulate race effort",
                    cooldown: "200m easy",
                    purpose: "Race-pace familiarity, pacing discipline",
                    zones: "Z3", rpe: "6"
                },

                {
                    day: 5, sport: "bike", type: "brick", duration: 120, intensity: "tempo", tss: 105,
                    desc: "Brick: Bike → Run transition",
                    warmup: "10 min easy spin",
                    main: "75 min ride (last 20 min @ race effort) → T2 (quick change) → 30 min run @ 5:50-6:00/km",
                    cooldown: "5 min walk",
                    purpose: "Multi-sport fatigue adaptation, T2 practice, race simulation",
                    zones: "Z2-Z3", rpe: "6-7"
                },

                {
                    day: 5, sport: "strength", type: "drill", duration: 40, intensity: "easy", tss: 18,
                    desc: "Gym Session 3: Maintenance / Full-Body",
                    warmup: "5 min dynamic warm-up",
                    main: "Goblet Squat 3×10 | Push-ups 3×15 | TRX Row 3×12 | Side Plank 3×30s/side | Band Pull-Apart 3×15 | Bird Dog 3×10/side",
                    cooldown: "5 min mobility",
                    purpose: "Light maintenance, injury prevention, movement quality",
                    zones: "N/A", rpe: "5-6"
                },

                {
                    day: 6, sport: "run", type: "long", duration: 85, intensity: "easy", tss: 70,
                    desc: "Long run with fueling practice",
                    warmup: "10 min easy",
                    main: "70 min @ 5:50-6:05/km, gel at 35 min and 60 min — practice race nutrition",
                    cooldown: "5 min walk",
                    purpose: "Endurance, nutrition rehearsal, mental toughness",
                    zones: "Z2", rpe: "5-6"
                },

                {
                    day: 6, sport: "swim", type: "easy", duration: 30, intensity: "easy", tss: 18,
                    desc: "Easy recovery swim",
                    warmup: "—",
                    main: "30 min easy freestyle, long strokes, relaxed",
                    cooldown: "—",
                    purpose: "Active recovery, total swim volume",
                    zones: "Z1", rpe: "3"
                },
            ]
        },

        // ── PHASE 4: RACE-SPECIFIC (6 weeks) ───────────────────────
        "Race-Specific": {
            targetHours: 13,
            sessions: [
                {
                    day: 0, sport: "swim", type: "tempo", duration: 55, intensity: "tempo", tss: 50,
                    desc: "Race-pace swim sets — extended",
                    warmup: "300m easy + 4×50m drill",
                    main: "3×600m @ race pace (2:25-2:35/100m), 30s rest",
                    cooldown: "200m easy",
                    purpose: "Race-pace endurance, swim confidence at distance",
                    zones: "Z3", rpe: "6"
                },

                {
                    day: 1, sport: "run", type: "tempo", duration: 60, intensity: "tempo", tss: 60,
                    desc: "Race-pace sustained tempo",
                    warmup: "10 min easy + strides",
                    main: "40 min @ 5:45-6:00/km (projected race effort) — practice negative split",
                    cooldown: "10 min easy",
                    purpose: "Race-pace familiarity, pacing strategy, mental rehearsal",
                    zones: "Z3", rpe: "6-7"
                },

                {
                    day: 1, sport: "strength", type: "easy", duration: 35, intensity: "easy", tss: 15,
                    desc: "Gym Session 1: Light Maintenance",
                    warmup: "5 min dynamic",
                    main: "Bodyweight Squat 3×15 | Push-ups 3×12 | Band Row 3×15 | Plank 3×45s | Calf Raise 3×20",
                    cooldown: "5 min mobility",
                    purpose: "Maintenance only — preserve muscle, prevent atrophy",
                    zones: "N/A", rpe: "4-5"
                },

                {
                    day: 2, sport: "bike", type: "tempo", duration: 75, intensity: "tempo", tss: 70,
                    desc: "Bike race-pace simulation",
                    warmup: "15 min easy spin",
                    main: "45 min @ race effort with nutrition practice every 20 min",
                    cooldown: "15 min easy spin",
                    purpose: "Race simulation, nutrition timing, aerobar position endurance",
                    zones: "Z3", rpe: "6-7"
                },

                {
                    day: 2, sport: "swim", type: "easy", duration: 40, intensity: "easy", tss: 30,
                    desc: "Open-water simulation — sighting drills",
                    warmup: "200m easy",
                    main: "8×100m with head-up sighting every 8 strokes + 4×50m draft practice",
                    cooldown: "100m easy",
                    purpose: "Open-water preparation, race-day skills",
                    zones: "Z2", rpe: "5"
                },

                {
                    day: 3, sport: "run", type: "easy", duration: 40, intensity: "easy", tss: 25,
                    desc: "Easy recovery run",
                    warmup: "5 min walk",
                    main: "30 min Z2 easy — shake out legs",
                    cooldown: "5 min walk + foam roll",
                    purpose: "Active recovery between hard sessions",
                    zones: "Z2", rpe: "3-4"
                },

                {
                    day: 3, sport: "strength", type: "easy", duration: 30, intensity: "easy", tss: 12,
                    desc: "Gym Session 2: Mobility + Core",
                    warmup: "5 min dynamic",
                    main: "Goblet Squat 2×10 | Band Pull-Apart 3×15 | Plank 3×45s | Side Plank 3×30s | Bird Dog 3×10/side",
                    cooldown: "5 min stretch",
                    purpose: "Core stability, movement maintenance, injury prevention",
                    zones: "N/A", rpe: "4"
                },

                {
                    day: 4, sport: "swim", type: "easy", duration: 50, intensity: "easy", tss: 45,
                    desc: "Swim full-distance simulation",
                    warmup: "200m easy",
                    main: "1900m continuous at race pace — the full 70.3 swim distance",
                    cooldown: "100m easy",
                    purpose: "Race distance confidence, pacing strategy",
                    zones: "Z2-Z3", rpe: "5-6"
                },

                {
                    day: 5, sport: "bike", type: "brick", duration: 280, intensity: "tempo", tss: 210,
                    desc: "Full race simulation brick",
                    warmup: "15 min easy spin",
                    main: "90 km ride @ race pace → T2 → 15-18 km run @ race effort — FULL nutrition plan",
                    cooldown: "5 min walk",
                    purpose: "Complete race simulation, nutritional dry run, transition practice",
                    zones: "Z2-Z3", rpe: "6-7"
                },

                {
                    day: 5, sport: "strength", type: "easy", duration: 25, intensity: "easy", tss: 10,
                    desc: "Gym Session 3: Very Light",
                    warmup: "5 min dynamic",
                    main: "Band work: pull-aparts, monster walks | Core: dead bug 3×10, pallof press 3×10/side",
                    cooldown: "5 min stretch",
                    purpose: "Light activation, injury prevention only",
                    zones: "N/A", rpe: "3-4"
                },

                {
                    day: 6, sport: "mobility", type: "recovery", duration: 30, intensity: "easy", tss: 5,
                    desc: "Recovery + mobility session",
                    warmup: "—",
                    main: "Foam roll full body, 90/90 hip stretches, ankle mobility, thoracic rotation",
                    cooldown: "—",
                    purpose: "Recovery from race simulation, prepare for next week",
                    zones: "Z1", rpe: "2"
                },

                {
                    day: 6, sport: "swim", type: "easy", duration: 30, intensity: "easy", tss: 15,
                    desc: "Easy recovery swim",
                    warmup: "—",
                    main: "30 min easy, relaxed strokes, breathing focus",
                    cooldown: "—",
                    purpose: "Active recovery, maintain water feel",
                    zones: "Z1", rpe: "3"
                },
            ]
        },

        // ── PHASE 5: TAPER (2 weeks) ──────────────────────────────
        "Taper": {
            targetHours: 7,
            sessions: [
                {
                    day: 0, sport: "swim", type: "easy", duration: 30, intensity: "easy", tss: 20,
                    desc: "Short race-pace intervals",
                    warmup: "200m easy",
                    main: "4×100m @ race pace, 30s rest — crisp, fast strokes",
                    cooldown: "100m easy",
                    purpose: "Maintain feel for water, neuromuscular sharpness",
                    zones: "Z2-Z3", rpe: "5"
                },

                {
                    day: 1, sport: "run", type: "easy", duration: 35, intensity: "easy", tss: 25,
                    desc: "Easy run with strides",
                    warmup: "10 min easy",
                    main: "15 min easy + 4×30s strides (fast but relaxed)",
                    cooldown: "5 min walk",
                    purpose: "Maintain leg turnover, neuromuscular activation",
                    zones: "Z2", rpe: "4"
                },

                {
                    day: 2, sport: "bike", type: "easy", duration: 45, intensity: "easy", tss: 30,
                    desc: "Easy spin with openers",
                    warmup: "15 min easy",
                    main: "20 min easy + 3×2 min @ race effort — feel the power",
                    cooldown: "10 min easy",
                    purpose: "Maintain cycling feel, race-pace recall",
                    zones: "Z2", rpe: "4"
                },

                {
                    day: 3, sport: "swim", type: "easy", duration: 25, intensity: "easy", tss: 15,
                    desc: "Easy swim — relax",
                    warmup: "100m easy",
                    main: "400m relaxed freestyle, focus on technique",
                    cooldown: "—",
                    purpose: "Water comfort, race-week confidence",
                    zones: "Z1", rpe: "3"
                },

                {
                    day: 4, sport: "run", type: "easy", duration: 25, intensity: "easy", tss: 15,
                    desc: "Short easy shakeout",
                    warmup: "5 min walk",
                    main: "15 min easy jog + 2× strides",
                    cooldown: "5 min walk",
                    purpose: "Keep legs loose, mental preparation",
                    zones: "Z2", rpe: "3"
                },

                {
                    day: 5, sport: "mobility", type: "recovery", duration: 20, intensity: "easy", tss: 5,
                    desc: "Full body mobility + visualization",
                    warmup: "—",
                    main: "Foam roll, gentle stretches, 10 min race visualization (swim start → finish line)",
                    cooldown: "—",
                    purpose: "Recovery + mental race preparation",
                    zones: "Z1", rpe: "2"
                },

                {
                    day: 6, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Race Day: IRONMAN 70.3 GOA",
                    warmup: "Race morning routine: light jog, dynamic stretch",
                    main: "1.9km SWIM → 90km BIKE → 21.1km RUN — Execute the plan!",
                    cooldown: "Celebrate. You're an Ironman.",
                    purpose: "RACE DAY",
                    zones: "All", rpe: "10"
                },
            ]
        },
    };

    // ── Workout Library (drag-and-drop templates) ────────────────
    const WORKOUT_LIBRARY = [
        {
            id: "lib-swim-easy", sport: "swim", type: "easy", duration: 30, intensity: "easy",
            desc: "Easy Swim", tss: 20, main: "Relaxed freestyle, technique focus"
        },
        {
            id: "lib-swim-drill", sport: "swim", type: "drill", duration: 45, intensity: "easy",
            desc: "Swim Drills", tss: 25, main: "Catch-up, fingertip drag, kick drills"
        },
        {
            id: "lib-swim-threshold", sport: "swim", type: "threshold", duration: 55, intensity: "threshold",
            desc: "Swim Threshold", tss: 50, main: "6×150m @ threshold pace"
        },
        {
            id: "lib-bike-easy", sport: "bike", type: "easy", duration: 45, intensity: "easy",
            desc: "Easy Spin", tss: 30, main: "Z2 spinning, smooth pedaling"
        },
        {
            id: "lib-bike-long", sport: "bike", type: "long", duration: 120, intensity: "easy",
            desc: "Long Ride", tss: 90, main: "Z2 endurance ride with nutrition"
        },
        {
            id: "lib-bike-tempo", sport: "bike", type: "tempo", duration: 60, intensity: "tempo",
            desc: "Bike Tempo", tss: 55, main: "3×8min tempo intervals"
        },
        {
            id: "lib-bike-brick", sport: "bike", type: "brick", duration: 110, intensity: "tempo",
            desc: "Brick Session", tss: 100, main: "Bike → Run transition"
        },
        {
            id: "lib-run-easy", sport: "run", type: "easy", duration: 40, intensity: "easy",
            desc: "Easy Run", tss: 30, main: "Z2 conversational pace"
        },
        {
            id: "lib-run-long", sport: "run", type: "long", duration: 75, intensity: "easy",
            desc: "Long Run", tss: 60, main: "Endurance run with mid-run fuel"
        },
        {
            id: "lib-run-tempo", sport: "run", type: "tempo", duration: 50, intensity: "tempo",
            desc: "Tempo Run", tss: 50, main: "25-30min at threshold pace"
        },
        {
            id: "lib-run-intervals", sport: "run", type: "intervals", duration: 50, intensity: "threshold",
            desc: "VO2max Intervals", tss: 60, main: "6×800m hard, 90s jog rest"
        },
        {
            id: "lib-strength-lower", sport: "strength", type: "drill", duration: 50, intensity: "tempo",
            desc: "Strength: Lower Body", tss: 30, main: "Squat, RDL, Split Squat, Core"
        },
        {
            id: "lib-strength-upper", sport: "strength", type: "drill", duration: 50, intensity: "tempo",
            desc: "Strength: Upper Body", tss: 30, main: "Pull-ups, Bench, Rows, Core"
        },
        {
            id: "lib-strength-full", sport: "strength", type: "drill", duration: 45, intensity: "tempo",
            desc: "Strength: Full Body", tss: 25, main: "Deadlift, Press, Row, Core"
        },
        {
            id: "lib-mobility", sport: "mobility", type: "recovery", duration: 20, intensity: "easy",
            desc: "Mobility & Foam Roll", tss: 5, main: "Full body foam roll, stretching"
        },
        {
            id: "lib-rest", sport: "rest", type: "recovery", duration: 0, intensity: "easy",
            desc: "Rest Day", tss: 0, main: "Complete rest — sleep, hydrate, recover"
        },
    ];

    // ── Plan Generation ──────────────────────────────────────────
    function generatePlan(startDate = PLAN_START) {
        const workouts = [];
        let currentDate = new Date(startDate);
        let weekNumber = 1;
        let globalId = 1;

        for (const phase of PHASES) {
            const template = WEEKLY_TEMPLATES[phase.name] || WEEKLY_TEMPLATES["Aerobic Base"];

            for (let w = 0; w < phase.weeks; w++) {
                const isDeload = (w + 1) % 4 === 0 && phase.name !== "Taper";
                const weekStart = new Date(currentDate);
                const progressionFactor = Math.min(1.0 + (w / phase.weeks) * 0.15, 1.15);

                for (const session of template.sessions) {
                    const sessionDate = new Date(weekStart);
                    sessionDate.setDate(sessionDate.getDate() + session.day);

                    let dur = session.duration;
                    let tss = session.tss;

                    if (isDeload) {
                        dur = Math.round(dur * 0.6);
                        tss = Math.round(tss * 0.5);
                    } else {
                        dur = Math.round(dur * progressionFactor);
                        tss = Math.round(tss * progressionFactor);
                    }

                    workouts.push({
                        id: `w-${globalId++}`,
                        date: formatDate(sessionDate),
                        sport: session.sport,
                        type: session.type,
                        duration: dur,
                        intensity: session.intensity,
                        desc: session.desc,
                        warmup: session.warmup || "",
                        main: session.main || "",
                        cooldown: session.cooldown || "",
                        purpose: session.purpose || "",
                        zones: session.zones || "",
                        rpe: session.rpe || "",
                        tssPlanned: tss,
                        tssActual: null,
                        phase: phase.name,
                        phaseColor: phase.color,
                        weekNumber: weekNumber,
                        isDeload: isDeload,
                        status: "planned",
                        actualDuration: null,
                        actualHR: null,
                        rpeActual: null,
                        notes: "",
                        bookmarked: false,
                    });
                }

                currentDate.setDate(currentDate.getDate() + 7);
                weekNumber++;
            }
        }

        return workouts;
    }

    // ── Sample Completion Data (for demo) ────────────────────────
    function addSampleCompletionData(workouts) {
        const today = new Date();
        const todayStr = formatDate(today);
        let seed = 42;
        const rng = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

        for (const w of workouts) {
            if (w.date <= todayStr && w.sport !== "rest") {
                const roll = rng();
                if (roll < 0.80) {
                    w.status = "completed";
                    w.actualDuration = Math.round(w.duration * (0.85 + rng() * 0.25));
                    w.rpeActual = Math.floor(4 + rng() * 5);
                    w.tssActual = Math.round(w.tssPlanned * (0.8 + rng() * 0.35));
                    if (w.sport === "run") w.actualHR = Math.floor(135 + rng() * 30);
                    else if (w.sport === "bike") w.actualHR = Math.floor(130 + rng() * 25);
                    else if (w.sport === "swim") w.actualHR = Math.floor(125 + rng() * 30);
                } else if (roll < 0.90) {
                    w.status = "modified";
                    w.actualDuration = Math.round(w.duration * (0.5 + rng() * 0.3));
                    w.rpeActual = Math.floor(3 + rng() * 4);
                    w.tssActual = Math.round(w.tssPlanned * (0.5 + rng() * 0.3));
                    w.notes = "Modified due to fatigue/time constraint";
                } else {
                    w.status = "skipped";
                    w.notes = "Skipped — recovery priority";
                }
            }
        }
        return workouts;
    }

    // ── Analytics: CTL / ATL / TSB ───────────────────────────────
    const CTL_CONSTANT = 42;
    const ATL_CONSTANT = 7;

    function calculateMetrics(workouts) {
        const dailyTSS = {};
        for (const w of workouts) {
            const tss = w.tssActual || (w.status === "completed" ? w.tssPlanned : 0);
            dailyTSS[w.date] = (dailyTSS[w.date] || 0) + tss;
        }

        const dates = Object.keys(dailyTSS).sort();
        if (dates.length === 0) return [];

        const startDate = new Date(dates[0]);
        const endDate = new Date(dates[dates.length - 1]);
        const metrics = [];
        let ctl = 0, atl = 0;

        for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
            const dateStr = formatDate(d);
            const tss = dailyTSS[dateStr] || 0;
            ctl = ctl + (tss - ctl) / CTL_CONSTANT;
            atl = atl + (tss - atl) / ATL_CONSTANT;
            const tsb = ctl - atl;

            metrics.push({ date: dateStr, ctl: Math.round(ctl * 10) / 10, atl: Math.round(atl * 10) / 10, tsb: Math.round(tsb * 10) / 10, tss });
        }

        return metrics;
    }

    // ── Weekly Volume Calculation ────────────────────────────────
    function calculateWeeklyVolume(workouts) {
        const weeks = {};
        for (const w of workouts) {
            if (!weeks[w.weekNumber]) {
                weeks[w.weekNumber] = { week: w.weekNumber, phase: w.phase, swim: 0, bike: 0, run: 0, strength: 0, total: 0 };
            }
            const dur = w.actualDuration || (w.status === "completed" ? w.duration : 0);
            if (["swim", "bike", "run", "strength"].includes(w.sport)) {
                weeks[w.weekNumber][w.sport] += dur;
            }
            weeks[w.weekNumber].total += dur;
        }
        return Object.values(weeks).sort((a, b) => a.week - b.week);
    }

    // ── Compliance ───────────────────────────────────────────────
    function calculateCompliance(workouts) {
        const today = formatDate(new Date());
        const past = workouts.filter(w => w.date <= today && w.sport !== "rest");
        const completed = past.filter(w => w.status === "completed" || w.status === "modified");
        const overall = past.length > 0 ? (completed.length / past.length * 100) : 0;

        const bySport = {};
        for (const w of past) {
            if (!bySport[w.sport]) bySport[w.sport] = { total: 0, done: 0 };
            bySport[w.sport].total++;
            if (w.status === "completed" || w.status === "modified") bySport[w.sport].done++;
        }

        return { overall: Math.round(overall), bySport };
    }

    // ── Helpers ──────────────────────────────────────────────────
    function formatDate(d) {
        const dd = new Date(d);
        const year = dd.getFullYear();
        const month = String(dd.getMonth() + 1).padStart(2, "0");
        const day = String(dd.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    function daysToRace() {
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        const diff = Math.ceil((RACE_DATE - now) / (1000 * 60 * 60 * 24));
        return Math.max(0, diff);
    }

    function getCurrentPhase(workouts) {
        const today = formatDate(new Date());
        for (const w of workouts) {
            if (w.date === today) return w.phase;
        }
        const sortedByDate = [...workouts].sort((a, b) => b.date.localeCompare(a.date));
        for (const w of sortedByDate) {
            if (w.date <= today) return w.phase;
        }
        return PHASES[0].name;
    }

    function getCurrentWeek(workouts) {
        const today = formatDate(new Date());
        for (const w of [...workouts].reverse()) {
            if (w.date <= today) return w.weekNumber;
        }
        return 1;
    }

    function getWorkoutsForDate(workouts, dateStr) {
        return workouts.filter(w => w.date === dateStr);
    }

    // ── Public API ───────────────────────────────────────────────
    return {
        ATHLETE,
        HR_ZONES,
        RACE_NAME,
        RACE_DATE,
        PLAN_START,
        SPORT_COLORS,
        SPORT_ICONS,
        INTENSITY_COLORS,
        PHASES,
        WORKOUT_LIBRARY,
        generatePlan,
        addSampleCompletionData,
        calculateMetrics,
        calculateWeeklyVolume,
        calculateCompliance,
        getHRZone,
        formatDate,
        daysToRace,
        getCurrentPhase,
        getCurrentWeek,
        getWorkoutsForDate,
    };

})();
