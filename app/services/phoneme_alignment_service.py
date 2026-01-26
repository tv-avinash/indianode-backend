import re
from typing import List, Dict


class PhonemeAlignmentService:
    """
    Lightweight phoneme + duration aligner.
    Language-agnostic baseline (upgradeable later).
    """

    VOWELS = set("aeiouāīūēōAEIOU")

    def text_to_units(self, text: str) -> List[str]:
        """
        Rough phoneme-like split.
        This is NOT final phonetics — it's a musical scaffold.
        """
        text = text.lower()
        text = re.sub(r"[^a-zāīūēō\s]", "", text)

        units = []
        current = ""

        for ch in text:
            current += ch
            if ch in self.VOWELS:
                units.append(current)
                current = ""

        if current.strip():
            units.append(current)

        return units

    def align(
        self,
        line_text: str,
        line_duration_sec: float
    ) -> List[Dict]:
        """
        Returns phoneme-like units with time alignment.
        """
        units = self.text_to_units(line_text)

        if not units:
            return []

        base = line_duration_sec / len(units)

        aligned = []
        for u in units:
            dur = base * (1.4 if any(v in u for v in self.VOWELS) else 0.8)
            aligned.append({
                "ph": u,
                "duration_sec": round(dur, 3)
            })

        return aligned

