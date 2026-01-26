from typing import List, Dict


class VocalPacingService:
    """
    Converts lyric segments into time-aligned vocal pacing.
    """

    def pace(
        self,
        segments: List[Dict],
        syllables_per_second: float,
        style: str = "default"
    ) -> List[Dict]:
        """
        Args:
            segments: [{text, syllables}]
            syllables_per_second: inferred tempo value
            style: future extension (default / devotional / cinematic)

        Returns:
            List of segments with duration and pause
        """

        paced_segments = []

        for i, seg in enumerate(segments):
            syllables = seg["syllables"]

            # Core vocal duration
            duration = syllables / syllables_per_second

            # Human singing adjustments
            sustain = self._sustain_factor(style)
            pause = self._pause_after_line(i, len(segments), style)

            duration = round(duration * sustain, 2)

            paced_segments.append({
                "text": seg["text"],
                "syllables": syllables,
                "sing_duration_sec": duration,
                "post_pause_sec": pause
            })

        return paced_segments

    def _sustain_factor(self, style: str) -> float:
        """
        Controls how much singers stretch syllables.
        """
        if style == "devotional":
            return 1.25
        if style == "cinematic":
            return 1.4
        return 1.15  # default human singing

    def _pause_after_line(self, index: int, total: int, style: str) -> float:
        """
        Natural breathing pauses between lines.
        """
        if index == total - 1:
            return 0.0  # no pause after last line

        if style == "devotional":
            return 0.6
        if style == "cinematic":
            return 0.8
        return 0.4

