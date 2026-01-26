# app/intelligence/intent_analyzer.py

from app.intelligence.llm_client import run_llm
import json
import re


# -------------------------------------------------
# 1️⃣ FAST RULE-BASED EMOTION DETECTION (GUARANTEED)
# -------------------------------------------------
def detect_emotion_rules(text: str) -> str | None:
    t = text.lower()

    if any(w in t for w in ["sad", "down", "depressed", "unhappy", "low"]):
        return "sad"
    if any(w in t for w in ["stressed", "stress", "anxious", "tired"]):
        return "stressed"
    if any(w in t for w in ["angry", "frustrated", "mad"]):
        return "angry"
    if any(w in t for w in ["happy", "excited", "joyful"]):
        return "happy"

    return None


# -------------------------------------------------
# 2️⃣ MAIN INTENT ANALYZER
# -------------------------------------------------
def analyze_intent(text: str) -> dict:
    """
    Interpreter between human language and MusicGen.
    Uses rules + LLM + safety overrides.
    """

    # ---------- RULE PASS ----------
    rule_emotion = detect_emotion_rules(text)

    prompt = f"""
You are a senior music therapist and creative music director.

Your task:
- Interpret user intent
- Decide what kind of music HELPS the user
- Translate into music-generation instructions

Rules:
- Prefer instrumental music unless vocals requested
- Respond ONLY with valid JSON
- Do NOT include explanations outside JSON

JSON schema:
{{
  "user_emotion": string,
  "desired_music_effect": string,
  "genre": string,
  "tempo": "slow" | "medium" | "fast",
  "energy": "low" | "medium" | "high",
  "instruments": [string],
  "vocals": "none" | "male" | "female",
  "reasoning": string
}}

User input:
{text}
"""

    raw = run_llm(prompt)

    try:
        llm_intent = json.loads(extract_json(raw))
    except Exception:
        llm_intent = {}

    intent = normalize_intent(llm_intent)

    # -------------------------------------------------
    # 3️⃣ SAFETY OVERRIDES (CRITICAL)
    # -------------------------------------------------
    if rule_emotion:
        intent["user_emotion"] = rule_emotion

        if rule_emotion == "sad":
            intent["desired_music_effect"] = "uplifting"
            intent["tempo"] = "medium"
            intent["energy"] = "medium"
            intent["instruments"] = intent["instruments"] or [
                "piano",
                "soft strings",
                "warm pads",
            ]
            intent["vocals"] = "none"

        elif rule_emotion == "stressed":
            intent["desired_music_effect"] = "calming"
            intent["tempo"] = "slow"
            intent["energy"] = "low"
            intent["instruments"] = intent["instruments"] or [
                "pads",
                "piano",
                "ambient textures",
            ]
            intent["vocals"] = "none"

    return intent


# -------------------------------------------------
# 4️⃣ NORMALIZATION
# -------------------------------------------------
def normalize_intent(intent: dict) -> dict:
    return {
        "user_emotion": intent.get("user_emotion", "neutral"),
        "desired_music_effect": intent.get("desired_music_effect", "neutral"),
        "genre": intent.get("genre", "ambient"),
        "tempo": intent.get("tempo", "medium"),
        "energy": intent.get("energy", "medium"),
        "instruments": intent.get("instruments", []),
        "vocals": intent.get("vocals", "none"),
        "reasoning": intent.get("reasoning", ""),
    }


# -------------------------------------------------
# 5️⃣ JSON EXTRACTION
# -------------------------------------------------
def extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found")
    return text[start : end + 1]

