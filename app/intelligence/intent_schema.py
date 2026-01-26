# app/intelligence/intent_schema.py

INTENT_SCHEMA = {
    # Free-text (NOT validated)
    "semantic_emotion": None,

    # Bounded musical controls
    "emotion": [
        "sad", "happy", "calm", "angry", "tired",
        "devotional", "romantic", "energetic", "neutral"
    ],
    "energy": ["low", "medium", "high"],
    "intent": [
        "comfort", "celebration", "relaxation",
        "devotional", "focus", "background", "dance"
    ],
    "culture": ["indian", "western", "neutral"],
    "ambience": ["rain", "traffic", "nature", "temple", "crowd"]
}

