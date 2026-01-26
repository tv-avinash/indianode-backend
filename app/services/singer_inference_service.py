from typing import Dict
import re


class SingerInferenceService:
    """
    Infers singer type (male / female / duet) from lyrics + intent.
    """

    FEMALE_CUES = [
        "love", "romantic", "lullaby", "mother", "goddess",
        "soft", "gentle", "cradle", "devotional"
    ]

    MALE_CUES = [
        "shiva", "mahadev", "warrior", "power",
        "strength", "chant", "mantra"
    ]

    DUET_CUES = [
        "conversation", "dialogue", "together",
        "union", "marriage", "wedding", "duet"
    ]

    def infer(
        self,
        lyrics: str,
        style: str = "default",
        tempo: str = "medium"
    ) -> Dict:
        text = lyrics.lower()

        female_score = self._score(text, self.FEMALE_CUES)
        male_score = self._score(text, self.MALE_CUES)
        duet_score = self._score(text, self.DUET_CUES)

        # Style-based bias (NOT hardcoded output)
        if style == "romantic":
            female_score += 1
        if style == "devotional" and "shiva" in text:
            male_score += 1
        if tempo == "medium":
            duet_score += 0.5

        # Decision
        if duet_score >= max(male_score, female_score):
            singer = "duet"
        elif female_score > male_score:
            singer = "female"
        else:
            singer = "male"

        return {
            "singer_type": singer,
            "scores": {
                "male": male_score,
                "female": female_score,
                "duet": duet_score
            }
        }

    def _score(self, text: str, cues: list) -> float:
        score = 0.0
        for c in cues:
            if re.search(rf"\b{c}\b", text):
                score += 1.0
        return score

