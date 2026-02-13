# app/intelligence/prompt_enhancer.py

"""
Prompt Enhancer (MASTER PROMPT LAYER)

Role:
- Convert raw user text into a clean, expressive musical description
- Help MusicGen understand mood + arrangement
- DO NOT add technical audio / mixing words
- Guardrails will handle timbre realism later

Pipeline:
User → LLM (this file) → Guardrails → MusicGen
"""

import os
from openai import OpenAI


# =====================================================
# Client
# =====================================================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# System Prompt  (⭐ tuned for MusicGen quality)
# =====================================================

SYSTEM = """
Rewrite the user's request into a natural musical description
for an AI music generator.

Guidelines:
- describe mood and emotion clearly
- mention instruments naturally if provided
- cinematic and expressive language
- 1–2 sentences only
- 25–40 words ideal
- avoid technical audio or mixing terms
- avoid commas spam or keyword lists
- sound like a human describing music

Return ONLY the sentence.
"""


# =====================================================
# Main API
# =====================================================
def enhance_prompt(text: str) -> str:

    if not text or not text.strip():
        return text

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY missing — skipping LLM enhancement")
        return text

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": text},
            ],
        )

        enhanced = res.choices[0].message.content.strip()
        return enhanced if enhanced else text

    except Exception as e:
        print("Prompt enhancement failed:", e)
        return text

