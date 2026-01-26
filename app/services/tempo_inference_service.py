from typing import Dict
import re


class TempoInferenceService:
    """
    Infers musical tempo intent from natural language.
    Returns deterministic timing parameters for audio pipelines.
    """

    # Deterministic execution map (SAFE)
    TEMPO_MAP = {
        "very_slow": {
            "syllables_per_second": 1.2,
            "description": "Very slow, meditative, deep devotional"
        },
        "slow": {
            "syllables_per_second": 1.8,
            "description": "Calm, devotional, emotional"
        },
        "medium": {
            "syllables_per_second": 2.6,
            "description": "Balanced, melodic, storytelling"
        },
        "fast": {
            "syllables_per_second": 3.6,
            "description": "Energetic, rhythmic, upbeat"
        }
    }

    # Semantic cues (INTENT ONLY, not timing)
    VERY_SLOW_CUES = [
        "meditative", "chant", "aarti", "deep devotion",
        "mantra", "temple", "spiritual", "peaceful silence"
    ]

    SLOW_CUES = [
        "devotional", "calm", "peaceful", "romantic",
        "soft", "emotional", "bhajan", "slow"
    ]

    FAST_CUES = [
        "fast", "energetic", "dance", "celebration",
        "folk", "festival", "upbeat", "rock"
    ]

    def infer(self, request_text: str) -> Dict:
        """
        Infer tempo class from user request.
        """
        text = request_text.lower()

        # Very slow has highest priority
        if self._contains_any(text, self.VERY_SLOW_CUES):
            tempo = "very_slow"

        # Fast overrides medium/slow
        elif self._contains_any(text, self.FAST_CUES):
            tempo = "fast"

        # Slow devotional default
        elif self._contains_any(text, self.SLOW_CUES):
            tempo = "slow"

        # Default musical pacing
        else:
            tempo = "medium"

        return {
            "tempo": tempo,
            "syllables_per_second": self.TEMPO_MAP[tempo]["syllables_per_second"],
            "description": self.TEMPO_MAP[tempo]["description"]
        }

    @staticmethod
    def _contains_any(text: str, keywords: list) -> bool:
        for k in keywords:
            if re.search(rf"\b{k}\b", text):
                return True
        return False

