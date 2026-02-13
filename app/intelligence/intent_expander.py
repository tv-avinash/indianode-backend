# app/intelligence/intent_expander.py

"""
Intent Expander (Layer 1 — Director Brain)

This is the ONLY intelligence layer before MusicGen.

GOAL
-----
Convert ANY user input (even 1 word) into a
clear, structured, professional music production brief.

Think:
    film composer
    trailer music producer
    festival EDM producer
    hit song director

NOT:
    poet
    storyteller
    essay writer

MusicGen performs MUCH better when prompts:
✔ are structured
✔ have sections (intro → build → drop → climax)
✔ use concrete instruments
✔ use clear actions (Start, Add, Drop, Build)
✘ NOT vague emotional paragraphs

Pipeline:
User → Expander → Guardrails → MusicGen
"""

import os
from typing import List, Optional
from openai import OpenAI


# =====================================================
# Client
# =====================================================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# 🔥 STRONG DIRECTOR SYSTEM PROMPT
# =====================================================

SYSTEM = """
You are a world-class film composer and hit music producer.

Your task:
EXPAND the user's idea into a PROFESSIONAL, HIGH-BUDGET
music production brief for an AI music generator.

CRITICAL:
Do NOT write poetry.
Do NOT narrate stories.
Do NOT write emotional paragraphs.

Write like a MUSIC DIRECTOR giving studio instructions.

================================================

FORMAT STYLE (ALWAYS FOLLOW):

Create ...

Start with ...

Gradually introduce ...

Build intensity with ...

Add ...

Drop into ...

Finish with ...

Mood: ...
Energy curve: ...

================================================

STRICT RULES:

• preserve the user's genre exactly
• never change instruments provided by the user
• never remove requested instruments
• if instruments are missing → add suitable ones for that style
• instrumental unless vocals explicitly requested

CLASSICAL MODE RULE:
If mode is classical → ONLY Indian classical instruments
(veena, sitar, bansuri, mridangam, tabla, tanpura, ghatam, etc)
NEVER use western orchestra or brass.

================================================

VERY IMPORTANT:

Use CONCRETE musical elements ONLY:
✔ instruments
✔ drums
✔ bass
✔ melody
✔ rhythm
✔ groove
✔ hook
✔ percussion
✔ drops
✔ sections

Avoid vague words like:
beautiful, lush, journey, tapestry, dreamy, magical

Be DIRECT. Be STRUCTURED. Be SPECIFIC.

Think:
movie trailer
festival anthem
viral hit song
premium production

================================================

Output must sound like a professional production plan,
not like a description.

Return ONLY the expanded production brief.
"""


# =====================================================
# Helpers
# =====================================================

def _join(items: List[str]) -> str:
    return ", ".join(items) if items else ""


# =====================================================
# Main Expander
# =====================================================

def expand_prompt(
    text: str,
    instruments: Optional[List[str]] = None,
    preset: Optional[str] = None,
    mode: str = "cinematic",
) -> str:

    if not text or not text.strip():
        return text

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY missing — skipping expander")
        return text

    instruments = instruments or []

    # -------------------------------------------------
    # DEBUG
    # -------------------------------------------------

    print("🔥 EXPANDER MODE ->", mode)
    print("🔥 EXPANDER INSTRUMENTS ->", instruments)
    print("🔥 EXPANDER TEXT ->", text)

    # -------------------------------------------------
    # Build context block for LLM
    # -------------------------------------------------

    context_parts = []

    if preset:
        context_parts.append(f"Preset: {preset}")

    if instruments:
        context_parts.append(
            f"User requested instruments (must include): {_join(instruments)}"
        )

    context_parts.append(f"Mode: {mode}")
    context_parts.append(f"User idea: {text}")

    context = "\n".join(context_parts)

    # -------------------------------------------------
    # LLM call
    # -------------------------------------------------

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.9,       # more creative/director-like
            max_tokens=320,        # allow rich structure
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": context},
            ],
        )

        expanded = res.choices[0].message.content.strip()

        print("🔥 EXPANDED RESULT ->", expanded)

        return expanded if expanded else text

    except Exception as e:
        print("Intent expansion failed:", e)
        return text

