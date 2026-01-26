# app/music_prompt/quality_guardrails.py

from typing import List

"""
QUALITY GUARDRAILS — HARD BASE LOCK VERSION

Philosophy:
• LLM decides arrangement
• Guardrail decides SOUND QUALITY ONLY
• Some instruments use HARD BASE RULES (non-negotiable)
• Never add instruments
• Never remove instruments
• Never contradict requested instruments

Hard locks:
✓ veena      → sitar proxy base
✓ nadaswaram → clarinet proxy base
"""

# =================================================
# 🔥 HARD BASE RULES (PROVEN WORKING PROMPTS)
# =================================================

VEENA_BASE_RULE = (
    "solo sitar, dry studio mono recording, close mic, warm wooden tone, "
    "soft finger pluck, short natural decay, clean pitch, detached notes, "
    "small pauses between notes, simple melodic phrases, single instrument only, "
    "absolutely no accompaniment, no percussion, no drums, no background music, completely dry mix"
)


NADASWARAM_BASE_RULE = (
    "solo clarinet playing raga hamsadhwani, dry studio mono recording, close mic, "
    "light thin reed tone, narrow bore, slightly bright nasal timbre, focused airflow, "
    "steady breath sustain, expressive gamakas and slides, short articulated notes, "
    "small pauses between phrases, clean pitch, simple melodic phrases, single instrument only, "
    "absolutely no accompaniment, no percussion, no drums, no background music, "
    "no pads, no ambience, no reverb, completely dry mix"
)


# -------------------------------------------------
# Known instruments
# -------------------------------------------------

INDIAN_INSTRUMENTS = {
    "veena", "sitar", "bansuri", "flute", "tabla",
    "mridangam", "tanpura", "ghatam", "kanjira",
    "nadaswaram", "santoor", "harmonium", "violin", "piano"
}


# -------------------------------------------------
# MODE DETECTION
# -------------------------------------------------

def _detect_mode(prompt: str) -> str:
    text = prompt.lower()

    if any(k in text for k in ["cinematic", "epic", "film", "bgm", "orchestra"]):
        return "cinematic"

    return "classical"


# -------------------------------------------------
# SMART NEGATIVES (avoid unwanted layers)
# -------------------------------------------------

def _build_negatives(instruments: List[str]) -> str:
    requested = set(i.lower() for i in instruments)

    candidates = [
        "tabla",
        "mridangam",
        "tanpura",
        "pads",
        "bass",
        "drone",
        "strings",
        "background music",
        "percussion",
        "drums",
    ]

    negatives = [f"no {name}" for name in candidates if name not in requested]
    return ", ".join(negatives)


# =================================================
# MAIN (FINAL STAGE BEFORE MUSICGEN)
# =================================================

def apply_quality_guardrails(prompt: str, instruments: List[str]) -> str:
    """
    FINAL PROMPT BUILDER.

    Priority:
    1) Hard base rules (veena / nadaswaram)
    2) Otherwise light realism polish
    3) Mix lock
    """

    lowered = [i.lower() for i in instruments]
    mode = _detect_mode(prompt)

    parts: List[str] = []

    # =================================================
    # 🔥 1️⃣ HARD LOCKS (highest priority)
    # =================================================

    if "veena" in lowered:
        parts.append(VEENA_BASE_RULE)

        # keep musical info like raga/tala
        parts.append(prompt.strip())


    elif "nadaswaram" in lowered:
        parts.append(NADASWARAM_BASE_RULE)

        # keep raga/tala words from original
        parts.append(prompt.strip())


    # =================================================
    # 2️⃣ NORMAL FLOW (no hard lock)
    # =================================================

    else:
        parts.append(prompt.strip())

        realism_rules = []

        for name in lowered:

            if name in ["flute", "bansuri"]:
                realism_rules.append(
                    "breathy air tone, soft tongued attack, stable pitch, natural airflow"
                )

            elif name == "violin":
                realism_rules.append(
                    "smooth bowing, light vibrato, controlled sustain"
                )

            elif name in ["mridangam", "tabla"]:
                realism_rules.append(
                    "tight strokes, clean transients, dry skin sound"
                )

        if realism_rules:
            parts.extend(realism_rules)

    # =================================================
    # 3️⃣ MIX LOCK
    # =================================================

    if mode == "classical":
        negatives = _build_negatives(lowered)

        parts.append(
            "dry studio close mic, mono, very low room sound, minimal reverb, minimal ambience"
        )

        if negatives:
            parts.append(negatives)

    else:
        parts.append(
            "wide stereo, lush ambience, soft reverb, cinematic depth"
        )

    # =================================================
    # 4️⃣ GLOBAL CLARITY
    # =================================================

    parts.append(
        "clean articulation, natural dynamics, clear tone, no distortion, clear ending"
    )

    return ", ".join(parts)

