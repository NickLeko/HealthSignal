from dataclasses import dataclass
from typing import Dict, List, Tuple

Likelihood = str  # "Low" | "Moderate" | "High"

@dataclass
class Inputs:
    age: int
    sex: str  # "Male" | "Female"
    height_cm: float
    weight_kg: float

    family_cvd: bool
    family_t2d: bool

    exercise_bucket: str  # "LOW" | "MID" | "HIGH"
    sleep_quality: str    # "RESTFUL" | "FRAGMENTED" | "POOR"
    sleep_duration_bucket: str  # "<6" | "6-7" | "7+" | "UNKNOWN"
    alcohol_bucket: str   # "0-3" | "4-7" | "8-14" | "15+"

    smoking_vaping: str   # "YES" | "NO" | "UNKNOWN"

    known_htn: bool
    known_prediabetes: bool
    known_sleep_apnea: bool

    bp_bucket: str        # "UNKNOWN" | "NORMAL" | "SOMETIMES_HIGH" | "CONSISTENTLY_HIGH" | "DIAGNOSED"
    ldl_bucket: str       # "UNKNOWN" | "NORMAL" | "BORDERLINE" | "HIGH"
    a1c_bucket: str       # "UNKNOWN" | "NORMAL" | "BORDERLINE" | "ELEVATED"
    rhr_bucket: str       # "UNKNOWN" | "NORMAL" | "ELEVATED"


def excess_weight_signal(height_cm: float, weight_kg: float) -> bool:
    # Internal-only heuristic; do not display BMI.
    h_m = height_cm / 100.0
    if h_m <= 0:
        return False
    bmi = weight_kg / (h_m ** 2)
    return bmi >= 27.0  # conservative "excess weight signal"


def level_from_points(points: int, low_max: int, mod_max: int) -> Likelihood:
    if points <= low_max:
        return "Low"
    if points <= mod_max:
        return "Moderate"
    return "High"


def score_cardiometabolic(x: Inputs) -> Tuple[Likelihood, int, List[str]]:
    p = 0
    reasons: List[str] = []
    ews = excess_weight_signal(x.height_cm, x.weight_kg)

    # Major
    if x.known_htn:
        p += 2; reasons.append("known hypertension")
    if x.known_prediabetes:
        p += 2; reasons.append("known prediabetes")
    if x.a1c_bucket == "ELEVATED":
        p += 2; reasons.append("elevated A1C/glucose category")
    if x.bp_bucket in {"SOMETIMES_HIGH", "CONSISTENTLY_HIGH", "DIAGNOSED"}:
        p += 2; reasons.append("blood pressure trend category")

    # Moderate
    if x.family_cvd:
        p += 1; reasons.append("family history of cardiovascular disease")
    if x.family_t2d:
        p += 1; reasons.append("family history of type 2 diabetes")
    if ews:
        p += 1; reasons.append("excess weight signal")
    if x.exercise_bucket == "LOW":
        p += 1; reasons.append("low exercise consistency")
    if x.ldl_bucket in {"BORDERLINE", "HIGH"}:
        p += 1; reasons.append("borderline/high LDL category")
    if x.alcohol_bucket in {"8-14", "15+"}:
        p += 1; reasons.append("higher alcohol exposure")
    if x.rhr_bucket == "ELEVATED":
        p += 1; reasons.append("elevated resting heart rate category")

    override = x.known_htn and (x.known_prediabetes or x.a1c_bucket == "ELEVATED")
    level = "High" if (override or p >= 5) else level_from_points(p, low_max=1, mod_max=4)
    return level, p, reasons[:3]


def score_sleep_stress(x: Inputs) -> Tuple[Likelihood, int, List[str]]:
    p = 0
    reasons: List[str] = []

    # Major
    if x.sleep_quality == "POOR":
        p += 2; reasons.append("poor sleep quality")
    if x.sleep_duration_bucket == "<6":
        p += 2; reasons.append("short sleep duration")
    if x.known_sleep_apnea:
        p += 2; reasons.append("known sleep apnea")

    # Moderate
    if x.sleep_quality == "FRAGMENTED":
        p += 1; reasons.append("fragmented sleep")
    if x.alcohol_bucket in {"8-14", "15+"}:
        p += 1; reasons.append("alcohol exposure affecting sleep")
    if x.rhr_bucket == "ELEVATED":
        p += 1; reasons.append("physiologic stress proxy (RHR)")
    if x.exercise_bucket == "LOW":
        p += 1; reasons.append("low activity consistency")

    override = x.known_sleep_apnea or (x.sleep_duration_bucket == "<6" and x.sleep_quality == "POOR")
    level = "High" if (override or p >= 4) else level_from_points(p, low_max=1, mod_max=3)
    return level, p, reasons[:3]


def score_msk_energy(x: Inputs) -> Tuple[Likelihood, int, List[str]]:
    p = 0
    reasons: List[str] = []
    ews = excess_weight_signal(x.height_cm, x.weight_kg)

    # Major
    if x.exercise_bucket == "LOW":
        p += 2; reasons.append("low strength/movement consistency")
    if x.sleep_quality == "POOR" or x.sleep_duration_bucket == "<6":
        p += 2; reasons.append("insufficient recovery signal")

    # Moderate
    if ews:
        p += 1; reasons.append("higher load on system (weight signal)")
    if x.sleep_quality == "FRAGMENTED":
        p += 1; reasons.append("fragmented recovery")

    level = "High" if p >= 4 else level_from_points(p, low_max=1, mod_max=3)
    return level, p, reasons[:3]


def pick_actions(cardio: Likelihood, sleep: Likelihood, msk: Likelihood, x: Inputs) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []

    sleep_trigger = (sleep in {"Moderate", "High"}) or (x.sleep_quality != "RESTFUL")
    strength_trigger = (msk in {"Moderate", "High"}) or (x.exercise_bucket == "LOW") or excess_weight_signal(x.height_cm, x.weight_kg)

    if sleep_trigger:
        actions.append({
            "title": "Lock a non-negotiable sleep floor",
            "target": "≥7 hours in bed; consistent window (±45 min); 5 nights/week",
            "why": "Highest-leverage lever for BP, glucose regulation, recovery, and adherence."
        })

    if strength_trigger:
        actions.append({
            "title": "Strength training 2×/week",
            "target": "30–40 minutes; simple compound/bodyweight; consistency > intensity",
            "why": "Protects against cardiometabolic decline and improves energy even without weight loss."
        })

    # Alcohol (only if room, not redundant)
    if len(actions) < 2 and x.alcohol_bucket in {"8-14", "15+"} and (sleep in {"Moderate", "High"} or cardio in {"Moderate", "High"}):
        actions.append({
            "title": "Reduce alcohol exposure",
            "target": "Aim ≤7 drinks/week; 2 alcohol-free days/week",
            "why": "Improves sleep quality and reduces cardiometabolic load."
        })

    return actions[:2]
