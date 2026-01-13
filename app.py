import streamlit as st
from risk_engine import Inputs, score_cardiometabolic, score_sleep_stress, score_msk_energy, pick_actions

st.set_page_config(page_title="HealthTriageAI", layout="centered")
st.title("HealthTriageAI — Preventive Snapshot (MVP)")
st.caption("Decision support only. Not diagnosis or treatment.")

with st.form("intake"):
    age = st.number_input("Age", 18, 90, 38)
    sex = st.selectbox("Sex", ["Male", "Female"])

    col1, col2 = st.columns(2)
    with col1:
        height_cm = st.number_input("Height (cm)", 120.0, 230.0, 183.0)
    with col2:
        weight_kg = st.number_input("Weight (kg)", 35.0, 250.0, 95.0)

    st.subheader("Family history")
    family_cvd = st.checkbox("Cardiovascular disease (HTN/heart attack/stroke)")
    family_t2d = st.checkbox("Type 2 diabetes")

    st.subheader("Lifestyle")
    exercise_bucket = st.selectbox("Exercise frequency", ["LOW (0–1x/week)", "MID (2–3x/week)", "HIGH (4+x/week)"])
    sleep_quality = st.selectbox("Sleep quality", ["RESTFUL", "FRAGMENTED", "POOR"])
    sleep_duration_bucket = st.selectbox("Average sleep duration (optional)", ["UNKNOWN", "<6", "6-7", "7+"])
    alcohol_bucket = st.selectbox("Alcohol intake (drinks/week)", ["0-3", "4-7", "8-14", "15+"])
    smoking_vaping = st.selectbox("Smoking/vaping", ["UNKNOWN", "NO", "YES"])

    st.subheader("Known conditions")
    known_htn = st.checkbox("Hypertension (diagnosed)")
    known_prediabetes = st.checkbox("Prediabetes (diagnosed)")
    known_sleep_apnea = st.checkbox("Sleep apnea (diagnosed)")

    st.subheader("Optional signals")
    bp_bucket = st.selectbox("Blood pressure trend (optional)", ["UNKNOWN", "NORMAL", "SOMETIMES_HIGH", "CONSISTENTLY_HIGH", "DIAGNOSED"])
    ldl_bucket = st.selectbox("LDL category (optional)", ["UNKNOWN", "NORMAL", "BORDERLINE", "HIGH"])
    a1c_bucket = st.selectbox("A1C/glucose category (optional)", ["UNKNOWN", "NORMAL", "BORDERLINE", "ELEVATED"])
    rhr_bucket = st.selectbox("Resting HR category (optional)", ["UNKNOWN", "NORMAL", "ELEVATED"])

    submitted = st.form_submit_button("Generate report")

if submitted:
    x = Inputs(
        age=age, sex=sex, height_cm=height_cm, weight_kg=weight_kg,
        family_cvd=family_cvd, family_t2d=family_t2d,
        exercise_bucket=exercise_bucket.split()[0],
        sleep_quality=sleep_quality,
        sleep_duration_bucket=sleep_duration_bucket,
        alcohol_bucket=alcohol_bucket,
        smoking_vaping=smoking_vaping,
        known_htn=known_htn, known_prediabetes=known_prediabetes, known_sleep_apnea=known_sleep_apnea,
        bp_bucket=bp_bucket, ldl_bucket=ldl_bucket, a1c_bucket=a1c_bucket, rhr_bucket=rhr_bucket
    )

    cardio_lvl, cardio_pts, cardio_reasons = score_cardiometabolic(x)
    sleep_lvl, sleep_pts, sleep_reasons = score_sleep_stress(x)
    msk_lvl, msk_pts, msk_reasons = score_msk_energy(x)
    actions = pick_actions(cardio_lvl, sleep_lvl, msk_lvl, x)

    st.markdown("## Risk Summary (5–10 year horizon)")
    st.markdown(f"**Cardiometabolic risk — {cardio_lvl}**  \nDrivers: {', '.join(cardio_reasons) if cardio_reasons else 'insufficient data'}")
    st.markdown(f"**Musculoskeletal / energy decline — {msk_lvl}**  \nDrivers: {', '.join(msk_reasons) if msk_reasons else 'insufficient data'}")
    st.markdown(f"**Sleep / stress load — {sleep_lvl}**  \nDrivers: {', '.join(sleep_reasons) if sleep_reasons else 'insufficient data'}")

    st.markdown("## Priority Actions (next 90 days)")
    for i, a in enumerate(actions, 1):
        st.markdown(f"**Action {i}: {a['title']}**  \nTarget: {a['target']}  \nWhy: {a['why']}")

    st.markdown("## Early Warning Signals")
    st.markdown("- Blood pressure trending up (esp. consistent >130/85 at home)")
    st.markdown("- Waist/weight trend increasing over 2–3 months")
    st.markdown("- Sleep <6 hours on multiple nights/week")
    st.markdown("- Resting HR trending upward (if tracked)")

    st.markdown("## What you do **NOT** need to worry about right now")
    st.markdown("- Continuous glucose monitors\n- Advanced lipid panels\n- VO₂ max testing\n- Supplement stacks\n- Extreme diets/biohacks")

    st.caption("Decision support only. Not diagnosis or treatment. Seek clinical care for concerning symptoms or major changes.")
