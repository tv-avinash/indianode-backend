# app/api/prompt_evaluate.py

from fastapi import APIRouter
from pydantic import BaseModel
import os
from openai import OpenAI


router = APIRouter(prefix="/api/prompt", tags=["prompt"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =================================================
# Request schema
# =================================================

class PromptEvalRequest(BaseModel):
    prompt: str


# =================================================
# 🔥 MUSICGEN-OPTIMIZED PROMPT DESIGN
# =================================================
#
# CRITICAL:
# MusicGen is TEXT → AUDIO diffusion
# NOT symbolic MIDI
#
# So we must:
#
# ❌ NOT use:
#   bpm numbers
#   time signatures
#   bars
#   note lengths
#   articulation theory
#   music theory jargon
#   JSON structure
#
# ✅ ONLY use:
#   mood
#   vibe
#   instruments
#   environment
#   energy words
#   mix/production style
#
# This dramatically improves:
#   • timing stability
#   • sync
#   • realism
#   • instrument coherence
#
# =================================================

SYSTEM_PROMPT = """
You are an expert music producer writing prompts for an AI audio generator (MusicGen).

IMPORTANT RULES:

Write ONLY natural descriptive English.

DO NOT output:
- BPM numbers
- time signatures
- bars or measures
- quarter/eighth/sixteenth notes
- articulation theory (staccato, legato, trill, glissando, conjunct, etc)
- music theory or MIDI terminology
- JSON
- lists of technical tokens

Instead describe:
- instruments
- tempo using words (slow, medium, fast, energetic)
- mood and atmosphere
- environment (river, temple, club, stage, etc)
- energy level
- texture (warm, soft, punchy, wide, cinematic)
- mixing style (clean, modern, professional, spacious)

Style:
- one sentence or comma-separated phrase
- concise but vivid
- realistic
- instrumental unless vocals requested

Output ONLY the final prompt text.
No explanations.
"""


# =================================================
# Prompt builder
# =================================================

def build_musicgen_prompt(user_prompt: str) -> str:
    """
    Converts user prompt → MusicGen-friendly descriptive prompt
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.35,
        max_tokens=180,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    return completion.choices[0].message.content.strip()


# =================================================
# API endpoint
# =================================================

@router.post("/evaluate")
def evaluate_prompt(req: PromptEvalRequest):
    """
    Returns MusicGen-ready prompt only
    """

    enhanced_prompt = build_musicgen_prompt(req.prompt)

    return {
        "enhanced_prompt": enhanced_prompt
    }

