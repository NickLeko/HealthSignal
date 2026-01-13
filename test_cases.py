from risk_engine import Inputs, score_cardiometabolic, score_sleep_stress, score_msk_energy, pick_actions

def run_case(name, x):
    cardio = score_cardiometabolic(x)
    sleep = score_sleep_stress(x)
    msk = score_msk_energy(x)
    actions = pick_actions(cardio[0], sleep[0], msk[0], x)

    print(f"\n{name}")
    print("Cardio:", cardio)
    print("Sleep:", sleep)
    print("MSK:", msk)
    print("Actions:", [a["title"] for a in actions])

# Persona A (your main case)
persona_a = Inputs(
    age=38, sex="Male", height_cm=183, weight_kg=95,
    family_cvd=True, family_t2d=True,
    exercise_bucket="LOW",
    sleep_quality="FRAGMENTED",
    sleep_duration_bucket="6-7",
    alcohol_bucket="8-14",
    smoking_vaping="NO",
    known_htn=False,
    known_prediabetes=False,
    known_sleep_apnea=False,
    bp_bucket="SOMETIMES_HIGH",
    ldl_bucket="BORDERLINE",
    a1c_bucket="ELEVATED",
    rhr_bucket="UNKNOWN"
)

# Healthy but anxious
persona_b = Inputs(
    age=32, sex="Female", height_cm=165, weight_kg=60,
    family_cvd=False, family_t2d=False,
    exercise_bucket="HIGH",
    sleep_quality="RESTFUL",
    sleep_duration_bucket="7+",
    alcohol_bucket="0-3",
    smoking_vaping="NO",
    known_htn=False,
    known_prediabetes=False,
    known_sleep_apnea=False,
    bp_bucket="NORMAL",
    ldl_bucket="NORMAL",
    a1c_bucket="NORMAL",
    rhr_bucket="NORMAL"
)

# Obvious high-risk
persona_c = Inputs(
    age=44, sex="Male", height_cm=178, weight_kg=110,
    family_cvd=True, family_t2d=True,
    exercise_bucket="LOW",
    sleep_quality="POOR",
    sleep_duration_bucket="<6",
    alcohol_bucket="15+",
    smoking_vaping="YES",
    known_htn=True,
    known_prediabetes=True,
    known_sleep_apnea=False,
    bp_bucket="DIAGNOSED",
    ldl_bucket="HIGH",
    a1c_bucket="ELEVATED",
    rhr_bucket="ELEVATED"
)

if __name__ == "__main__":
    run_case("Persona A", persona_a)
    run_case("Persona B (Healthy/Anxious)", persona_b)
    run_case("Persona C (High Risk)", persona_c)
