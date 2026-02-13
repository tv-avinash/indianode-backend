# app/music_prompt/quality_guardrails.py

from typing import List

"""
QUALITY GUARDRAILS — TIMBRE ONLY (SAFE FOR MULTI-INSTRUMENT)

Golden rule:
Guardrails ONLY improve realism.
Never change arrangement.
Never force solo.
Never forbid instruments.
"""


# =================================================
# TIMBRE RULES ONLY (NO STRUCTURE WORDS)
# =================================================

VEENA_TIMBRE = (
    "sitar style plucked string timbre, warm wooden resonance, "
    "soft finger pluck attack, short natural decay, clean pitch stability"
)

NADASWARAM_TIMBRE = (
    "clarinet style reed timbre, slightly bright nasal tone, "
    "steady breath sustain, expressive slides and gamakas"
)

FLUTE_TIMBRE = (
    "breathy air tone, soft tongued attack, smooth airflow, natural phrasing"
)

TABLA_TIMBRE = (
    "tight strokes, crisp transients, dry skin percussion tone, clear bols"
)

MRIDANGAM_TIMBRE = (
    "double headed drum tone, clean attack, warm resonance, precise rhythm"
)

VIOLIN_TIMBRE = (
    "smooth bowing, light vibrato, expressive slides"
)


# =================================================
# MODE DETECTION
# =================================================

def _detect_mode(prompt: str) -> str:
    p = prompt.lower()
    if any(x in p for x in ["cinematic", "epic", "film", "bgm"]):
        return "cinematic"
    return "classical"


# =================================================
# REALISM PATCHES
# =================================================

def _instrument_rules(instruments: List[str]) -> List[str]:

    rules = []
    lowered = [i.lower() for i in instruments]

    if "veena" in lowered:
        rules.append(VEENA_TIMBRE)

    if "nadaswaram" in lowered:
        rules.append(NADASWARAM_TIMBRE)

    if "flute" in lowered or "bansuri" in lowered:
        rules.append(FLUTE_TIMBRE)

    if "tabla" in lowered:
        rules.append(TABLA_TIMBRE)

    if "mridangam" in lowered:
        rules.append(MRIDANGAM_TIMBRE)

    if "violin" in lowered:
        rules.append(VIOLIN_TIMBRE)

    return rules


# =================================================
# MAIN
# =================================================

def apply_quality_guardrails(prompt: str, instruments: List[str]) -> str:

    parts: List[str] = []

    # 1️⃣ Always keep LLM intent first
    parts.append(prompt.strip())

    # 2️⃣ Optional: reinforce ensemble wording (helps MusicGen)
    if instruments:
        parts.append("featuring " + ", ".join(instruments))

    # 3️⃣ Timbre realism only
    parts.extend(_instrument_rules(instruments))

    # 4️⃣ Mix style
    mode = _detect_mode(prompt)

    if mode == "classical":
        parts.append("dry studio close mic, minimal reverb, natural room sound")
    else:
        parts.append("wide stereo, lush ambience, soft reverb, cinematic depth")

    # 5️⃣ Global clarity
    parts.append("clean articulation, natural dynamics, clear tone, no distortion, no clipping")

    return ", ".join(parts)

