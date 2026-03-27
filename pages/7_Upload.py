"""Upload & Import — Upload workout files, parse data, and import into the system."""
import streamlit as st
from pathlib import Path
from datetime import date
from data.store import load_workouts, add_workout, save_upload, load_uploads
from data.models import Workout, WorkoutUpload
from engine.parsers import parse_uploaded_file, parse_structured_text
from config import SPORT_ICONS, SPORTS, INTENSITY_TYPES

st.set_page_config(page_title="Upload | IronPlan", page_icon="📤", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# 📤 Upload & Import")
st.markdown("Import workout data from files, manual entry, or pasted text.")

tab1, tab2, tab3, tab4 = st.tabs(["📁 File Upload", "✏️ Manual Entry", "📋 Paste Text", "📜 Upload History"])

# === FILE UPLOAD ===
with tab1:
    st.markdown("### Upload Workout File")
    st.markdown("Supported formats: **CSV**, **TCX**, **JSON**, **FIT**")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "tcx", "json", "fit"],
        key="workout_upload",
        help="Upload a workout file in CSV, TCX, JSON, or FIT format",
    )

    if uploaded_file:
        file_content = uploaded_file.read()
        filename = uploaded_file.name

        with st.spinner("Parsing file..."):
            result = parse_uploaded_file(file_content, filename)

        # Show warnings
        if result["warnings"]:
            for warn in result["warnings"]:
                st.warning(f"⚠️ {warn}")

        # Show metrics
        if result["metrics"]:
            st.markdown("#### 📊 Parse Summary")
            met_cols = st.columns(len(result["metrics"]))
            for i, (key, val) in enumerate(result["metrics"].items()):
                with met_cols[i]:
                    st.metric(key.replace("_", " ").title(), str(val))

        # Preview workouts
        workouts_data = result.get("workouts", [])
        if workouts_data:
            st.markdown(f"#### 🏋️ {len(workouts_data)} Workout(s) Found")

            for i, w_data in enumerate(workouts_data):
                icon = SPORT_ICONS.get(w_data.get("sport", "run"), "❓")
                desc = w_data.get("description", "Uploaded workout")
                dur = w_data.get("actual_duration_min") or w_data.get("planned_duration_min", 0)
                sport = w_data.get("sport", "run")
                w_date = w_data.get("date", str(date.today()))

                with st.expander(f"{icon} {desc} — {sport} · {dur}min · {w_date}", expanded=i == 0):
                    # Allow editing before import
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        w_data["date"] = str(st.date_input("Date", value=date.fromisoformat(w_date),
                                                            key=f"up_date_{i}"))
                        w_data["sport"] = st.selectbox("Sport",
                                                        ["swim", "bike", "run", "strength", "mobility"],
                                                        index=["swim", "bike", "run", "strength", "mobility"].index(
                                                            sport) if sport in ["swim", "bike", "run", "strength",
                                                                                 "mobility"] else 2,
                                                        key=f"up_sport_{i}")
                        w_data["description"] = st.text_input("Description", value=desc, key=f"up_desc_{i}")
                    with ec2:
                        w_data["planned_duration_min"] = st.number_input("Duration (min)", value=dur,
                                                                         min_value=0, key=f"up_dur_{i}")
                        w_data["actual_duration_min"] = w_data["planned_duration_min"]
                        tss_val = w_data.get("tss_actual") or w_data.get("tss_planned", 0)
                        w_data["tss_planned"] = st.number_input("TSS", value=tss_val, min_value=0, key=f"up_tss_{i}")
                        w_data["tss_actual"] = w_data["tss_planned"]
                        w_data["intensity"] = st.selectbox("Intensity", INTENSITY_TYPES,
                                                            key=f"up_int_{i}")

                    # Extra metrics
                    if w_data.get("actual_hr_avg") or w_data.get("actual_distance_km"):
                        st.markdown("**Parsed Metrics:**")
                        extra_cols = st.columns(4)
                        with extra_cols[0]:
                            if w_data.get("actual_hr_avg"):
                                st.metric("Avg HR", f"{w_data['actual_hr_avg']} bpm")
                        with extra_cols[1]:
                            if w_data.get("actual_distance_km"):
                                st.metric("Distance", f"{w_data['actual_distance_km']} km")
                        with extra_cols[2]:
                            if w_data.get("avg_power_watts"):
                                st.metric("Avg Power", f"{w_data['avg_power_watts']} W")
                        with extra_cols[3]:
                            if w_data.get("elevation_m"):
                                st.metric("Elevation", f"{w_data['elevation_m']} m")

            st.markdown("---")
            if st.button("📥 Import All Workouts", type="primary", use_container_width=True):
                imported = 0
                for w_data in workouts_data:
                    w_data.setdefault("workout_type", w_data.get("intensity", "easy"))
                    w_data.setdefault("warmup", "")
                    w_data.setdefault("main_set", "")
                    w_data.setdefault("cooldown", "")
                    w_data.setdefault("purpose", "Imported workout")
                    w_data.setdefault("phase", "")
                    w_data.setdefault("week_number", 0)

                    workout = Workout.from_dict(w_data)
                    add_workout(workout)
                    imported += 1

                # Save upload record
                upload = WorkoutUpload(
                    filename=filename,
                    file_format=filename.rsplit(".", 1)[-1],
                    parsed_metrics=result["metrics"],
                    warnings=result["warnings"],
                    status="imported",
                )
                save_upload(upload)

                st.success(f"✅ {imported} workout(s) imported successfully!")
                st.balloons()
                st.rerun()
        else:
            if not result["warnings"]:
                st.info("No workout data found in the file.")

# === MANUAL ENTRY ===
with tab2:
    st.markdown("### ✏️ Log a Workout Manually")

    with st.form("manual_workout_form"):
        mc1, mc2 = st.columns(2)
        with mc1:
            m_date = st.date_input("Date", value=date.today())
            m_sport = st.selectbox("Sport", ["swim", "bike", "run", "strength", "mobility"])
            m_desc = st.text_input("Description", placeholder="e.g., Easy Z2 Run")
            m_intensity = st.selectbox("Intensity", INTENSITY_TYPES)
            m_type = st.selectbox("Workout Type", INTENSITY_TYPES)
        with mc2:
            m_dur = st.number_input("Duration (min)", min_value=0, max_value=600, value=60)
            m_dist = st.number_input("Distance (km)", min_value=0.0, max_value=300.0, value=0.0, step=0.1)
            m_tss = st.number_input("TSS", min_value=0, max_value=500, value=int(m_dur * 0.8))
            m_rpe = st.slider("RPE (1-10)", 1, 10, 5)
            m_hr = st.number_input("Avg HR (optional)", min_value=0, max_value=220, value=0)
            m_status = st.selectbox("Status", ["completed", "planned", "modified", "skipped"])

        st.markdown("#### Workout Structure")
        m_warmup = st.text_area("Warm-up", height=60)
        m_main = st.text_area("Main Set", height=80)
        m_cool = st.text_area("Cool-down", height=60)
        m_purpose = st.text_input("Purpose")
        m_notes = st.text_area("Notes", height=60)

        if st.form_submit_button("💾 Save Workout", type="primary"):
            workout = Workout(
                date=str(m_date),
                sport=m_sport,
                workout_type=m_type,
                planned_duration_min=m_dur,
                actual_duration_min=m_dur if m_status in ("completed", "modified") else None,
                planned_distance_km=m_dist if m_dist > 0 else None,
                actual_distance_km=m_dist if m_dist > 0 and m_status == "completed" else None,
                intensity=m_intensity,
                description=m_desc or f"{m_sport.capitalize()} workout",
                warmup=m_warmup,
                main_set=m_main,
                cooldown=m_cool,
                purpose=m_purpose,
                status=m_status,
                rpe=m_rpe if m_status in ("completed", "modified") else None,
                actual_hr_avg=m_hr if m_hr > 0 else None,
                notes=m_notes,
                tss_planned=m_tss,
                tss_actual=m_tss if m_status in ("completed", "modified") else None,
            )
            add_workout(workout)
            st.success(f"✅ Workout saved: {workout.description}")
            st.rerun()

# === PASTE TEXT ===
with tab3:
    st.markdown("### 📋 Paste Structured Workout Text")
    st.markdown("Paste a workout description and we'll parse it automatically.")

    pasted_text = st.text_area(
        "Workout text",
        height=200,
        placeholder="e.g.,\nTempo Run\n10 min warmup easy\n3x800m @4:40/km, 90s jog rest\n10 min cooldown",
    )

    if pasted_text and st.button("🔍 Parse Text", type="primary"):
        result = parse_structured_text(pasted_text)

        if result["warnings"]:
            for warn in result["warnings"]:
                st.warning(warn)

        for w_data in result.get("workouts", []):
            icon = SPORT_ICONS.get(w_data.get("sport", "run"), "❓")
            st.markdown(f"""
            <div class="workout-card {w_data.get('sport', 'run')}">
                <strong>{icon} {w_data.get('description', 'Parsed workout')}</strong>
                <span style="margin-left:12px; font-size:0.85rem;">
                    {w_data.get('sport', 'run').capitalize()} · {w_data.get('intensity', 'easy')} ·
                    {w_data.get('planned_duration_min', 0)}min
                </span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Edit before importing"):
                p1, p2 = st.columns(2)
                with p1:
                    w_data["date"] = str(st.date_input("Date", key="paste_date"))
                    w_data["sport"] = st.selectbox("Sport", ["swim", "bike", "run", "strength", "mobility"],
                                                    key="paste_sport")
                with p2:
                    w_data["planned_duration_min"] = st.number_input("Duration", value=w_data.get("planned_duration_min", 60),
                                                                      key="paste_dur")
                    w_data["intensity"] = st.selectbox("Intensity", INTENSITY_TYPES, key="paste_int")

            if st.button("📥 Import", key="import_paste"):
                w_data.setdefault("workout_type", w_data.get("intensity", "easy"))
                w_data.setdefault("warmup", "")
                w_data.setdefault("cooldown", "")
                w_data.setdefault("purpose", "Imported from text")
                w_data.setdefault("phase", "")
                w_data.setdefault("week_number", 0)
                w_data.setdefault("tss_planned", int(w_data.get("planned_duration_min", 60) * 0.8))

                workout = Workout.from_dict(w_data)
                add_workout(workout)
                st.success("✅ Workout imported!")
                st.rerun()

# === UPLOAD HISTORY ===
with tab4:
    st.markdown("### 📜 Upload History")
    uploads = load_uploads()

    if uploads:
        for u in reversed(uploads):
            status_color = "#00B894" if u.status == "imported" else "#FDCB6E" if u.status == "pending" else "#D63031"
            st.markdown(f"""
            <div style="padding:10px 16px; border-left:3px solid {status_color}; margin-bottom:6px;
                background:var(--bg-card); border-radius:0 8px 8px 0;">
                <div style="display:flex; justify-content:space-between;">
                    <strong>{u.filename}</strong>
                    <span style="color:{status_color}; font-size:0.85rem;">{u.status.upper()}</span>
                </div>
                <div style="font-size:0.78rem; color:var(--text-muted);">
                    {u.file_format.upper()} · {u.upload_date[:16]}
                </div>
                {f'<div style="font-size:0.72rem; color:var(--text-muted);">{u.parsed_metrics}</div>' if u.parsed_metrics else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No uploads yet. Use the File Upload tab to import workout data.")
