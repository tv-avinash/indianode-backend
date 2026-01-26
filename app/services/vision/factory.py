# app/services/vision/factory.py

from app.services.vision.analyzer import VisionAnalyzer

_ANALYZER = None


def get_vision_analyzer() -> VisionAnalyzer:
    global _ANALYZER

    if _ANALYZER is None:
        _ANALYZER = VisionAnalyzer()

    return _ANALYZER

