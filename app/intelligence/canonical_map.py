# app/intelligence/canonical_map.py

EMOTION_MAP = {
    "sadness": "sad",
    "sad": "sad",
    "lonely": "sad",
    "nostalgic": "sad",
    "melancholy": "sad",

    "happiness": "happy",
    "joy": "happy",
    "cheerful": "happy",
    "excited": "energetic",

    "peaceful": "calm",
    "relaxed": "calm",
    "calming": "calm",

    "spiritual": "devotional",
    "devotion": "devotional",

    "angry": "angry",
    "tired": "tired",
}

INTENT_MAP = {
    "relax": "relaxation",
    "relaxing": "relaxation",
    "chill": "relaxation",
    "calm": "relaxation",

    "comfort": "comfort",
    "console": "comfort",

    "celebrate": "celebration",
    "celebrating": "celebration",
    "party": "celebration",

    "pray": "devotional",
    "prayer": "devotional",
    "worship": "devotional",

    "background": "background",
    "focus": "focus",
    "study": "focus",

    "dance": "dance"
}

ENERGY_MAP = {
    "low": "low",
    "soft": "low",
    "mellow": "low",
    "slow": "low",
    "calm": "low",

    "medium": "medium",
    "moderate": "medium",
    "balanced": "medium",

    "high": "high",
    "energetic": "high",
    "fast": "high",
    "intense": "high"
}

AMBIENCE_MAP = {
    "rain": "rain",
    "rainy": "rain",
    "rainfall": "rain",
    "drizzle": "rain",
    "storm": "rain",

    "traffic": "traffic",
    "city": "traffic",
    "road": "traffic",

    "nature": "nature",
    "forest": "nature",
    "birds": "nature",
    "wind": "nature",

    "temple": "temple",
    "church": "temple",
    "mosque": "temple",

    "crowd": "crowd",
    "people": "crowd",
    "market": "crowd"
}

