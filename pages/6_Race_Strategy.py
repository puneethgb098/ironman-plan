"""Race Strategy — Race-day plan, pacing, transitions, countdown."""
import streamlit as st
from pathlib import Path
from datetime import date
from data.store import load_athlete
from engine.calendar_engine import days_to_race
from config import RACE_DATE, RACE_NAME

st.set_page_config(page_title="Race Strategy | IronPlan", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# Race Strategy")

athlete = load_athlete()
dtrace = days_to_race(RACE_DATE)

st.metric("Days to Race", int(dtrace), delta=f"{RACE_NAME} — {RACE_DATE.strftime('%A, %B %d, %Y')}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Race Plan", "Pacing", "Transitions", "Contingencies"])

with tab1:
    st.markdown("### Target Race Time: 6:30 – 7:30")

    segments = [
        {"name": "Swim 1.9 km", "target": "45-55 min", "pace": "~2:30-2:55/100m",
         "strategy": "Survival pace. Start at back/side. Backstroke as backup. Sight every 6-8 strokes."},
        {"name": "T1", "target": "5 min", "pace": "—",
         "strategy": "Calm, don't rush. Remove wetsuit if worn. Helmet on first. Sip water."},
        {"name": "Bike 90 km", "target": "3:15-3:30", "pace": "23-25 km/h",
         "strategy": "Steady RPE 5-6. Don't chase. Eat every 20 min, drink every 15 min."},
        {"name": "T2", "target": "3 min", "pace": "—",
         "strategy": "Quick change. Gel + water before heading out."},
        {"name": "Run 21.1 km", "target": "2:10-2:30", "pace": "6:10-7:00/km",
         "strategy": "Walk out of T2. Settle km 3-10. Walk aid stations. Run-walk if needed."},
    ]

    for seg in segments:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{seg['name']}**")
                st.caption(seg["strategy"])
            with c2:
                st.metric("Target", seg["target"], delta=seg["pace"])

with tab2:
    st.markdown("### Detailed Pacing Strategy")

    st.markdown("#### Swim Pacing")
    st.markdown("""
    | Segment | Pace | Notes |
    |---------|------|-------|
    | First 200m | Easy, 3:00/100m | Establish breathing rhythm |
    | 200m - 1.5 km | Steady, 2:40-2:50/100m | Find rhythm, sight regularly |
    | Last 400m | Maintain, 2:40/100m | Prepare for T1 mentally |

    **If you panic:** Flip to backstroke. Float. Breathe. Resume when ready.
    """)

    st.markdown("#### Bike Pacing")
    st.markdown("""
    | Segment | Speed | Heart Rate | Notes |
    |---------|-------|------------|-------|
    | Km 0-10 | 20-22 km/h | Z2 (easy) | Spin up, settle in |
    | Km 10-70 | 23-25 km/h | Z2-Z3 | Race pace, eat every 20 min |
    | Km 70-85 | 23-25 km/h | Z2-Z3 | Maintain, last gel at km 80 |
    | Km 85-90 | 20 km/h | Z1-Z2 | Soft pedal, prepare for run |

    **RULE:** If you feel great, DO NOT go harder. Bank energy.
    """)

    st.markdown("#### Run Pacing")
    st.markdown("""
    | Segment | Pace | Strategy |
    |---------|------|----------|
    | Km 0-3 | 6:30-7:00/km | Walk/jog. Legs will feel terrible. Normal. |
    | Km 3-10 | 6:00-6:30/km | Settle in. Walk through every aid station. |
    | Km 10-16 | 6:15-6:45/km | The grind. Walk 30s, run 2 min if needed. |
    | Km 16-21 | Whatever it takes | Survival. Keep moving forward. |
    """)

with tab3:
    st.markdown("### Transition Strategy")

    st.markdown("#### T1: Swim to Bike")
    st.markdown("""
    1. **Exit water** — Stand, walk, don't run (you'll be dizzy)
    2. **Remove wetsuit** (if worn) en route to bike
    3. **At transition bag:**
       - Helmet ON first (mandatory before touching bike)
       - Sunglasses
       - Bike shoes if clip-in (or run to mount line in them)
       - Number belt
    4. **Mount bike** after the mount line
    5. **First sip of nutrition** within 5 min on bike
    """)

    st.markdown("#### T2: Bike to Run")
    st.markdown("""
    1. **Dismount** before the line
    2. **Rack bike**, helmet OFF last
    3. **Change shoes** to runners
    4. **Grab:** visor/cap, gel, water
    5. **Walk first 200m** — let blood redistribute to legs
    6. **Start slow jog** when legs feel ready
    """)

    st.markdown("#### Pre-Race Checklist")
    checklist = [
        "Race bib + timing chip",
        "Goggles (2 pairs — backup in transition bag)",
        "Tri suit / race kit",
        "Wetsuit (if allowed/owned)",
        "Bike — checked, tires pumped, gears working",
        "Helmet (mandatory)",
        "Bike shoes + socks",
        "Run shoes + socks",
        "Sunglasses",
        "Number belt",
        "Bike nutrition — 2 bottles + gels on frame",
        "Run nutrition — 2 gels in pocket",
        "Sunscreen",
        "Towel in transition area",
        "Body Glide / anti-chafe",
        "Spare tube + CO2 + tire levers + mini tool",
        "Post-race recovery food",
    ]
    for item in checklist:
        st.checkbox(item, key=f"check_{item}")

with tab4:
    st.markdown("### Contingency Plans")

    contingencies = [
        {"problem": "Swim panic", "severity": "Critical",
         "response": "Flip to backstroke. Float on back. Signal rescue kayak if needed. There is NO SHAME in this. Recover and resume."},
        {"problem": "Flat tire on bike", "severity": "Medium",
         "response": "Pull over safely. Use spare tube + CO2. Practice changing a flat before race day. Cost: ~8 min."},
        {"problem": "Cramps on bike", "severity": "Medium",
         "response": "Ease power, shift to an easy gear, stretch on the bike. Increase electrolyte intake. Sip don't gulp."},
        {"problem": "Bonk on run", "severity": "Critical",
         "response": "Walk immediately. Eat 2 gels back-to-back. Drink cola at next aid station. Wait 10 min, then try running slowly."},
        {"problem": "Extreme heat (>35C)", "severity": "Medium",
         "response": "Slow all paces by 10%. Extra water at every aid station. Pour water on head. Ice in hat."},
        {"problem": "Can't maintain run pace", "severity": "Normal",
         "response": "Switch to walk/run: run 4 min, walk 1 min. This is a legitimate race strategy used by many finishers."},
        {"problem": "Mechanical failure", "severity": "Critical",
         "response": "Flag a course marshal. Walk bike to nearest aid station. Ironman has mechanical support on course."},
        {"problem": "GI distress", "severity": "Medium",
         "response": "Reduce intake to water only. Walk for 5 min. Resume gentle sipping. Avoid gels temporarily, try solid food."},
    ]

    for c in contingencies:
        with st.expander(f"[{c['severity'].upper()}] {c['problem']}"):
            st.markdown(f"**Response:** {c['response']}")

    st.markdown("---")
    st.markdown("### Race Mantras")
    st.markdown("""
    - **Swim:** *"Relax. Breathe. Keep moving."*
    - **Bike:** *"Steady wins. Don't chase. Fuel the engine."*
    - **Run:** *"One aid station at a time."*
    - **Dark moments:** *"You trained for this. Forward is the only direction."*
    """)
