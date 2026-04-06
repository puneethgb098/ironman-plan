"""Athlete Profile — View and edit athlete data, HR zones, goals."""
import streamlit as st
from pathlib import Path
from data.store import load_athlete, save_athlete
from data.models import AthleteProfile
from config import HR_ZONES, RACE_DATE

st.set_page_config(page_title="Profile | IronPlan", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# Athlete Profile")

athlete = load_athlete()

tab1, tab2, tab3 = st.tabs(["Profile", "HR Zones", "Goals and Benchmarks"])

with tab1:
    with st.form("profile_form"):
        st.markdown("### Demographics")
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Name", value=athlete.name)
            age = st.number_input("Age", min_value=10, max_value=80, value=athlete.age)
            gender = st.selectbox("Gender", ["Male", "Female"], index=0 if athlete.gender == "Male" else 1)
        with c2:
            height = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=float(athlete.height_cm))
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0, value=float(athlete.weight_kg), step=0.1)
            body_fat = st.number_input("Body Fat %", min_value=3.0, max_value=50.0, value=float(athlete.body_fat_pct), step=0.1)
        with c3:
            smm = st.number_input("Skeletal Muscle Mass (kg)", min_value=10.0, max_value=60.0, value=float(athlete.smm_kg), step=0.1)
            fat_mass = st.number_input("Fat Mass (kg)", min_value=1.0, max_value=60.0, value=float(athlete.fat_mass_kg), step=0.1)

        st.markdown("### Physiology")
        p1, p2, p3 = st.columns(3)
        with p1:
            resting_hr = st.number_input("Resting HR (morning)", min_value=35, max_value=100, value=int(athlete.resting_hr))
        with p2:
            max_hr = st.number_input("Max HR", min_value=140, max_value=220, value=int(athlete.max_hr))
        with p3:
            sleep_target = st.number_input("Sleep Target (hrs)", min_value=5.0, max_value=12.0, value=float(athlete.sleep_target_hrs), step=0.5)

        st.markdown("### Performance")
        pf1, pf2, pf3 = st.columns(3)
        with pf1:
            hm_time = st.number_input("Half Marathon (min)", min_value=60, max_value=240, value=int(athlete.hm_time_min))
            five_k = st.number_input("5K Time (min)", min_value=12, max_value=60, value=int(athlete.five_k_time_min))
        with pf2:
            easy_pace = st.text_input("Easy Run Pace (/km)", value=athlete.easy_run_pace)
            ftp = st.number_input("FTP (watts)", min_value=0, max_value=500, value=int(athlete.ftp_watts or 0))
        with pf3:
            swim_pace = st.text_input("Swim Pace /100m", value=athlete.swim_pace_100m or "N/A")

        st.markdown("### Nutrition Targets")
        n1, n2 = st.columns(2)
        with n1:
            daily_cal = st.number_input("Daily Calories", min_value=1500, max_value=5000, value=int(athlete.daily_calories))
        with n2:
            protein = st.number_input("Protein Target (g)", min_value=40, max_value=300, value=int(athlete.protein_target_g))

        if st.form_submit_button("Save Profile", type="primary"):
            updated = AthleteProfile(
                name=name, age=age, gender=gender, height_cm=height,
                weight_kg=weight, body_fat_pct=body_fat, smm_kg=smm,
                fat_mass_kg=fat_mass, resting_hr=resting_hr, max_hr=max_hr,
                sleep_target_hrs=sleep_target, hm_time_min=hm_time,
                five_k_time_min=five_k, easy_run_pace=easy_pace,
                ftp_watts=ftp if ftp > 0 else None,
                swim_pace_100m=swim_pace if swim_pace != "N/A" else None,
                daily_calories=daily_cal, protein_target_g=protein,
                goal=athlete.goal, race_date=athlete.race_date,
            )
            save_athlete(updated)
            st.success("Profile saved.")
            st.rerun()

with tab2:
    st.markdown("### Heart Rate Zones")
    st.markdown(f"Based on **Resting HR: {athlete.resting_hr}** and **Max HR: {athlete.max_hr}** (Karvonen method)")

    for zone_num, zone_info in HR_ZONES.items():
        low, high = athlete.hr_zone(zone_num)
        pct_low = int(zone_info["pct_range"][0] * 100)
        pct_high = int(zone_info["pct_range"][1] * 100)

        zc1, zc2, zc3, zc4 = st.columns([1, 1, 3, 2])
        with zc1:
            st.markdown(f"**Zone {zone_num}**")
        with zc2:
            st.caption(zone_info["name"])
        with zc3:
            bar_pct = float(high - low) / float(athlete.max_hr - athlete.resting_hr)
            st.progress(min(1.0, bar_pct))
        with zc4:
            st.markdown(f"**{low}–{high} bpm** ({pct_low}–{pct_high}%)")

    st.markdown("---")
    st.markdown("#### Run Pace Zones (estimated from HM)")
    hm_pace_sec = float(athlete.hm_time_min) * 60.0 / 21.1
    zones_pace = {
        "Recovery (Z1)": (hm_pace_sec * 1.25, hm_pace_sec * 1.40),
        "Aerobic (Z2)": (hm_pace_sec * 1.10, hm_pace_sec * 1.25),
        "Tempo (Z3)": (hm_pace_sec * 1.00, hm_pace_sec * 1.10),
        "Threshold (Z4)": (hm_pace_sec * 0.92, hm_pace_sec * 1.00),
        "VO2max (Z5)": (hm_pace_sec * 0.82, hm_pace_sec * 0.92),
    }
    for zone_name, (low_s, high_s) in zones_pace.items():
        low_m, low_r = divmod(int(low_s), 60)
        high_m, high_r = divmod(int(high_s), 60)
        st.markdown(f"**{zone_name}:** {high_m}:{high_r:02d} – {low_m}:{low_r:02d} /km")

with tab3:
    st.markdown("### Race Goal")
    st.markdown(f"**Target Race:** {athlete.goal}")
    st.markdown(f"**Race Date:** {athlete.race_date}")

    st.markdown("---")
    st.markdown("### Benchmark Tests")
    st.markdown("Schedule these tests to calibrate your training zones:")

    benchmarks = [
        {"test": "5K Time Trial", "when": "Every 6 weeks", "purpose": "Calibrate run zones, track fitness"},
        {"test": "20-min FTP Test", "when": "When power meter acquired", "purpose": "Set bike power zones"},
        {"test": "1000m Swim TT", "when": "Once you can swim 1000m", "purpose": "Set swim pace zones"},
        {"test": "Morning RHR (3-day avg)", "when": "Weekly", "purpose": "Track aerobic adaptation"},
        {"test": "Body Composition", "when": "Monthly", "purpose": "Track weight and muscle trends"},
    ]

    for b in benchmarks:
        with st.container(border=True):
            bc1, bc2 = st.columns([3, 1])
            with bc1:
                st.markdown(f"**{b['test']}**")
                st.caption(b["purpose"])
            with bc2:
                st.caption(b["when"])
