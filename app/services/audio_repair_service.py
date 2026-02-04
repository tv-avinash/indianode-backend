# ======================================================
# Intelligent repair engine
# reason -> deterministic fix
# ======================================================

def repair_generation(model, prompt, reason, duration):
    """
    Adjusts BOTH:
      - generation params
      - prompt
    before next retry
    """

    params = dict(
        duration=duration,
        use_sampling=True,
        temperature=0.9,
        top_k=120,
        cfg_coef=3.5
    )

    new_prompt = prompt.lower()

    # ----------------------------
    # musical fixes
    # ----------------------------

    if "pitch" in reason or "off-key" in reason:
        params["temperature"] = 0.7
        params["top_k"] = 70
        params["cfg_coef"] = 4.0
        new_prompt += ", stable tuning, in key, harmonious melody"

    elif "tempo" in reason:
        params["temperature"] = 0.8
        params["top_k"] = 90
        new_prompt += ", steady rhythm, consistent tempo"

    # ----------------------------
    # technical fixes
    # ----------------------------

    elif "noise" in reason or "harsh" in reason or "clipping" in reason:
        params["temperature"] = 0.8
        new_prompt += ", clean studio quality, no distortion, no noise"

    # ----------------------------
    # intent fixes (NEW 🔥)
    # ----------------------------

    elif "intent" in reason:
        params["cfg_coef"] = 5.0
        new_prompt += ", strictly follow the requested mood and style only"

    model.set_generation_params(**params)

    return new_prompt

