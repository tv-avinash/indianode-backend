# app/music_prompt/builder.py

def build_musicgen_prompt(
    intent: dict,
    music_plan: dict,
    instruments: list[str],
    user_text: str,
) -> str:
    """
    Converts reasoning + intent into a clean MusicGen prompt.
    This MUST be pure text. No JSON. No metadata.
    """

    parts = []

    # Emotion & intent
    emotion = intent.get("emotion")
    intent_type = intent.get("intent")
    energy = intent.get("energy")

    if emotion:
        parts.append(f"{emotion} mood")
    if intent_type:
        parts.append(intent_type)
    if energy:
        parts.append(f"{energy} energy")

    # Musical structure
    tempo = music_plan.get("tempo")
    mode = music_plan.get("mode")

    if tempo:
        parts.append(f"{tempo} bpm")
    if mode:
        parts.append(f"{mode} scale")

    # Instruments
    if instruments:
        parts.append("with " + ", ".join(instruments))

    # Ambience
    ambience = music_plan.get("ambience_layers", [])
    if ambience:
        parts.append("ambient sounds of " + ", ".join(ambience))

    # User text last (for creativity)
    if user_text:
        parts.append(f"inspired by: {user_text}")

    return ", ".join(parts)

