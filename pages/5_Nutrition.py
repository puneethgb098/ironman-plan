"""Nutrition — Daily targets, training fueling, and tracking."""
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
from datetime import date
from data.store import load_athlete, load_daily_logs, save_daily_log
from data.models import DailyLog

st.set_page_config(page_title="Nutrition | IronPlan", page_icon="🍎", layout="wide")
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.markdown("# 🍎 Nutrition")

athlete = load_athlete()
daily_logs = load_daily_logs()
today = date.today()

tab1, tab2, tab3 = st.tabs(["🎯 Daily Targets", "📝 Log Nutrition", "📊 Trends"])

with tab1:
    st.markdown("### Daily Nutrition Targets")
    st.markdown(f"Based on **{athlete.weight_kg} kg**, training for Ironman 70.3 in Bangalore conditions.")

    targets = {
        "Rest Day": {"cal": 2400, "protein": 110, "carbs": 250, "fat": 65, "water": 3.0},
        "Light Training": {"cal": 2800, "protein": 120, "carbs": 350, "fat": 70, "water": 3.5},
        "Hard / Long Day": {"cal": 3200, "protein": 120, "carbs": 420, "fat": 75, "water": 4.0},
    }

    cols = st.columns(3)
    for i, (day_type, macros) in enumerate(targets.items()):
        with cols[i]:
            colors = ["#E17055", "#0984E3", "#00B894"][i]
            st.markdown(f"""
            <div style="background:var(--bg-card); border-radius:12px; padding:20px; border-top:4px solid {colors};">
                <h4 style="text-align:center; margin-bottom:16px;">{day_type}</h4>
                <div style="text-align:center;">
                    <div style="font-size:2rem; font-weight:700; color:{colors};">{macros['cal']}</div>
                    <div style="font-size:0.8rem; color:var(--text-secondary);">CALORIES</div>
                </div>
                <div style="margin-top:16px; display:grid; grid-template-columns:1fr 1fr; gap:8px;">
                    <div style="text-align:center; padding:8px; background:var(--bg-secondary); border-radius:8px;">
                        <div style="font-weight:700; color:#E17055;">{macros['protein']}g</div>
                        <div style="font-size:0.7rem; color:var(--text-muted);">Protein</div>
                    </div>
                    <div style="text-align:center; padding:8px; background:var(--bg-secondary); border-radius:8px;">
                        <div style="font-weight:700; color:#FDCB6E;">{macros['carbs']}g</div>
                        <div style="font-size:0.7rem; color:var(--text-muted);">Carbs</div>
                    </div>
                    <div style="text-align:center; padding:8px; background:var(--bg-secondary); border-radius:8px;">
                        <div style="font-weight:700; color:#6C5CE7;">{macros['fat']}g</div>
                        <div style="font-size:0.7rem; color:var(--text-muted);">Fat</div>
                    </div>
                    <div style="text-align:center; padding:8px; background:var(--bg-secondary); border-radius:8px;">
                        <div style="font-weight:700; color:#0984E3;">{macros['water']}L</div>
                        <div style="font-size:0.7rem; color:var(--text-muted);">Water</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🍽️ Meal Timing Template")

    meals = [
        ("5:45 AM", "Pre-workout", "Banana + 10g whey in water + coffee", "~150 kcal"),
        ("7:00 AM", "Post-workout", "30g whey shake + 50g oats + fruit", "~350 kcal"),
        ("8:30 AM", "Breakfast", "3 idli/dosa + sambar + curd (25g protein)", "~500 kcal"),
        ("12:30 PM", "Lunch", "Rice + dal + sabzi + paneer (30g protein)", "~600 kcal"),
        ("4:00 PM", "Pre-PM snack", "Banana + peanut butter toast", "~250 kcal"),
        ("6:30 PM", "Post-PM session", "20g whey + fruit", "~200 kcal"),
        ("8:00 PM", "Dinner", "Roti + dal + sabzi + curd (25g protein)", "~550 kcal"),
    ]

    for time, name, content, cals in meals:
        st.markdown(f"""
        <div style="display:flex; align-items:center; padding:10px 16px; background:var(--bg-card); border-radius:8px; margin-bottom:6px;">
            <div style="width:80px; font-weight:600; color:#0984E3;">{time}</div>
            <div style="width:120px; font-weight:600;">{name}</div>
            <div style="flex:1; color:var(--text-secondary);">{content}</div>
            <div style="width:80px; text-align:right; color:var(--text-muted); font-size:0.85rem;">{cals}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Long Session Fueling (>90 min)")
    st.markdown("""
    - **60–80g carbs/hour** during exercise
    - Gel (25g carbs) every 25–30 min OR drink mix
    - 500–750 ml fluid/hour with electrolytes
    - Start fueling at 30 min mark, not when you feel hungry
    """)

with tab2:
    st.markdown("### 📝 Log Today's Nutrition")
    log_date = st.date_input("Date", value=today, key="nut_date")
    existing = daily_logs.get(str(log_date), DailyLog(date=str(log_date)))

    with st.form("nutrition_log"):
        nc1, nc2 = st.columns(2)
        with nc1:
            cals = st.number_input("Calories", min_value=0, max_value=6000, value=existing.calories_eaten or 0)
            protein_g = st.number_input("Protein (g)", min_value=0, max_value=400, value=existing.protein_g or 0)
        with nc2:
            water = st.number_input("Water (L)", min_value=0.0, max_value=8.0,
                                    value=existing.water_liters or 0.0, step=0.25)
            notes = st.text_area("Notes", value=existing.notes if existing.notes else "")

        if st.form_submit_button("💾 Save", type="primary"):
            existing.calories_eaten = cals
            existing.protein_g = protein_g
            existing.water_liters = water
            existing.notes = notes
            existing.date = str(log_date)
            save_daily_log(existing)
            st.success("✅ Nutrition logged!")

with tab3:
    st.markdown("### 📊 Nutrition Trends")
    logged = {k: v for k, v in daily_logs.items() if v.calories_eaten and v.calories_eaten > 0}

    if logged:
        dates = sorted(logged.keys())
        cals_data = [logged[d].calories_eaten or 0 for d in dates]
        protein_data = [logged[d].protein_g or 0 for d in dates]
        water_data = [logged[d].water_liters or 0 for d in dates]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=dates, y=cals_data, name="Calories", marker_color="#E17055"))
        fig.add_hline(y=2800, line_dash="dash", line_color="#0984E3", annotation_text="Target")
        fig.update_layout(
            template="plotly_dark", height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="", yaxis_title="Calories",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, width="stretch")

        fc1, fc2 = st.columns(2)
        with fc1:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=dates, y=protein_data, mode="lines+markers",
                                        name="Protein", line=dict(color="#E17055")))
            fig_p.add_hline(y=athlete.protein_target_g, line_dash="dash", line_color="#00B894",
                           annotation_text=f"Target: {athlete.protein_target_g}g")
            fig_p.update_layout(
                template="plotly_dark", height=250, title="Protein (g)",
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_p, width="stretch")

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
            st.plotly_chart(fig_w, width="stretch")
    else:
        st.info("Start logging nutrition data to see trends here.")
