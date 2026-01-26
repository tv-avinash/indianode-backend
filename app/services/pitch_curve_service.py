import random
from typing import List, Dict


class PitchCurveService:
    """
    Generates pitch (F0) curves per phoneme.
    AI-light baseline, raga-safe, upgradeable.
    """

    def __init__(self):
        # Reference tonic (Sa) in Hz — adjustable later
        self.tonic_hz = 220.0  # A3 ≈ Sa

    def _base_scale(self, style: str):
        """
        Soft scale skeletons (NOT hard ragas).
        """
        if style == "carnatic":
            return [1.0, 1.125, 1.25, 1.333, 1.5, 1.667]
        if style == "western":
            return [1.0, 1.122, 1.26, 1.335, 1.498]
        return [1.0, 1.2, 1.33, 1.5]

    def generate(
        self,
        phoneme_units: List[Dict],
        mood: str = "neutral",
        style: str = "carnatic"
    ) -> List[Dict]:
        scale = self._base_scale(style)

        output = []
        last_pitch = self.tonic_hz

        for unit in phoneme_units:
            multiplier = random.choice(scale)
            target_pitch = self.tonic_hz * multiplier

            # Mood-based movement
            if mood == "devotional":
                curve = [
                    last_pitch,
                    (last_pitch + target_pitch) / 2,
                    target_pitch
                ]
            elif mood == "romantic":
                curve = [
                    last_pitch,
                    target_pitch * 0.98,
                    target_pitch
                ]
            else:
                curve = [target_pitch]

            output.append({
                "ph": unit["ph"],
                "duration_sec": unit["duration_sec"],
                "f0_curve_hz": [round(p, 2) for p in curve]
            })

            last_pitch = target_pitch

        return output

