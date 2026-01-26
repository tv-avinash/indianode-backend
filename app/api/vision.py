# app/api/vision.py

from fastapi import APIRouter, UploadFile, File
import base64
import os
from openai import OpenAI

router = APIRouter(prefix="/api/vision", tags=["vision"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================================
# 🔥 MUSICGEN-STYLE PROMPTING (NOT STRUCTURED JSON)
# =========================================================
#
# CRITICAL:
# MusicGen = TEXT → AUDIO diffusion
# NOT MIDI / symbolic engine
#
# So:
# ❌ NO bpm
# ❌ NO bars
# ❌ NO time signatures
# ❌ NO articulation theory
# ❌ NO JSON schema
#
# ONLY:
#   descriptive natural English
#
# =========================================================

SYSTEM_PROMPT = """
You are an expert music producer.

You receive an IMAGE.

Your job:
Describe the music that should accompany this image
as a natural, realistic instrumental soundtrack.

IMPORTANT RULES:

DO NOT output:
- bpm numbers
- time signatures
- bars or measures
- note lengths
- music theory jargon
- articulation terms
- JSON
- lists
- technical tokens

ONLY output:
- one natural English sentence
- instruments
- mood
- tempo described in words (slow, medium, fast)
- atmosphere
- environment
- texture
- production style

Examples:

"soft bansuri flute melody at sunrise by a calm river, gentle slow tempo, light tanpura drone, spacious natural ambience, warm clean mix"

"energetic electronic dance track with punchy kick drums, driving bass, bright synth leads, club atmosphere, wide stereo, modern mix"

Output ONLY the final sentence.
No explanations.
"""


# =========================================================
# ROUTE
# =========================================================

@router.post("/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.35,
            max_tokens=160,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe the best matching music for this image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ]
        )

        prompt_line = completion.choices[0].message.content.strip()

        return {
            "source": "vision-natural",
            "analysis": {
                "suggested_prompt": prompt_line
            }
        }

    except Exception as e:
        print("VISION ERROR:", repr(e))

        # safe fallback
        return {
            "source": "fallback",
            "analysis": {
                "suggested_prompt":
                    "soft instrumental background music, calm melody, warm ambience, gentle tempo, clean professional mix"
            }
        }

