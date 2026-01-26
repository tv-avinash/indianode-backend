# app/music_reasoner/music_rules.py

TEMPO_MAP = {
    "low": 60,
    "medium": 90,
    "high": 120,
}

MODE_MAP = {
    "sad": "minor",
    "happy": "major",
    "calm": "minor",
    "devotional": "minor",
    "neutral": "major",
}

INTENT_INSTRUMENTS = {
    "comfort": ["piano", "pad"],
    "relaxation": ["pad", "strings", "soft_synth"],
    "celebration": ["drums", "bass", "synth"],
    "devotional": ["harmonium", "flute", "tanpura"],
}

CULTURE_INSTRUMENTS = {
    "indian": ["tabla", "bansuri"],
    "western": ["piano", "guitar"],
    "neutral": [],
}

AMBIENCE_LAYERS = {
    "rain": "rain",
    "traffic": "traffic",
    "nature": "birds",
    "temple": "bells",
}

