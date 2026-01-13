import streamlit as st
from risk_engine import Inputs, score_cardiometabolic, score_sleep_stress, score_msk_energy, pick_actions

st.set_page_config(page_title="HealthSignal", layout="centered", initial_sidebar_state="expanded")
st.title("HealthSignal — Preventive Snapshot (MVP)")
st.caption("Decision support only. Not diagnosis or treatment.")

st.sidebar.header("Intake")

age = st.sidebar.number_input("Age", 18, 90, 38)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])

height_cm = st.sidebar.number_input("Height (cm)", 120.0, 230.0, 183.0)
weight_kg  = st.sidebar.number_input("Weight (kg)", 35.0, 250.0, 95.0)

st.sidebar.subheader("Family history")
family_cvd = st.sidebar.checkbox("Cardiovascular disease (HTN/heart attack/stroke)")
family_t2d = st.sidebar.checkbox("Type 2 diabetes")

st.sidebar.subheader("Lifestyle")
exercise_bucket = st.sidebar.selectbox("Exercise frequency", ["LOW (0–1x/week)", "MID (2–3x/week)", "HIGH (4+x/week)"])
sleep_quality = st.sidebar.selectbox("Sleep quality", ["RESTFUL", "FRAGMENTED", "POOR"])
sleep_duration_bucket = st.sidebar.selectbox("Avg sleep duration (optional)", ["UNKNOWN", "<6", "6-7", "7+"])
alcohol_bucket = st.sidebar.selectbox("Alcohol intake (drinks/week)", ["0-3", "4-7", "8-14", "15+"])
smoking_vaping = st.sidebar.selectbox("Smoking/vaping", ["UNKNOWN", "NO", "YES"])

st.sidebar.subheader("Known conditions")
known_htn = st.sidebar.checkbox("Hypertension (diagnosed)")
known_prediabetes = st.sidebar.checkbox("Prediabetes (diagnosed)")
known_sleep_apnea = st.sidebar.checkbox("Sleep apnea (diagnosed)")

st.sidebar.subheader("Optional signals")
bp_bucket = st.sidebar.selectbox("Blood pressure trend (optional)", ["UNKNOWN", "NORMAL", "SOMETIMES_HIGH", "CONSISTENTLY_HIGH", "DIAGNOSED"])
ldl_bucket = st.sidebar.selectbox("LDL category (optional)", ["UNKNOWN", "NORMAL", "BORDERLINE", "HIGH"])
a1c_bucket = st.sidebar.selectbox("A1C/glucose category (optional)", ["UNKNOWN", "NORMAL", "BORDERLINE", "ELEVATED"])
rhr_bucket = st.sidebar.selectbox("Resting HR category (optional)", ["UNKNOWN", "NORMAL", "ELEVATED"])

generate = st.sidebar.button("Generate report")

if generate:
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

        #DEBUG BLOCK 
    debug = st.checkbox("Debug mode (show internals)")
    if debug:
        st.write({
            "cardiometabolic": {
                "level": cardio_lvl,
                "points": cardio_pts,
                "drivers": cardio_reasons
            },
            "sleep_stress": {
                "level": sleep_lvl,
                "points": sleep_pts,
                "drivers": sleep_reasons
            },
            "msk_energy": {
                "level": msk_lvl,
                "points": msk_pts,
                "drivers": msk_reasons
            },
            "actions_selected": [a["title"] for a in actions]
        })


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
