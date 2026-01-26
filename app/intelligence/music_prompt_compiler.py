# app/intelligence/music_prompt_compiler.py

def build_musicgen_prompt(intent: dict) -> str:
    """
    Convert interpreted musical intent into a clean MusicGen prompt.
    Deterministic, no LLM, no side effects.
    """

    parts = []

    # 1. Desired effect first (most important)
    effect = intent.get("desired_music_effect")
    if effect and effect != "neutral":
        parts.append(effect)

    # 2. Genre
    genre = intent.get("genre")
    if genre:
        parts.append(genre)

    # 3. Tempo
    tempo = intent.get("tempo")
    if tempo:
        parts.append(f"{tempo} tempo")

    # 4. Energy
    energy = intent.get("energy")
    if energy:
        parts.append(f"{energy} energy")

    # 5. Instruments
    instruments = intent.get("instruments", [])
    if instruments:
        parts.append("featuring " + ", ".join(instruments))

    # 6. Vocals
    vocals = intent.get("vocals", "none")
    if vocals == "none":
        parts.append("instrumental, no vocals")
    else:
        parts.append(f"{vocals} vocals")

    # Final assembly
    prompt = ", ".join(parts)

    return prompt.strip()

