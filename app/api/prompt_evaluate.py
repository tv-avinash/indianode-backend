# app/api/prompt_evaluate.py

from fastapi import APIRouter
from pydantic import BaseModel
import os
import json
from openai import OpenAI


router = APIRouter(prefix="/api/prompt", tags=["prompt"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =================================================
# Request schema
# =================================================

class PromptEvalRequest(BaseModel):
    prompt: str


# =================================================
# 🔥 LLM = STRUCTURE COMPOSER (GENRE NEUTRAL)
# =================================================
#
# This stage ONLY decides:
#   • tempo
#   • instruments
#   • structure
#   • phrasing
#
# It does NOT:
#   • enforce tone realism
#   • force negatives
#   • apply veena/flute locks
#
# Guardrails will handle realism later.
#
# IMPORTANT DESIGN:
#   DEFAULT → WESTERN instruments
#   INDIAN only if explicitly requested
#
# =================================================

SYSTEM_PROMPT = """
You are a deterministic MusicGen music arranger.

Return STRICT JSON ONLY.
Return EXACTLY the schema.
Never output prose or explanations.

CRITICAL INSTRUMENT SELECTION RULE:

DEFAULT:
Use WESTERN instruments (piano, strings, guitar, synth, bass, drums).

ONLY use INDIAN instruments if the user explicitly mentions:
carnatic, hindustani, indian, raga, tala, kriti, bhajan,
veena, bansuri, flute (indian), nadaswaram, mridangam, tabla, tanpura.

Never assume Indian style automatically.


Every value MUST directly affect sound synthesis.
Fill ALL keys even if guessing.


Schema:

{
  tempo_bpm:int,
  time_signature:str,
  tala:str,
  scale_or_raga:str,

  lead_instrument:str,
  lead_role:str,

  support_instruments:list,
  rhythm_instruments:list,
  drone_instruments:list,

  phrase_length:str,
  note_length:str,
  rest_density:str,

  articulation:list,
  ornamentation:list,
  melodic_motion:str,

  attack:str,
  sustain:str,
  decay:str,

  recording_style:list,
  mix_style:list,

  negatives:list
}

Rules:
• only real acoustic or synth instruments
• solo → empty support/rhythm
• only technical audio terms
• no emotional/cinematic words
"""


# =================================================
# 🔥 DEFAULTS (GENRE NEUTRAL SAFE FALLBACK)
# =================================================
# NOTE:
#   Western defaults (NOT flute)
#   No forced negatives
# =================================================

DEFAULT_CONFIG = {
    "tempo_bpm": 90,
    "time_signature": "4/4",
    "tala": "",
    "scale_or_raga": "",

    "lead_instrument": "piano",   # ← IMPORTANT (neutral)
    "lead_role": "melody",

    "support_instruments": ["strings"],
    "rhythm_instruments": [],
    "drone_instruments": [],

    "phrase_length": "4 bars",
    "note_length": "medium",
    "rest_density": "medium",

    "articulation": ["legato"],
    "ornamentation": [],
    "melodic_motion": "stepwise",

    "attack": "soft",
    "sustain": "medium",
    "decay": "short",

    "recording_style": ["dry", "close mic", "mono"],
    "mix_style": [],

    "negatives": []   # ← no forced constraints
}


REQUIRED_KEYS = list(DEFAULT_CONFIG.keys())


# =================================================
# 🔥 SAFETY FILL
# =================================================

def fill_missing(cfg: dict) -> dict:
    """
    Guarantees ALL keys exist.
    Prevents partial LLM outputs.
    """

    final = DEFAULT_CONFIG.copy()

    for k, v in cfg.items():
        final[k] = v

    return final


# =================================================
# JSON → MusicGen prompt builder
# =================================================

def config_to_musicgen_prompt(cfg: dict) -> str:
    """
    Deterministic conversion
    JSON → comma-separated MusicGen prompt
    """

    parts = []

    # tempo / rhythm
    parts.append(f"{cfg['tempo_bpm']} bpm")
    parts.append(cfg["time_signature"])

    if cfg["tala"]:
        parts.append(cfg["tala"])

    if cfg["scale_or_raga"]:
        parts.append(cfg["scale_or_raga"])

    # lead
    parts.append(f"{cfg['lead_instrument']} lead")

    if cfg["lead_role"]:
        parts.append(cfg["lead_role"])

    # layers
    parts.extend(cfg["support_instruments"])
    parts.extend(cfg["rhythm_instruments"])
    parts.extend(cfg["drone_instruments"])

    # performance
    parts.append(cfg["phrase_length"])
    parts.append(cfg["note_length"])
    parts.append(cfg["rest_density"])

    parts.extend(cfg["articulation"])
    parts.extend(cfg["ornamentation"])

    parts.append(cfg["melodic_motion"])

    parts.append(cfg["attack"])
    parts.append(cfg["sustain"])
    parts.append(cfg["decay"])

    # recording / mix
    parts.extend(cfg["recording_style"])
    parts.extend(cfg["mix_style"])

    # negatives (optional)
    parts.extend(cfg["negatives"])

    parts = [p for p in parts if p]

    return ", ".join(parts)


# =================================================
# API
# =================================================

@router.post("/evaluate")
def evaluate_prompt(req: PromptEvalRequest):

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.15,  # deterministic
        max_tokens=700,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.prompt},
        ],
    )

    raw = completion.choices[0].message.content.strip()

    # ---------------------------------------------
    # Parse JSON safely
    # ---------------------------------------------
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {}

    config = fill_missing(parsed)

    prompt_line = config_to_musicgen_prompt(config)

    return {
        "enhanced_config": config,
        "enhanced_prompt": prompt_line
    }

