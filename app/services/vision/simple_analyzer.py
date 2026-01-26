# app/services/vision/simple_analyzer.py

class SimpleVisionAnalyzer:
    """
    Placeholder vision analyzer.
    This ensures:
    - Backend boots correctly
    - API contract is stable
    - Zero rework when upgrading to real vision models
    """

    def analyze(self, image_bytes: bytes) -> dict:
        # TEMP: deterministic fallback
        # Real vision model can replace this later
        return {
            "mood": "calm",
            "style": "cinematic",
            "suggested_prompt": (
                "Calm cinematic instrumental music with warm atmosphere, "
                "slow tempo, emotional undertones."
            )
        }

