/* ═══════════════════════════════════════════════════════════════
   IRONPLAN 70.3 — Training Data Engine
   20-week periodized plan from Strategic Training Protocol PDF
   Mon/Thu rest · 2-2-2 rule · Hybrid athlete approach
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
        fiveKPace: "5:30",
        cyclingRange: 20,
        swimLevel: 0,
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
    const PLAN_START = new Date(2026, 3, 13); // Mon Apr 13, 2026 — Week 1 starts
    const RACE_DATE = new Date(2026, 7, 30);  // Sun Aug 30, 2026 — Week 20 Sunday

    // Race distances
    const RACE_DISTANCES = {
        swim: 1.9,   // km
        bike: 90,    // km
        run: 21.1,   // km (half marathon)
    };

    // ── Sport & Intensity Colors ─────────────────────────────────
    const SPORT_COLORS = {
        swim: "#0984E3", bike: "#00B894", run: "#E17055", strength: "#6C5CE7",
        mobility: "#FDCB6E", recovery: "#81ECEC", race: "#E84393", rest: "#636E72",
    };

    const SPORT_ICONS = {
        swim: "🏊", bike: "🚴", run: "🏃", strength: "🏋️",
        mobility: "🧘", recovery: "💤", race: "🏁", rest: "😴",
    };

    const INTENSITY_COLORS = {
        easy: "#00B894", tempo: "#0984E3", threshold: "#E17055",
        intervals: "#D63031", long: "#6C5CE7", brick: "#E84393",
        drill: "#FDCB6E", recovery: "#81ECEC",
    };

    // ── Phase Definitions (20-week plan from PDF) ────────────────
    const PHASES = [
        {
            name: "Aquatic Immersion & Foundation", weeks: 4, color: "#6C5CE7",
            desc: "Master the water from zero. 3x weekly morning swims for neuromuscular patterning. Maintenance running and aerobic cycling base."
        },
        {
            name: "2-2-2 Hybrid Balance", weeks: 8, color: "#0984E3",
            desc: "Expand structural tolerance. 2 swims/week, increase cycling saddle time, maintain half-marathon readiness."
        },
        {
            name: "Specificity & Heat Acclimation", weeks: 5, color: "#00B894",
            desc: "Simulate Goa race conditions. Race-pace intervals, open-water ocean simulation, GI nutrition practice."
        },
        {
            name: "Peak & Taper", weeks: 3, color: "#FDCB6E",
            desc: "Maximize readiness, shed fatigue. 2-3 week volume reduction, glycogen supercompensation, neural sharpening."
        },
    ];

    // ── Weekly Templates (Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6) ──
    // Mon/Thu = REST days (office 09:00-21:00)
    // Wed/Sun = Hardest days (before rest days)
    const WEEKLY_TEMPLATES = {

        // ═══ PHASE 1: Aquatic Immersion & Foundation (Weeks 1-4) ═══
        // 3 swims/week (Tue, Fri, Sat), strength Tue/Fri, rest Mon/Thu
        "Aquatic Immersion & Foundation": {
            targetHours: 9,
            sessions: [
                // Monday - REST
                {
                    day: 0, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest — office day (09:00-21:00). Focus on sleep, hydration, high-protein nutrition.",
                    cooldown: "—", purpose: "Recovery from Sunday's hard session. Anabolic nutrition priority.",
                    zones: "N/A", rpe: "0"
                },

                // Tuesday - AM Swim (Coached) + PM Strength A (Pull Dominant)
                {
                    day: 1, sport: "swim", type: "drill", duration: 45, intensity: "easy", tss: 25,
                    desc: "Coached Swim Lesson",
                    warmup: "Water comfort drills, floating, wall kicks",
                    main: "Coach-led technique: body position, kick timing, bilateral breathing. 6×25m freestyle attempts with rest.",
                    cooldown: "5 min gentle floating, relaxation",
                    purpose: "Water comfort and basic freestyle mechanics from absolute zero.",
                    zones: "Z1-Z2", rpe: "3-4"
                },
                {
                    day: 1, sport: "strength", type: "drill", duration: 40, intensity: "tempo", tss: 30,
                    desc: "Strength A: Pull Dominant + Push Accessory",
                    warmup: "5 min dynamic: band pull-aparts, arm circles, scap push-ups",
                    main: "Weighted Pull-Ups/Lat Pulldowns 3×6-8 | Incline DB Bench Press 3×8-10 | Chest-Supported DB Rows 3×8-10 | DB Lateral Raises 3×10-12 | Superset: Hammer Curls & Overhead Triceps Ext. 2×10-12",
                    cooldown: "5 min stretch: lats, shoulders, chest",
                    purpose: "V-taper width, lat development for swim stroke, shoulder health. RPE 8-9, 2 min rest between compounds.",
                    zones: "N/A", rpe: "8-9"
                },

                // Wednesday - Hard Day: Cycling + Run
                {
                    day: 2, sport: "bike", type: "easy", duration: 60, intensity: "easy", tss: 40,
                    desc: "Aerobic Cycling Base",
                    warmup: "10 min easy spin, cadence 75-80 rpm",
                    main: "45 min Z2 steady state, cadence focus 80-90 rpm, stay seated on inclines",
                    cooldown: "5 min easy spin + stretch",
                    purpose: "Time in saddle, pedaling efficiency, cycling aerobic base building.",
                    zones: "Z2", rpe: "4-5"
                },
                {
                    day: 2, sport: "run", type: "easy", duration: 35, intensity: "easy", tss: 25,
                    desc: "Easy Recovery Run",
                    warmup: "5 min walk → easy jog",
                    main: "25 min Z2 @ 6:00-6:30/km — truly conversational",
                    cooldown: "5 min walk + dynamic stretch",
                    purpose: "Aerobic flush, maintain running base without adding stress.",
                    zones: "Z2", rpe: "4"
                },

                // Thursday - REST
                {
                    day: 3, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest — office day (09:00-21:00). Anabolic nutrition, stretching if time.",
                    cooldown: "—", purpose: "Recovery from Wednesday's hard session.",
                    zones: "N/A", rpe: "0"
                },

                // Friday - AM Swim (Self-Practice) + PM Strength B (Push Dominant)
                {
                    day: 4, sport: "swim", type: "drill", duration: 40, intensity: "easy", tss: 22,
                    desc: "Swim Self-Practice Drills",
                    warmup: "Water walking, kick with board 4×25m",
                    main: "Side breathing practice, 6×25m freestyle with rest, fingertip drag drill 4×25m, side-kick drill 4×25m",
                    cooldown: "5 min floating + relaxation",
                    purpose: "Reinforce coached lessons, build water confidence independently.",
                    zones: "Z1", rpe: "3-4"
                },
                {
                    day: 4, sport: "strength", type: "drill", duration: 40, intensity: "tempo", tss: 30,
                    desc: "Strength B: Push Dominant + Pull Accessory + Core",
                    warmup: "5 min dynamic: arm circles, band pull-aparts, thoracic rotation",
                    main: "Seated DB Overhead Press 3×6-8 | Neutral Grip Cable Rows/T-Bar Rows 3×8-10 | DB/Cable Chest Flyes 2×10-12 | Face Pulls 3×12-15 | Weighted Planks 3×45-60s",
                    cooldown: "5 min stretch: shoulders, chest, core",
                    purpose: "3D shoulders, chest thickness, anti-rotational core stability. Bulletproof rotator cuff.",
                    zones: "N/A", rpe: "8-9"
                },

                // Saturday - AM Swim (Technique) + Long Ride
                {
                    day: 5, sport: "swim", type: "drill", duration: 40, intensity: "easy", tss: 22,
                    desc: "Swim Technique Focus",
                    warmup: "Kick with board 4×25m, side-kick 4×25m",
                    main: "Catch-up drill 4×25m, fingertip drag 4×25m, 6×25m freestyle with focus on long glide per stroke",
                    cooldown: "Easy floating 5 min",
                    purpose: "Stroke refinement, develop feel for water, breathing rhythm.",
                    zones: "Z1", rpe: "3-4"
                },
                {
                    day: 5, sport: "bike", type: "long", duration: 90, intensity: "easy", tss: 65,
                    desc: "Long Easy Ride — Aerobic Base",
                    warmup: "10 min easy spin, cadence 75-80 rpm",
                    main: "70 min Z2, cadence focus 80-90 rpm, practice nutrition every 30 min",
                    cooldown: "10 min easy spin + stretch",
                    purpose: "Cycling aerobic base, pedaling efficiency, fat oxidation, saddle time.",
                    zones: "Z2", rpe: "4-5"
                },

                // Sunday - Hard Day: Long Run + Mobility
                {
                    day: 6, sport: "run", type: "long", duration: 60, intensity: "easy", tss: 50,
                    desc: "Long Easy Run — Endurance",
                    warmup: "10 min easy walk/jog",
                    main: "45 min @ 6:00-6:30/km — fully conversational, leveraging half-marathon stamina",
                    cooldown: "5 min walk + foam roll",
                    purpose: "Aerobic endurance, fat oxidation, aerobic flush for the week.",
                    zones: "Z2", rpe: "4-5"
                },
                {
                    day: 6, sport: "mobility", type: "recovery", duration: 20, intensity: "easy", tss: 5,
                    desc: "Foam Roll + Mobility",
                    warmup: "—",
                    main: "Hip 90/90, ankle dorsiflexion, thoracic rotation, foam roll ITB/quads/calves",
                    cooldown: "—",
                    purpose: "Recovery, flexibility, injury prevention before Monday rest.",
                    zones: "Z1", rpe: "2"
                },
            ]
        },

        // ═══ PHASE 2: 2-2-2 Hybrid Balance (Weeks 5-12) ═══
        // 2 swims, 2 bikes, 2 runs per week + strength Tue/Fri
        "2-2-2 Hybrid Balance": {
            targetHours: 10,
            sessions: [
                // Monday - REST
                {
                    day: 0, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest — office day. Prioritize sleep & high-protein meals.",
                    cooldown: "—", purpose: "Recovery from Sunday's long session.",
                    zones: "N/A", rpe: "0"
                },

                // Tuesday - Swim Endurance + Strength A
                {
                    day: 1, sport: "swim", type: "easy", duration: 50, intensity: "easy", tss: 35,
                    desc: "Swim Endurance — Continuous Freestyle",
                    warmup: "200m easy + 4×50m drill (catch-up, fingertip drag)",
                    main: "4×100m freestyle @ 2:40/100m, 20s rest | 4×50m kick, 15s rest",
                    cooldown: "100m easy backstroke",
                    purpose: "Build swim endurance, stroke efficiency, water confidence.",
                    zones: "Z2", rpe: "4-5"
                },
                {
                    day: 1, sport: "strength", type: "drill", duration: 40, intensity: "tempo", tss: 30,
                    desc: "Strength A: Pull Dominant + Push Accessory",
                    warmup: "5 min dynamic warm-up",
                    main: "Weighted Pull-Ups/Lat Pulldowns 3×6-8 | Incline DB Bench Press 3×8-10 | Chest-Supported DB Rows 3×8-10 | DB Lateral Raises 3×10-12 | Superset: Hammer Curls & Overhead Triceps Ext. 2×10-12",
                    cooldown: "5 min stretch",
                    purpose: "Maintain V-taper, pulling power for swim stroke improvement.",
                    zones: "N/A", rpe: "8-9"
                },

                // Wednesday - Hard: Bike Tempo + Run Tempo
                {
                    day: 2, sport: "bike", type: "tempo", duration: 60, intensity: "tempo", tss: 55,
                    desc: "Bike Tempo — Threshold Development",
                    warmup: "15 min easy spin",
                    main: "3×8 min @ RPE 6-7 (threshold effort), 4 min easy between",
                    cooldown: "10 min easy spin",
                    purpose: "Cycling threshold, power at pace, FTP development.",
                    zones: "Z3-Z4", rpe: "6-7"
                },
                {
                    day: 2, sport: "run", type: "tempo", duration: 50, intensity: "tempo", tss: 50,
                    desc: "Tempo Run — Lactate Threshold",
                    warmup: "10 min easy jog + 4× strides",
                    main: "25 min @ 5:20-5:30/km (RPE 6-7) — just below threshold",
                    cooldown: "10 min easy jog + stretch",
                    purpose: "Lactate threshold development, teach body to clear lactate.",
                    zones: "Z3", rpe: "6-7"
                },

                // Thursday - REST
                {
                    day: 3, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest — office day. Focus on recovery nutrition.",
                    cooldown: "—", purpose: "Recovery from Wednesday's double-hard session.",
                    zones: "N/A", rpe: "0"
                },

                // Friday - Swim Drills + Strength B
                {
                    day: 4, sport: "swim", type: "drill", duration: 50, intensity: "easy", tss: 35,
                    desc: "Swim Drills + Build Sets",
                    warmup: "200m easy mixed stroke",
                    main: "8×50m drill (catch-up, fingertip drag, fist swim) + 4×100m build (easy→moderate)",
                    cooldown: "100m easy",
                    purpose: "Technique refinement, stroke efficiency, feel for water.",
                    zones: "Z1-Z2", rpe: "4-5"
                },
                {
                    day: 4, sport: "strength", type: "drill", duration: 40, intensity: "tempo", tss: 30,
                    desc: "Strength B: Push Dominant + Pull Accessory + Core",
                    warmup: "5 min dynamic warm-up",
                    main: "Seated DB Overhead Press 3×6-8 | Neutral Grip Cable Rows 3×8-10 | DB Chest Flyes 2×10-12 | Face Pulls 3×12-15 | Weighted Planks 3×45-60s",
                    cooldown: "5 min stretch",
                    purpose: "3D shoulder development, rotator cuff bulletproofing, core for tri.",
                    zones: "N/A", rpe: "8-9"
                },

                // Saturday - Long Ride
                {
                    day: 5, sport: "bike", type: "long", duration: 150, intensity: "easy", tss: 100,
                    desc: "Long Ride — Cycling Endurance",
                    warmup: "15 min easy spin",
                    main: "120 min Z2, practice nutrition every 30 min (gel/bottle), cadence 85-95 rpm",
                    cooldown: "15 min easy spin + stretch",
                    purpose: "Cycling endurance, nutrition strategy rehearsal, saddle adaptation.",
                    zones: "Z2", rpe: "4-5"
                },

                // Sunday - Hard: Long Run + Mobility
                {
                    day: 6, sport: "run", type: "long", duration: 75, intensity: "easy", tss: 60,
                    desc: "Long Run — Endurance Progression",
                    warmup: "10 min easy",
                    main: "60 min @ 5:55-6:10/km — practice mid-run fueling (gel at 40 min)",
                    cooldown: "5 min walk",
                    purpose: "Run endurance, fat oxidation, mental toughness training.",
                    zones: "Z2", rpe: "5"
                },
                {
                    day: 6, sport: "mobility", type: "recovery", duration: 20, intensity: "easy", tss: 5,
                    desc: "Foam Roll + Mobility",
                    warmup: "—",
                    main: "Hip 90/90, ankle dorsiflexion, thoracic rotation, foam roll full body",
                    cooldown: "—",
                    purpose: "Recovery before Monday rest, flexibility maintenance.",
                    zones: "Z1", rpe: "2"
                },
            ]
        },

        // ═══ PHASE 3: Specificity & Heat Acclimation (Weeks 13-17) ═══
        "Specificity & Heat Acclimation": {
            targetHours: 10,
            sessions: [
                // Monday - REST
                {
                    day: 0, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest — office day. Begin heat acclimation protocol (warm clothing during day).",
                    cooldown: "—", purpose: "Recovery. Begin sodium loading practice.",
                    zones: "N/A", rpe: "0"
                },

                // Tuesday - Swim Threshold + Strength Maintenance
                {
                    day: 1, sport: "swim", type: "threshold", duration: 55, intensity: "threshold", tss: 50,
                    desc: "Swim Threshold Sets",
                    warmup: "300m easy + 4×50m drill",
                    main: "6×150m @ 2:20-2:30/100m, 20s rest — push the pace. Sighting every 8 strokes.",
                    cooldown: "200m easy backstroke",
                    purpose: "Swim lactate tolerance, race-pace development, open-water skills.",
                    zones: "Z3-Z4", rpe: "6-7"
                },
                {
                    day: 1, sport: "strength", type: "easy", duration: 35, intensity: "easy", tss: 18,
                    desc: "Strength Maintenance: Upper Body",
                    warmup: "5 min dynamic",
                    main: "Pull-ups 3×6 | DB Bench 3×8 | Cable Row 3×10 | Face Pulls 3×12 | Plank 3×45s",
                    cooldown: "5 min stretch",
                    purpose: "Maintain muscle mass without overtraining. Reduced volume in build phase.",
                    zones: "N/A", rpe: "6-7"
                },

                // Wednesday - Hard: Bike Race-Pace + Run Intervals
                {
                    day: 2, sport: "bike", type: "tempo", duration: 75, intensity: "tempo", tss: 70,
                    desc: "Bike Race-Pace Simulation",
                    warmup: "15 min easy spin",
                    main: "45 min @ race effort with nutrition practice every 20 min. Practice sodium intake (500-1500mg/hr).",
                    cooldown: "15 min easy spin",
                    purpose: "Race simulation, nutrition timing, aerobar position endurance for Goa heat.",
                    zones: "Z3", rpe: "6-7"
                },
                {
                    day: 2, sport: "run", type: "intervals", duration: 55, intensity: "threshold", tss: 60,
                    desc: "VO2max Intervals",
                    warmup: "15 min easy + 4× strides",
                    main: "6×800m @ 4:40-4:50/km, 90s jog recovery — hard but controlled",
                    cooldown: "10 min easy jog",
                    purpose: "VO2max stimulus, running economy, speed endurance.",
                    zones: "Z4-Z5", rpe: "8"
                },

                // Thursday - REST
                {
                    day: 3, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest — office day. Analyze previous session data.",
                    cooldown: "—", purpose: "Recovery from Wednesday's race-pace double.",
                    zones: "N/A", rpe: "0"
                },

                // Friday - Swim Open-Water Sim + Light Strength
                {
                    day: 4, sport: "swim", type: "tempo", duration: 50, intensity: "tempo", tss: 45,
                    desc: "Open-Water Simulation — Sighting Drills",
                    warmup: "200m easy",
                    main: "8×100m with head-up sighting every 8 strokes + 4×50m draft practice. Practice race-pace 2:25-2:35/100m.",
                    cooldown: "100m easy",
                    purpose: "Open-water preparation, race-day skills for Miramar Beach swim.",
                    zones: "Z2-Z3", rpe: "5-6"
                },
                {
                    day: 4, sport: "strength", type: "easy", duration: 30, intensity: "easy", tss: 12,
                    desc: "Strength: Light Maintenance + Core",
                    warmup: "5 min dynamic",
                    main: "Band pull-aparts 3×15 | Goblet Squat 2×10 | Plank 3×45s | Side Plank 3×30s | Bird Dog 3×10/side",
                    cooldown: "5 min stretch",
                    purpose: "Core stability, movement maintenance, injury prevention only.",
                    zones: "N/A", rpe: "4"
                },

                // Saturday - Brick Session
                {
                    day: 5, sport: "bike", type: "brick", duration: 180, intensity: "tempo", tss: 150,
                    desc: "Brick: Bike → Run Transition",
                    warmup: "10 min easy spin",
                    main: "75 min ride (last 20 min @ race effort) → T2 quick change → 30 min run @ 5:50-6:00/km. Full nutrition plan rehearsal.",
                    cooldown: "5 min walk",
                    purpose: "Multi-sport fatigue adaptation, T2 practice, race simulation, GI testing.",
                    zones: "Z2-Z3", rpe: "6-7"
                },

                // Sunday - Long Run + Recovery
                {
                    day: 6, sport: "run", type: "long", duration: 85, intensity: "easy", tss: 70,
                    desc: "Long Run with Race Fueling",
                    warmup: "10 min easy",
                    main: "70 min @ 5:50-6:05/km, gel at 35 min and 60 min — practice full race nutrition",
                    cooldown: "5 min walk",
                    purpose: "Endurance, nutrition rehearsal for Goa heat, mental toughness.",
                    zones: "Z2", rpe: "5-6"
                },
                {
                    day: 6, sport: "mobility", type: "recovery", duration: 25, intensity: "easy", tss: 5,
                    desc: "Recovery + Mobility Session",
                    warmup: "—",
                    main: "Foam roll full body, 90/90 hip stretches, ankle mobility, thoracic rotation, cold immersion if available",
                    cooldown: "—",
                    purpose: "Recovery from race simulation week, prepare for next week.",
                    zones: "Z1", rpe: "2"
                },
            ]
        },

        // ═══ PHASE 4: Peak & Taper (Weeks 18-20) ═══
        "Peak & Taper": {
            targetHours: 6,
            sessions: [
                // Monday - REST
                {
                    day: 0, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest. Mental preparation, race logistics planning.",
                    cooldown: "—", purpose: "Full recovery. Glycogen supercompensation begins.",
                    zones: "N/A", rpe: "0"
                },

                // Tuesday - Easy Swim + Light Strength
                {
                    day: 1, sport: "swim", type: "easy", duration: 30, intensity: "easy", tss: 20,
                    desc: "Short Race-Pace Intervals",
                    warmup: "200m easy",
                    main: "4×100m @ race pace, 30s rest — crisp, fast strokes. Focus on feel.",
                    cooldown: "100m easy",
                    purpose: "Maintain water feel, neuromuscular sharpness without fatigue.",
                    zones: "Z2-Z3", rpe: "5"
                },
                {
                    day: 1, sport: "strength", type: "easy", duration: 25, intensity: "easy", tss: 10,
                    desc: "Strength: Very Light Maintenance",
                    warmup: "5 min dynamic",
                    main: "Band pull-aparts 2×15 | Push-ups 2×10 | Plank 2×30s | Bird Dog 2×8/side",
                    cooldown: "5 min stretch + mobility",
                    purpose: "Prevent detraining, keep neural pathways active. No fatigue.",
                    zones: "N/A", rpe: "3-4"
                },

                // Wednesday - Easy Bike with Openers
                {
                    day: 2, sport: "bike", type: "easy", duration: 45, intensity: "easy", tss: 30,
                    desc: "Easy Spin with Openers",
                    warmup: "15 min easy",
                    main: "20 min easy + 3×2 min @ race effort — feel the power, stay sharp",
                    cooldown: "10 min easy",
                    purpose: "Maintain cycling feel, race-pace neuromuscular recall.",
                    zones: "Z2", rpe: "4"
                },

                // Thursday - REST
                {
                    day: 3, sport: "rest", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "Rest Day",
                    warmup: "—", main: "Complete rest. Race week mental preparation.",
                    cooldown: "—", purpose: "Full recovery. Carb loading protocol.",
                    zones: "N/A", rpe: "0"
                },

                // Friday - Easy Run with Strides
                {
                    day: 4, sport: "run", type: "easy", duration: 30, intensity: "easy", tss: 18,
                    desc: "Easy Run with Strides",
                    warmup: "10 min easy",
                    main: "15 min easy + 4×30s strides (fast but relaxed)",
                    cooldown: "5 min walk",
                    purpose: "Keep legs loose, neuromuscular activation, mental calm.",
                    zones: "Z2", rpe: "4"
                },

                // Saturday - Mobility + Visualization
                {
                    day: 5, sport: "mobility", type: "recovery", duration: 20, intensity: "easy", tss: 5,
                    desc: "Mobility + Race Visualization",
                    warmup: "—",
                    main: "Foam roll, gentle stretches, 10 min race visualization (Miramar Beach swim → bike course → flat run → finish)",
                    cooldown: "—",
                    purpose: "Recovery + mental race preparation. Visualize every transition.",
                    zones: "Z1", rpe: "2"
                },

                // Sunday (Week 20 only) - RACE DAY
                {
                    day: 6, sport: "race", type: "recovery", duration: 0, intensity: "easy", tss: 0,
                    desc: "RACE DAY: IRONMAN 70.3 GOA",
                    warmup: "Race morning: light jog, dynamic stretch, practice swim strokes",
                    main: "1.9km SWIM (Miramar Beach) → 90km BIKE (525m elevation) → 21.1km RUN — Execute the plan!",
                    cooldown: "Celebrate. You're an Ironman.",
                    purpose: "RACE DAY — Trust the 20 weeks of preparation.",
                    zones: "All", rpe: "10"
                },
            ]
        },
    };

    // ── Workout Library (drag-and-drop templates) ────────────────
    const WORKOUT_LIBRARY = [
        { id: "lib-swim-easy", sport: "swim", type: "easy", duration: 30, intensity: "easy", desc: "Easy Swim", tss: 20, main: "Relaxed freestyle, technique focus" },
        { id: "lib-swim-drill", sport: "swim", type: "drill", duration: 45, intensity: "easy", desc: "Swim Drills", tss: 25, main: "Catch-up, fingertip drag, kick drills" },
        { id: "lib-swim-threshold", sport: "swim", type: "threshold", duration: 55, intensity: "threshold", desc: "Swim Threshold", tss: 50, main: "6×150m @ threshold pace" },
        { id: "lib-bike-easy", sport: "bike", type: "easy", duration: 45, intensity: "easy", desc: "Easy Spin", tss: 30, main: "Z2 spinning, smooth pedaling" },
        { id: "lib-bike-long", sport: "bike", type: "long", duration: 120, intensity: "easy", desc: "Long Ride", tss: 90, main: "Z2 endurance ride with nutrition" },
        { id: "lib-bike-tempo", sport: "bike", type: "tempo", duration: 60, intensity: "tempo", desc: "Bike Tempo", tss: 55, main: "3×8min tempo intervals" },
        { id: "lib-bike-brick", sport: "bike", type: "brick", duration: 110, intensity: "tempo", desc: "Brick Session", tss: 100, main: "Bike → Run transition" },
        { id: "lib-run-easy", sport: "run", type: "easy", duration: 40, intensity: "easy", desc: "Easy Run", tss: 30, main: "Z2 conversational pace" },
        { id: "lib-run-long", sport: "run", type: "long", duration: 75, intensity: "easy", desc: "Long Run", tss: 60, main: "Endurance run with mid-run fuel" },
        { id: "lib-run-tempo", sport: "run", type: "tempo", duration: 50, intensity: "tempo", desc: "Tempo Run", tss: 50, main: "25-30min at threshold pace" },
        { id: "lib-run-intervals", sport: "run", type: "intervals", duration: 50, intensity: "threshold", desc: "VO2max Intervals", tss: 60, main: "6×800m hard, 90s jog rest" },
        { id: "lib-strength-pull", sport: "strength", type: "drill", duration: 40, intensity: "tempo", desc: "Strength A: Pull Dominant", tss: 30, main: "Pull-ups, Incline Press, Rows, Laterals" },
        { id: "lib-strength-push", sport: "strength", type: "drill", duration: 40, intensity: "tempo", desc: "Strength B: Push Dominant", tss: 30, main: "OHP, Cable Rows, Flyes, Face Pulls, Planks" },
        { id: "lib-mobility", sport: "mobility", type: "recovery", duration: 20, intensity: "easy", desc: "Mobility & Foam Roll", tss: 5, main: "Full body foam roll, stretching" },
        { id: "lib-rest", sport: "rest", type: "recovery", duration: 0, intensity: "easy", desc: "Rest Day", tss: 0, main: "Complete rest" },
    ];

    // ── Nutrition Data ──────────────────────────────────────────
    const NUTRITION = {
        dailyTargets: {
            calories: "2800-3200 kcal (training days), 2200-2500 kcal (rest days)",
            protein: "1.7-2.2 g/kg bodyweight = 99-128g daily",
            carbs: "4-7 g/kg bodyweight = 232-406g daily",
            fat: "0.8-1.2 g/kg = 46-70g daily",
            water: "3-4 liters daily, more on training days",
        },
        preTraining: {
            twoToThreeHoursBefore: {
                title: "2-3 Hours Before Training",
                items: [
                    "Complex carbs: oatmeal, whole grain toast, brown rice",
                    "Moderate protein: eggs, yogurt, lean chicken",
                    "Low fat, low fiber to prevent GI distress",
                    "Example: 2 eggs + 2 toast + banana + honey",
                    "300-500 kcal, 60-80% carbs",
                ],
            },
            thirtyMinBefore: {
                title: "30 Minutes Before",
                items: [
                    "Simple carbs: banana, dates, energy bar",
                    "100-200 kcal max",
                    "250-500ml water with electrolytes",
                    "NEVER train fasted (per protocol)",
                ],
            },
        },
        duringTraining: {
            underSixtyMin: "Water only (250-500ml/hr)",
            sixtyToNinetyMin: "Water + electrolytes, optional 30g carbs",
            overNinetyMin: "60-90g carbohydrates per hour (gels, sports drink, dates)",
            sodium: "500-1500mg sodium per hour (critical for Goa heat)",
            hydration: "500-750ml fluid per hour, more in heat",
        },
        postTraining: {
            withinThirtyMin: {
                title: "Within 30 Minutes (Golden Window)",
                items: [
                    "3:1 or 4:1 carb-to-protein ratio",
                    "Example: Protein shake + banana + honey",
                    "40-60g carbs + 15-25g protein",
                    "Restores glycogen, initiates mTOR muscle repair",
                ],
            },
            withinTwoHours: {
                title: "Within 2 Hours — Full Meal",
                items: [
                    "Complete meal with all macros",
                    "Lean protein: chicken, fish, paneer, eggs",
                    "Complex carbs: rice, roti, sweet potato",
                    "Vegetables for micronutrients",
                    "Example: Chicken breast + rice + dal + sabzi",
                ],
            },
        },
        raceDayPlan: {
            morning: "Race morning (3hrs before): Oatmeal + banana + honey + coffee. 500ml water with electrolytes.",
            swim: "Nothing during 1.9km swim. Hydrate in T1 if needed.",
            bike: "60-90g carbs/hr: gels every 20-30 min + sports drink. 500-1500mg sodium/hr. 500-750ml fluid/hr.",
            run: "40-60g carbs/hr: cola + gels at aid stations. Continue sodium intake. Small water sips.",
        },
        supplements: [
            { name: "Whey Protein", dose: "25-30g post-workout", purpose: "Muscle preservation, mTOR activation" },
            { name: "Creatine Monohydrate", dose: "3-5g daily", purpose: "Power output, muscle cell hydration" },
            { name: "Electrolyte Mix", dose: "During sessions >60min", purpose: "Sodium, potassium, magnesium replacement" },
            { name: "Caffeine", dose: "3-6mg/kg before key sessions", purpose: "Performance enhancement, fat oxidation" },
            { name: "Vitamin D3", dose: "2000-4000 IU daily", purpose: "Bone health, immune function" },
            { name: "Omega-3 Fish Oil", dose: "1-2g EPA+DHA daily", purpose: "Anti-inflammatory, joint health" },
        ],
        faq: [
            {
                q: "Should I train fasted for fat adaptation?",
                a: "No. The protocol strictly prohibits fasted training. While fasted training can enhance fat oxidation, for a beginner-intermediate triathlete, the performance cost and muscle catabolism risk outweigh the benefits. Always consume at least simple carbs before training."
            },
            {
                q: "How much protein to prevent muscle loss during endurance training?",
                a: "1.7-2.2g per kg bodyweight daily. For a 58kg athlete, that's 99-128g protein. Distribute evenly across 4-5 meals. Prioritize leucine-rich sources: whey, eggs, chicken, fish. The endurance training volume creates a catabolic environment — protein intake is your primary defense against muscle loss."
            },
            {
                q: "What's the 3:1 carb-to-protein ratio post-workout?",
                a: "After endurance training, consume 3 parts carbohydrates to 1 part protein. Example: 60g carbs + 20g protein. This ratio optimizes glycogen resynthesis (you burned through your stores) while providing amino acids for the mTOR pathway that repairs damaged muscle fibers. A banana + protein shake is the simplest execution."
            },
            {
                q: "How should I fuel on rest days (Mon/Thu)?",
                a: "Rest days are NOT low-calorie days. Maintain caloric intake at maintenance or slight surplus. Keep protein high (1.7-2.2g/kg) to maximize the repair window. You can slightly reduce carbs since you're not training, but don't cut calories aggressively — your body is rebuilding."
            },
            {
                q: "Why 60-90g carbs per hour during long sessions?",
                a: "Your body can oxidize ~60g/hr from a single carb source (glucose). By using dual-source carbs (glucose + fructose), absorption increases to 90g/hr. For sessions over 90 minutes, this prevents bonking (glycogen depletion). Practice this in training to train your gut — GI distress on race day is the #1 DNF cause."
            },
            {
                q: "How do I prepare for Goa's heat and humidity?",
                a: "Goa race conditions involve extreme heat. Start heat acclimation 4-6 weeks before (Phase 3): train in warm conditions, wear extra layers. Increase sodium intake to 500-1500mg/hr during training. Pre-load with 1000mg sodium 2 hours before long sessions. Practice your full nutrition plan in hot conditions."
            },
            {
                q: "What should I eat the night before race day?",
                a: "Carb-loading dinner: familiar foods, high carb, moderate protein, LOW fiber and fat. Rice/pasta + chicken + simple sauce. Avoid spicy food, dairy, high-fiber vegetables, alcohol. Eat early (6-7 PM). Hydrate with electrolytes but don't overdrink. This is NOT the time to try new foods."
            },
            {
                q: "Do I need supplements or can I get everything from food?",
                a: "Food should be your primary nutrition source. However, for a triathlete training 10 hrs/week: Whey protein makes hitting 100g+ protein practical. Creatine (3-5g/day) has strong evidence for power output. Electrolyte mixes are essential for sessions >60 min. Caffeine is a proven ergogenic aid. Vitamin D and Omega-3 support recovery. Everything else is optional."
            },
            {
                q: "How do I know if I'm eating enough?",
                a: "Track these red flags for underfueling: (1) Resting heart rate elevated 5-7 bpm for 3+ days, (2) Inability to hit prescribed workout intensities, (3) Poor sleep quality, (4) Persistent muscle soreness beyond 48 hrs, (5) Getting sick frequently, (6) Mood changes/irritability. If these appear, increase calories by 300-500/day."
            },
            {
                q: "What about intermittent fasting during training?",
                a: "Not recommended. Your 10-hour training schedule requires consistent fueling across the day. The post-workout nutrition window is critical for glycogen restoration and muscle repair. IF would compromise recovery quality and training adaptation. Eat 4-5 balanced meals distributed throughout the day."
            },
        ],
    };

    // ── Plan Generation ──────────────────────────────────────────
    function generatePlan(startDate = PLAN_START) {
        const workouts = [];
        let currentDate = new Date(startDate);
        let weekNumber = 1;
        let globalId = 1;

        for (const phase of PHASES) {
            const template = WEEKLY_TEMPLATES[phase.name];
            if (!template) continue;

            for (let w = 0; w < phase.weeks; w++) {
                const isDeload = (w + 1) % 4 === 0 && phase.name !== "Peak & Taper";
                const weekStart = new Date(currentDate);
                const progressionFactor = Math.min(1.0 + (w / phase.weeks) * 0.12, 1.12);

                for (const session of template.sessions) {
                    const sessionDate = new Date(weekStart);
                    sessionDate.setDate(sessionDate.getDate() + session.day);

                    let dur = session.duration;
                    let tss = session.tss;

                    if (isDeload) {
                        dur = Math.round(dur * 0.6);
                        tss = Math.round(tss * 0.5);
                    } else if (session.sport !== "rest" && session.sport !== "race") {
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

    // ── Sample Completion Data ───────────────────────────────────
    // Week 1: Mon rest, Tue completed, Wed completed, Thu+ planned
    function addSampleCompletionData(workouts) {
        const today = new Date();
        const todayStr = formatDate(today);

        for (const w of workouts) {
            if (w.date <= todayStr && w.sport !== "rest" && w.sport !== "race") {
                w.status = "completed";
                w.actualDuration = Math.round(w.duration * (0.9 + Math.random() * 0.15));
                w.rpeActual = Math.floor(4 + Math.random() * 4);
                w.tssActual = Math.round(w.tssPlanned * (0.85 + Math.random() * 0.25));
                if (w.sport === "run") w.actualHR = Math.floor(135 + Math.random() * 25);
                else if (w.sport === "bike") w.actualHR = Math.floor(130 + Math.random() * 20);
                else if (w.sport === "swim") w.actualHR = Math.floor(125 + Math.random() * 25);
            }
        }
        return workouts;
    }

    // ── Metrics: CTL / ATL / TSB ─────────────────────────────────
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

    // ── Weekly Volume ────────────────────────────────────────────
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
        const past = workouts.filter(w => w.date <= today && w.sport !== "rest" && w.sport !== "race");
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

    // ── Dashboard Analytics ─────────────────────────────────────
    function calculateDashboardStats(workouts) {
        const today = formatDate(new Date());
        const all = workouts.filter(w => w.sport !== "rest" && w.sport !== "race");
        const past = all.filter(w => w.date <= today);
        const completed = past.filter(w => w.status === "completed" || w.status === "modified");
        const skipped = past.filter(w => w.status === "skipped");
        const planned = all.filter(w => w.date > today);

        // Total hours trained
        let totalMinutes = 0;
        completed.forEach(w => totalMinutes += (w.actualDuration || w.duration));

        // Mileage estimates based on pace/speed and duration
        let swimKm = 0, bikeKm = 0, runKm = 0;
        completed.forEach(w => {
            const dur = (w.actualDuration || w.duration);
            if (w.sport === "swim") swimKm += (dur / 60) * 1.5; // ~1.5 km/hr for beginner
            else if (w.sport === "bike") bikeKm += (dur / 60) * 22;  // ~22 km/hr
            else if (w.sport === "run") runKm += (dur / 60) * 9.5;   // ~9.5 km/hr (~6:20/km)
        });

        // Average pace/speed by sport
        const avgPace = {};
        ["swim", "bike", "run"].forEach(sport => {
            const sportWorkouts = completed.filter(w => w.sport === sport);
            if (sportWorkouts.length > 0) {
                const totalDur = sportWorkouts.reduce((s, w) => s + (w.actualDuration || w.duration), 0);
                avgPace[sport] = Math.round(totalDur / sportWorkouts.length);
            }
        });

        // Weekly plan vs actual
        const weeklyComparison = [];
        const weekNumbers = [...new Set(all.map(w => w.weekNumber))].sort((a, b) => a - b);
        weekNumbers.forEach(wn => {
            const weekWorkouts = all.filter(w => w.weekNumber === wn);
            const plannedMin = weekWorkouts.reduce((s, w) => s + w.duration, 0);
            const actualMin = weekWorkouts.reduce((s, w) => {
                if (w.status === "completed" || w.status === "modified") return s + (w.actualDuration || w.duration);
                return s;
            }, 0);
            const completedCount = weekWorkouts.filter(w => w.status === "completed" || w.status === "modified").length;
            const totalCount = weekWorkouts.filter(w => w.sport !== "rest" && w.sport !== "race").length;
            weeklyComparison.push({
                week: wn,
                phase: weekWorkouts[0]?.phase || "",
                plannedMin, actualMin,
                completedCount, totalCount,
                compliance: totalCount > 0 ? Math.round(completedCount / totalCount * 100) : 0,
            });
        });

        return {
            totalWorkouts: completed.length,
            totalPlanned: all.length,
            totalHours: Math.round(totalMinutes / 60 * 10) / 10,
            totalMinutes,
            completedCount: completed.length,
            skippedCount: skipped.length,
            plannedCount: planned.length,
            modifiedCount: completed.filter(w => w.status === "modified").length,
            swimKm: Math.round(swimKm * 10) / 10,
            bikeKm: Math.round(bikeKm * 10) / 10,
            runKm: Math.round(runKm * 10) / 10,
            avgPace,
            weeklyComparison,
            completionPct: past.length > 0 ? Math.round(completed.length / past.length * 100) : 0,
        };
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
        ATHLETE, HR_ZONES, RACE_NAME, RACE_DATE, PLAN_START, RACE_DISTANCES,
        SPORT_COLORS, SPORT_ICONS, INTENSITY_COLORS,
        PHASES, WORKOUT_LIBRARY, NUTRITION,
        generatePlan, addSampleCompletionData,
        calculateMetrics, calculateWeeklyVolume, calculateCompliance,
        calculateDashboardStats,
        getHRZone, formatDate, daysToRace,
        getCurrentPhase, getCurrentWeek, getWorkoutsForDate,
    };

})();
