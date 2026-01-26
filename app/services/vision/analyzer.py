# app/services/vision/analyzer.py

class VisionAnalyzer:
    """
    VisionAnalyzer v1 (SAFE STUB)

    This class is intentionally simple.
    It guarantees a stable output schema so that
    frontend + future LLMs can plug in without rework.
    """

    def analyze(self, image_bytes: bytes) -> dict:
        # ⚠️ Stub logic (deterministic, non-random)
        # Will be replaced by LLM / vision model later

        return {
            "mood": "calm",
            "energy": "medium",
            "style": "cinematic indian",
            "description": (
                "A calm, cinematic Indian atmosphere with emotional undertones. "
                "Suitable for melodic instruments, slow tempo, and expressive phrasing."
            ),
            "suggested_prompt": (
                "Calm cinematic Indian music with emotional depth, "
                "slow tempo, melodic lead, soft accompaniment, and warm ambience."
            ),
        }

