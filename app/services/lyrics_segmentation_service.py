import re
from typing import List, Dict


class LyricsSegmentationService:
    """
    Splits lyrics into singable phrases and estimates syllable counts.
    No AI. No language assumptions. Safe & deterministic.
    """

    VOWEL_PATTERN = re.compile(r"[aeiouyAEIOUY]+")

    def segment(self, lyrics: str) -> List[Dict]:
        """
        Returns a list of lyric segments with estimated syllables.
        """

        lines = [
            line.strip()
            for line in lyrics.split("\n")
            if line.strip()
        ]

        segments = []

        for line in lines:
            syllables = self._estimate_syllables(line)
            segments.append({
                "text": line,
                "syllables": syllables
            })

        return segments

    def _estimate_syllables(self, text: str) -> int:
        """
        Very lightweight syllable approximation.
        Works reasonably well for Indian & English lyrics.
        """

        # Remove punctuation
        clean = re.sub(r"[^a-zA-Z\s]", "", text)

        words = clean.split()
        count = 0

        for word in words:
            # Count vowel groups as syllables
            matches = self.VOWEL_PATTERN.findall(word)
            count += max(1, len(matches))

        return count

