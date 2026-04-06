"""Nutrition — Daily targets, training fueling, tracking, and daily completion."""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
from datetime import date
from data.store import load_athlete, load_daily_logs, save_daily_log, save_daily_completion, get_daily_completion
from data.models import DailyLog, DailyCompletion

st.set_page_config(page_title="Nutrition | IronPlan", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# Nutrition")

athlete = load_athlete()
daily_logs = load_daily_logs()
today = date.today()

tab1, tab2, tab3 = st.tabs(["Daily Targets", "Log Nutrition", "Trends"])

with tab1:
    st.markdown("### Daily Nutrition Targets")
    st.markdown(f"Based on **{athlete.weight_kg} kg**, training for Ironman 70.3.")

    targets = {
        "Rest Day": {"cal": 2400, "protein": 110, "carbs": 250, "fat": 65, "water": 3.0},
        "Light Training": {"cal": 2800, "protein": 120, "carbs": 350, "fat": 70, "water": 3.5},
        "Hard / Long Day": {"cal": 3200, "protein": 120, "carbs": 420, "fat": 75, "water": 4.0},
    }

    cols = st.columns(3)
    for i, (day_type, macros) in enumerate(targets.items()):
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"#### {day_type}")
                st.metric("Calories", macros["cal"])
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.metric("Protein", f"{macros['protein']}g")
                    st.metric("Fat", f"{macros['fat']}g")
                with mc2:
                    st.metric("Carbs", f"{macros['carbs']}g")
                    st.metric("Water", f"{macros['water']}L")

    st.markdown("---")
    st.markdown("### Meal Timing Template")

    meals = [
        ("5:45 AM", "Pre-workout", "Banana + 10g whey in water + coffee", "~150 kcal"),
        ("7:00 AM", "Post-workout", "30g whey shake + 50g oats + fruit", "~350 kcal"),
        ("8:30 AM", "Breakfast", "3 idli/dosa + sambar + curd (25g protein)", "~500 kcal"),
        ("12:30 PM", "Lunch", "Rice + dal + sabzi + paneer (30g protein)", "~600 kcal"),
        ("4:00 PM", "Pre-PM snack", "Banana + peanut butter toast", "~250 kcal"),
        ("6:30 PM", "Post-PM session", "20g whey + fruit", "~200 kcal"),
        ("8:00 PM", "Dinner", "Roti + dal + sabzi + curd (25g protein)", "~550 kcal"),
    ]

    import pandas as pd
    meal_df = pd.DataFrame(meals, columns=["Time", "Meal", "Content", "Calories"])
    st.dataframe(meal_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Long Session Fueling (>90 min)")
    st.markdown("""
    - **60-80g carbs/hour** during exercise
    - Gel (25g carbs) every 25-30 min OR drink mix
    - 500-750 ml fluid/hour with electrolytes
    - Start fueling at 30 min mark, not when you feel hungry
    """)

with tab2:
    st.markdown("### Log Today's Nutrition")
    log_date = st.date_input("Date", value=today, key="nut_date")
    log_str = str(log_date)
    existing = daily_logs.get(log_str, DailyLog(date=log_str))

    # Nutrition completion toggle
    dc = get_daily_completion(log_str)
    n_done = st.checkbox("Nutrition targets met today", value=dc.nutrition_done, key=f"nut_dc_{log_str}")
    if n_done != dc.nutrition_done:
        save_daily_completion(DailyCompletion(
            date=log_str, training_done=dc.training_done, nutrition_done=n_done,
        ))
        st.success("Nutrition completion updated.")

    with st.form("nutrition_log"):
        nc1, nc2 = st.columns(2)
        with nc1:
            cals = st.number_input("Calories", min_value=0, max_value=6000, value=int(existing.calories_eaten or 0))
            protein_g = st.number_input("Protein (g)", min_value=0, max_value=400, value=int(existing.protein_g or 0))
        with nc2:
            water = st.number_input("Water (L)", min_value=0.0, max_value=8.0,
                                    value=float(existing.water_liters or 0.0), step=0.25)
            notes = st.text_area("Notes", value=existing.notes if existing.notes else "")

        if st.form_submit_button("Save", type="primary"):
            existing.calories_eaten = cals
            existing.protein_g = protein_g
            existing.water_liters = water
            existing.notes = notes
            existing.date = log_str
            save_daily_log(existing)
            st.success("Nutrition logged.")

with tab3:
    st.markdown("### Nutrition Trends")
    logged = {k: v for k, v in daily_logs.items() if v.calories_eaten and v.calories_eaten > 0}

    if logged:
        dates = sorted(logged.keys())
        cals_data = [int(logged[d].calories_eaten or 0) for d in dates]
        protein_data = [int(logged[d].protein_g or 0) for d in dates]
        water_data = [float(logged[d].water_liters or 0) for d in dates]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=dates, y=cals_data, name="Calories", marker_color="#E17055"))
        fig.add_hline(y=2800, line_dash="dash", line_color="#0984E3", annotation_text="Target")
        fig.update_layout(
            template="plotly_dark", height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="", yaxis_title="Calories",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        fc1, fc2 = st.columns(2)
        with fc1:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=dates, y=protein_data, mode="lines+markers",
                                        name="Protein", line=dict(color="#E17055")))
            fig_p.add_hline(y=int(athlete.protein_target_g), line_dash="dash", line_color="#00B894",
                           annotation_text=f"Target: {athlete.protein_target_g}g")
            fig_p.update_layout(
                template="plotly_dark", height=250, title="Protein (g)",
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_p, use_container_width=True)

        with fc2:
            fig_w = go.Figure()
            fig_w.add_trace(go.Scatter(x=dates, y=water_data, mode="lines+markers",
                                        name="Water", line=dict(color="#0984E3")))
            fig_w.add_hline(y=3.5, line_dash="dash", line_color="#00B894", annotation_text="Target: 3.5L")
            fig_w.update_layout(
                template="plotly_dark", height=250, title="Water (L)",
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info("Start logging nutrition data to see trends here.")
