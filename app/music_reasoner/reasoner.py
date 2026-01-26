# app/music_reasoner/reasoner.py

def reason_music(intent: dict) -> dict:
    """
    Convert normalized intent into a structured music plan
    """

    mood = intent.get("mood", "calm")
    energy = intent.get("energy", "medium")
    tempo = intent.get("tempo", "medium")
    genre = intent.get("genre", "ambient")

    instruments = intent.get("instruments", [])
    if not instruments:
        instruments = default_instruments_for_mood(mood)

    ambience_layers = ambience_for_energy(energy)

    return {
        "mood": mood,
        "energy": energy,
        "tempo": tempo,
        "genre": genre,
        "instruments": instruments,
        "ambience_layers": ambience_layers,
    }


def default_instruments_for_mood(mood: str) -> list[str]:
    mood = mood.lower()

    if mood in ("sad", "melancholic"):
        return ["violin", "piano", "pad"]
    if mood in ("happy", "joyful"):
        return ["guitar", "flute", "bells"]
    if mood in ("angry", "intense"):
        return ["drums", "bass", "synth"]

    return ["piano", "pad"]


def ambience_for_energy(energy: str) -> list[str]:
    if energy == "low":
        return ["soft_pad", "reverb"]
    if energy == "high":
        return ["impact", "wide_stereo"]

    return ["balanced"]

