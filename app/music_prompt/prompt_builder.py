# app/music_prompt/prompt_builder.py

def build_musicgen_prompt(
    music_plan: dict,
    base_duration: int = 10
) -> dict:
    """
    Convert a music plan into MusicGen-friendly prompt + params.
    """

    tempo = music_plan.get("tempo", 90)
    mode = music_plan.get("mode", "major")
    instruments = music_plan.get("instruments", [])
    ambience = music_plan.get("ambience_layers", [])

    # --- Text fragments ---
    tempo_text = f"{tempo} BPM"
    mode_text = f"{mode}-scale"
    instrument_text = ", ".join(instruments) if instruments else "soft instruments"
    ambience_text = ""

    if ambience:
        ambience_text = f" with {', '.join(ambience)} ambience"

    description = (
        f"{mode_text} music at {tempo_text} "
        f"using {instrument_text}{ambience_text}"
    )

    return {
        "description": description,
        "duration": base_duration
    }

