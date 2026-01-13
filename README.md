# HealthSignal

HealthSignal is a preventive health triage MVP for busy adults who want clarity—not dashboards—about their health.

It helps answer three simple questions:

* What health risks actually matter for me over the next 5–10 years?
* What should I realistically do in the next 90 days?
* What can I stop worrying about right now?

This is decision support, not medical care.



## Why I Built This

Most health apps overwhelm people with metrics, optimization tactics, or generic advice. That works poorly for people who are already busy and mostly healthy.

What’s missing is **prioritization**.

HealthSignal is built around the idea that prevention is a triage problem. If everything is important, nothing is. The product deliberately limits scope so users walk away with clarity instead of anxiety.

If the output can’t be explained in under a minute, it’s too complicated.



## Who It’s For

**Primary users**

* Ages 30–45
* Full-time, cognitively demanding work
* Generally healthy, but noticing early signals (fatigue, stress, weight creep, poor sleep, borderline labs)
* Interested in prevention, not diagnosis

**Not designed for (v1)**

* Aesthetic optimization (<25)
* Established chronic disease (45+)
* Anyone looking for diagnoses, treatment plans, or medical advice



## What It Does

Users complete a short intake (under 7 minutes). HealthSignal generates a single-page report with four sections:

### 1. Risk Summary (5–10 year horizon)

* Top future risks (cardiometabolic, sleep/stress, musculoskeletal/energy)
* Relative likelihood: Low / Moderate / High
* Plain-English drivers
* Explicit uncertainty language

### 2. Priority Actions (next 90 days)

* Exactly two high-leverage actions
* Specific, realistic, and time-bound
* Corrective actions for higher-risk users
* Maintenance actions for low-risk users (no “nothing to do” state)

### 3. Early Warning Signals

* A small number of signals worth monitoring
* Clear thresholds for reassessment

### 4. What You *Don’t* Need to Worry About

* Explicit deprioritization (CGMs, advanced panels, supplement stacks, extreme protocols)

This section is intentional. Reducing unnecessary concern is part of the product.



## What It Doesn’t Do

HealthSignal is intentionally conservative.

It does **not**:

* Diagnose conditions
* Provide treatment plans
* Output precise risk percentages
* Replace clinicians
* Encourage extreme optimization or biohacking

This is triage, not medicine.



## How It’s Built

* **Frontend:** Streamlit
* **Logic:** Conservative, explainable heuristics + structured reasoning
* **Design choices:**

  * Deterministic outputs
  * Explicit tradeoffs and uncertainty
  * Clear separation between decision support and care

A Debug tab exposes internal scoring to make the system transparent and testable.



## Why This Project Matters (Portfolio Context)

This MVP demonstrates:

* Product judgment in a sensitive domain
* Clear risk framing and prioritization
* AI restraint rather than maximalism
* Thoughtful handling of healthy users, not just acute cases

Narratively, it extends an earlier acute-care triage project into preventive care—where prioritization and clarity matter even more.



## Current Status

* MVP complete and stable
* Logic validated across multiple personas
* UI and state handling finalized
* Feature expansion intentionally paused to avoid scope creep



## Disclaimer

HealthSignal is for educational and decision-support purposes only.
It is not a medical device and does not provide diagnosis or treatment.
Users should seek professional medical care for symptoms or clinical concerns.
