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

    new_prompt = prompt

    # ----------------------------
    # targeted fixes
    # ----------------------------

    if "off-key" in reason or "besura" in reason or "pitch" in reason:
        params["temperature"] = 0.7
        params["top_k"] = 70
        params["cfg_coef"] = 4.0
        new_prompt += ", stable tuning, harmonious, in key"

    elif "tempo" in reason:
        params["temperature"] = 0.8
        params["top_k"] = 90
        new_prompt += ", steady rhythm, consistent tempo"

    elif "perceptual" in reason or "noise" in reason:
        params["temperature"] = 0.8
        new_prompt += ", clean studio quality, no noise"

    elif "match prompt" in reason:
        params["cfg_coef"] = 4.5

    model.set_generation_params(**params)

    return new_prompt
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

    new_prompt = prompt

    # ----------------------------
    # targeted fixes
    # ----------------------------

    if "off-key" in reason or "besura" in reason or "pitch" in reason:
        params["temperature"] = 0.7
        params["top_k"] = 70
        params["cfg_coef"] = 4.0
        new_prompt += ", stable tuning, harmonious, in key"

    elif "tempo" in reason:
        params["temperature"] = 0.8
        params["top_k"] = 90
        new_prompt += ", steady rhythm, consistent tempo"

    elif "perceptual" in reason or "noise" in reason:
        params["temperature"] = 0.8
        new_prompt += ", clean studio quality, no noise"

    elif "match prompt" in reason:
        params["cfg_coef"] = 4.5

    model.set_generation_params(**params)

    return new_prompt
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

    new_prompt = prompt

    # ----------------------------
    # targeted fixes
    # ----------------------------

    if "off-key" in reason or "besura" in reason or "pitch" in reason:
        params["temperature"] = 0.7
        params["top_k"] = 70
        params["cfg_coef"] = 4.0
        new_prompt += ", stable tuning, harmonious, in key"

    elif "tempo" in reason:
        params["temperature"] = 0.8
        params["top_k"] = 90
        new_prompt += ", steady rhythm, consistent tempo"

    elif "perceptual" in reason or "noise" in reason:
        params["temperature"] = 0.8
        new_prompt += ", clean studio quality, no noise"

    elif "match prompt" in reason:
        params["cfg_coef"] = 4.5

    model.set_generation_params(**params)

    return new_prompt
