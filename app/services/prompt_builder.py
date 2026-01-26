from app.services.presets import PRESETS

def build_prompt(
    preset_key: str | None,
    instruments: list[str] | None = None,
    user_description: str | None = None
):
    # 1️⃣ Base prompt resolution
    if preset_key:
        if preset_key not in PRESETS:
            raise ValueError(f"Invalid preset: {preset_key}")
        base_prompt = PRESETS[preset_key]["base_prompt"]
        temperature = PRESETS[preset_key]["temperature"]
    else:
        # Neutral fallback
        base_prompt = "instrumental music composition"
        temperature = 1.0

    # 2️⃣ Instrument enrichment
    if instruments:
        inst_text = ", ".join(instruments)
        base_prompt += f", featuring {inst_text}"

    # 3️⃣ User description enrichment
    if user_description:
        base_prompt += f", {user_description}"

    return base_prompt, temperature

