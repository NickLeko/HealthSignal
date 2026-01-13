# app.py
import streamlit as st
from risk_engine import (
    Inputs,
    score_cardiometabolic,
    score_sleep_stress,
    score_msk_energy,
    pick_actions,
)

st.set_page_config(
    page_title="HealthSignal",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("HealthSignal — Preventive Snapshot (MVP)")
st.caption("Decision support only. Not diagnosis or treatment.")

# Presets

PRESETS = {
    "Custom": {},
    "Persona A (example)": {
        "age": 38,
        "sex": "Male",
        "height_cm": 183.0,
        "weight_kg": 95.0,
        "family_cvd": True,
        "family_t2d": True,
        "exercise_bucket": "LOW (0–1x/week)",
        "sleep_quality": "FRAGMENTED",
        "sleep_duration_bucket": "6-7",
        "alcohol_bucket": "8-14",
        "smoking_vaping": "NO",
        "known_htn": False,
        "known_prediabetes": False,
        "known_sleep_apnea": False,
        "bp_bucket": "SOMETIMES_HIGH",
        "ldl_bucket": "BORDERLINE",
        "a1c_bucket": "ELEVATED",
        "rhr_bucket": "UNKNOWN",
    },
    "Persona B (Healthy/Anxious)": {
        "age": 32,
        "sex": "Female",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "family_cvd": False,
        "family_t2d": False,
        "exercise_bucket": "HIGH (4+x/week)",
        "sleep_quality": "RESTFUL",
        "sleep_duration_bucket": "7+",
        "alcohol_bucket": "0-3",
        "smoking_vaping": "NO",
        "known_htn": False,
        "known_prediabetes": False,
        "known_sleep_apnea": False,
        "bp_bucket": "NORMAL",
        "ldl_bucket": "NORMAL",
        "a1c_bucket": "NORMAL",
        "rhr_bucket": "NORMAL",
    },
    "Persona C (High Risk)": {
        "age": 44,
        "sex": "Male",
        "height_cm": 178.0,
        "weight_kg": 110.0,
        "family_cvd": True,
        "family_t2d": True,
        "exercise_bucket": "LOW (0–1x/week)",
        "sleep_quality": "POOR",
        "sleep_duration_bucket": "<6",
        "alcohol_bucket": "15+",
        "smoking_vaping": "YES",
        "known_htn": True,
        "known_prediabetes": True,
        "known_sleep_apnea": False,
        "bp_bucket": "DIAGNOSED",
        "ldl_bucket": "HIGH",
        "a1c_bucket": "ELEVATED",
        "rhr_bucket": "ELEVATED",
    },
}

# Persistent state for report
if "generated" not in st.session_state:
    st.session_state.generated = False


# If user has never loaded anything, default to Persona A once.
if "initialized" not in st.session_state:
    for k, v in PRESETS["Persona A (example)"].items():
        st.session_state[k] = v
    st.session_state["initialized"] = True


def load_preset(preset_name: str) -> None:
    preset = PRESETS.get(preset_name, {})
    # Only set keys present in preset; don't wipe others.
    for k, v in preset.items():
        st.session_state[k] = v



# Sidebar Intake

st.sidebar.header("Intake")

preset_name = st.sidebar.selectbox("Preset", list(PRESETS.keys()), index=1)  # Persona A default
if st.sidebar.button("Load preset"):
    load_preset(preset_name)
    st.sidebar.success(f"Loaded: {preset_name}")

age = st.sidebar.number_input("Age", 18, 90, value=int(st.session_state.get("age", 38)), key="age")
sex = st.sidebar.selectbox(
    "Sex",
    ["Male", "Female"],
    index=["Male", "Female"].index(st.session_state.get("sex", "Male")),
    key="sex",
)

height_cm = st.sidebar.number_input(
    "Height (cm)",
    120.0,
    230.0,
    value=float(st.session_state.get("height_cm", 183.0)),
    key="height_cm",
)
weight_kg = st.sidebar.number_input(
    "Weight (kg)",
    35.0,
    250.0,
    value=float(st.session_state.get("weight_kg", 95.0)),
    key="weight_kg",
)

st.sidebar.subheader("Family history")
family_cvd = st.sidebar.checkbox(
    "Cardiovascular disease (HTN/heart attack/stroke)",
    value=bool(st.session_state.get("family_cvd", False)),
    key="family_cvd",
)
family_t2d = st.sidebar.checkbox(
    "Type 2 diabetes",
    value=bool(st.session_state.get("family_t2d", False)),
    key="family_t2d",
)

st.sidebar.subheader("Lifestyle")
exercise_options = ["LOW (0–1x/week)", "MID (2–3x/week)", "HIGH (4+x/week)"]
exercise_bucket = st.sidebar.selectbox(
    "Exercise frequency",
    exercise_options,
    index=exercise_options.index(st.session_state.get("exercise_bucket", exercise_options[0])),
    key="exercise_bucket",
)

sleep_options = ["RESTFUL", "FRAGMENTED", "POOR"]
sleep_quality = st.sidebar.selectbox(
    "Sleep quality",
    sleep_options,
    index=sleep_options.index(st.session_state.get("sleep_quality", "FRAGMENTED")),
    key="sleep_quality",
)

sleep_dur_options = ["UNKNOWN", "<6", "6-7", "7+"]
sleep_duration_bucket = st.sidebar.selectbox(
    "Avg sleep duration (optional)",
    sleep_dur_options,
    index=sleep_dur_options.index(st.session_state.get("sleep_duration_bucket", "UNKNOWN")),
    key="sleep_duration_bucket",
)

alcohol_options = ["0-3", "4-7", "8-14", "15+"]
alcohol_bucket = st.sidebar.selectbox(
    "Alcohol intake (drinks/week)",
    alcohol_options,
    index=alcohol_options.index(st.session_state.get("alcohol_bucket", "4-7")),
    key="alcohol_bucket",
)

smoke_options = ["UNKNOWN", "NO", "YES"]
smoking_vaping = st.sidebar.selectbox(
    "Smoking/vaping",
    smoke_options,
    index=smoke_options.index(st.session_state.get("smoking_vaping", "UNKNOWN")),
    key="smoking_vaping",
)

st.sidebar.subheader("Known conditions")
known_htn = st.sidebar.checkbox(
    "Hypertension (diagnosed)",
    value=bool(st.session_state.get("known_htn", False)),
    key="known_htn",
)
known_prediabetes = st.sidebar.checkbox(
    "Prediabetes (diagnosed)",
    value=bool(st.session_state.get("known_prediabetes", False)),
    key="known_prediabetes",
)
known_sleep_apnea = st.sidebar.checkbox(
    "Sleep apnea (diagnosed)",
    value=bool(st.session_state.get("known_sleep_apnea", False)),
    key="known_sleep_apnea",
)

st.sidebar.subheader("Optional signals")
bp_options = ["UNKNOWN", "NORMAL", "SOMETIMES_HIGH", "CONSISTENTLY_HIGH", "DIAGNOSED"]
bp_bucket = st.sidebar.selectbox(
    "Blood pressure trend (optional)",
    bp_options,
    index=bp_options.index(st.session_state.get("bp_bucket", "UNKNOWN")),
    key="bp_bucket",
)

ldl_options = ["UNKNOWN", "NORMAL", "BORDERLINE", "HIGH"]
ldl_bucket = st.sidebar.selectbox(
    "LDL category (optional)",
    ldl_options,
    index=ldl_options.index(st.session_state.get("ldl_bucket", "UNKNOWN")),
    key="ldl_bucket",
)

a1c_options = ["UNKNOWN", "NORMAL", "BORDERLINE", "ELEVATED"]
a1c_bucket = st.sidebar.selectbox(
    "A1C/glucose category (optional)",
    a1c_options,
    index=a1c_options.index(st.session_state.get("a1c_bucket", "UNKNOWN")),
    key="a1c_bucket",
)

rhr_options = ["UNKNOWN", "NORMAL", "ELEVATED"]
rhr_bucket = st.sidebar.selectbox(
    "Resting HR category (optional)",
    rhr_options,
    index=rhr_options.index(st.session_state.get("rhr_bucket", "UNKNOWN")),
    key="rhr_bucket",
)

st.sidebar.divider()

if st.sidebar.button("Generate report"):
    st.session_state.generated = True


if st.sidebar.button("Reset report"):
    st.session_state.generated = False



# Report Rendering

if st.session_state.generated:


    x = Inputs(
        age=age,
        sex=sex,
        height_cm=height_cm,
        weight_kg=weight_kg,
        family_cvd=family_cvd,
        family_t2d=family_t2d,
        exercise_bucket=exercise_bucket.split()[0],  # "LOW"/"MID"/"HIGH"
        sleep_quality=sleep_quality,
        sleep_duration_bucket=sleep_duration_bucket,
        alcohol_bucket=alcohol_bucket,
        smoking_vaping=smoking_vaping,
        known_htn=known_htn,
        known_prediabetes=known_prediabetes,
        known_sleep_apnea=known_sleep_apnea,
        bp_bucket=bp_bucket,
        ldl_bucket=ldl_bucket,
        a1c_bucket=a1c_bucket,
        rhr_bucket=rhr_bucket,
    )

    cardio_lvl, cardio_pts, cardio_reasons = score_cardiometabolic(x)
    sleep_lvl, sleep_pts, sleep_reasons = score_sleep_stress(x)
    msk_lvl, msk_pts, msk_reasons = score_msk_energy(x)
    actions = pick_actions(cardio_lvl, sleep_lvl, msk_lvl, x)

    # Debug toggle (appears after generate)
    debug = st.checkbox("Debug mode (show internals)")

    # Tabs-based report (avoids scrolling issues on desktop/mobile)
    tabs = st.tabs(
        ["Risk Summary", "Priority Actions", "Warning Signals", "Deprioritization", "Debug"]
    )

    with tabs[0]:
        st.markdown("## Risk Summary (5–10 year horizon)")
        st.markdown(
            f"**Cardiometabolic risk — {cardio_lvl}**  \n"
            f"Drivers: {', '.join(cardio_reasons) if cardio_reasons else 'insufficient data'}"
        )
        st.markdown(
            f"**Musculoskeletal / energy decline — {msk_lvl}**  \n"
            f"Drivers: {', '.join(msk_reasons) if msk_reasons else 'insufficient data'}"
        )
        st.markdown(
            f"**Sleep / stress load — {sleep_lvl}**  \n"
            f"Drivers: {', '.join(sleep_reasons) if sleep_reasons else 'insufficient data'}"
        )

    with tabs[1]:
        st.markdown("## Priority Actions (next 90 days)")

        for i, a in enumerate(actions, 1):
            st.markdown(
            f"**Action {i}: {a['title']}**  \n"
            f"Target: {a['target']}  \n"
            f"Why: {a['why']}"
        )

                

    with tabs[2]:
        st.markdown("## Early Warning Signals")
        st.markdown("- Blood pressure trending up (esp. consistent >130/85 at home)")
        st.markdown("- Waist/weight trend increasing over 2–3 months")
        st.markdown("- Sleep <6 hours on multiple nights/week")
        st.markdown("- Resting HR trending upward (if tracked)")

    with tabs[3]:
        st.markdown("## What you do **NOT** need to worry about right now")
        st.markdown(
            "- Continuous glucose monitors\n"
            "- Advanced lipid panels\n"
            "- VO₂ max testing\n"
            "- Supplement stacks\n"
            "- Extreme diets/biohacks"
        )

    with tabs[4]:
        st.markdown("## Debug")

    with st.container(height=600):
        st.write(
            {
                "cardiometabolic": {
                    "level": cardio_lvl,
                    "points": cardio_pts,
                    "drivers": cardio_reasons,
                },
                "sleep_stress": {
                    "level": sleep_lvl,
                    "points": sleep_pts,
                    "drivers": sleep_reasons,
                },
                "msk_energy": {
                    "level": msk_lvl,
                    "points": msk_pts,
                    "drivers": msk_reasons,
                },
                "actions_selected": [a["title"] for a in actions],
            }
        )
