import os
import sys
from pathlib import Path

# Make DiffSinger available to Python
DIFFSINGER_ROOT = Path(__file__).resolve().parents[2] / "external" / "DiffSinger"
sys.path.append(str(DIFFSINGER_ROOT))

class DiffSingerService:
    """
    Inference-only wrapper for DiffSinger.
    No training, no model hacking.
    """

    def __init__(self):
        self.root = DIFFSINGER_ROOT
        self.ready = True
        print("[DiffSingerService] DiffSinger backend ready")

    def sing(
        self,
        lyrics: str,
        output_path: str,
        voice: str = "auto",
        language: str = "auto",
        style: str = "auto"
    ):
        """
        Placeholder interface.
        Real inference will be wired next step.
        """
        raise NotImplementedError(
            "DiffSinger inference wiring is next step"
        )

