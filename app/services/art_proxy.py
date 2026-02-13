# app/services/art_proxy.py

import time
import requests
import json
from openai import OpenAI

client = OpenAI()

GALLERY_URL = "http://192.168.68.100:8010"


# =====================================================
# LLM PROMPT GENERATOR (INTENT → STYLE AUTOMATIC)
# =====================================================

def generate_prompts(mood: str):
    """
    LLM decides everything:
    - subject
    - abstraction level
    - composition
    - color palette
    - instruments

    We ONLY guide:
    -> premium
    -> painterly
    -> slightly abstract
    -> not repetitive
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",

        # high creativity but still stable
        temperature=1.15,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a world-class gallery art director and film composer.\n\n"

                    "Your job is to convert the user's idea into:\n"
                    "1) a premium painting prompt for Stable Diffusion XL\n"
                    "2) a matching cinematic background music prompt\n\n"

                    "STYLE RULES FOR IMAGE:\n"
                    "- museum quality fine-art painting\n"
                    "- painterly, textured, expressive\n"
                    "- slightly abstract (not literal illustration)\n"
                    "- avoid stock/AI look\n"
                    "- avoid repeating patterns\n"
                    "- avoid glossy digital render look\n"
                    "- focus on light, depth, materials, emotion\n"
                    "- maximum 28 words (very important)\n\n"

                    "STYLE RULES FOR MUSIC:\n"
                    "- soft cinematic ambient background score\n"
                    "- emotional, immersive\n"
                    "- NO drums, NO beats, NO vocals\n"
                    "- instruments like pads, strings, piano, flute, textures\n"
                    "- maximum 18 words\n\n"

                    "Return EXACT JSON only:\n"
                    '{"image":"...", "music":"..."}'
                )
            },
            {
                "role": "user",
                "content": mood
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        prompts = json.loads(content)
    except Exception:
        # fallback safety
        print("⚠️ LLM JSON parse failed, using raw text")
        prompts = {
            "image": content[:120],
            "music": "soft ambient cinematic background music"
        }

    image_prompt = prompts["image"]
    music_prompt = prompts["music"]

    # =====================================================
    # DEBUG PRINTS (VERY IMPORTANT FOR QUALITY TUNING)
    # =====================================================

    print("\n==============================")
    print("🎨 IMAGE PROMPT USED:")
    print(image_prompt)
    print("\n🎵 MUSIC PROMPT USED:")
    print(music_prompt)
    print("==============================\n")

    return image_prompt, music_prompt


# =====================================================
# MAIN PIPELINE (3090 → 4090)
# =====================================================

def generate_art_from_mood(mood: str):

    image_prompt, music_prompt = generate_prompts(mood)

    # start job on 4090
    r = requests.post(
        f"{GALLERY_URL}/gallery/generate",
        json={
            "prompt": image_prompt,
            "music_prompt": music_prompt
        },
        timeout=600
    )

    r.raise_for_status()

    job_id = r.json()["job_id"]

    # poll until finished
    while True:
        status = requests.get(
            f"{GALLERY_URL}/gallery/status/{job_id}"
        ).json()

        if status["status"] == "done":
            return {
                "image_url": f"{GALLERY_URL}/{status['path']}",
                "music_url": f"{GALLERY_URL}/{status.get('music_path')}" if status.get("music_path") else None,
                "video_url": f"{GALLERY_URL}/{status.get('video_path')}" if status.get("video_path") else None,

                # for debugging in frontend
                "image_prompt_used": image_prompt,
                "music_prompt_used": music_prompt
            }

        if status["status"] == "error":
            raise Exception(status.get("error", "Gallery job failed"))

        time.sleep(2)

