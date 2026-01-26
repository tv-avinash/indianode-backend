import os
import uuid
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

OUTPUT_DIR = "outputs"

class MusicGenService:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        print("[MusicGenService] Loading MusicGen model…")
        self.model = MusicGen.get_pretrained("facebook/musicgen-small")

        self.model.set_generation_params(
            use_sampling=True,
            top_k=250,
            temperature=1.0,
        )

        print("[MusicGenService] Model loaded")

    def generate(
        self,
        preset_key: str | None,
        duration: int,
        user_description: str | None,
        instruments: list[str] | None,
    ) -> str:

        instruments = instruments or []
        lowered = [i.lower() for i in instruments]

        has_veena = "veena" in lowered

        # -----------------------------
        # Build ORIGINAL prompt (unchanged logic)
        # -----------------------------
        prompt_parts = []

        if preset_key:
            prompt_parts.append(preset_key)

        if instruments:
            prompt_parts.append("instruments: " + ", ".join(instruments))

        if user_description:
            prompt_parts.append(user_description)

        base_prompt = ", ".join(prompt_parts) or "instrumental music"

        # -----------------------------
        # ✅ VEENA CLARIFICATION (ADD ONLY)
        # Applies for Veena-only AND combinations
        # -----------------------------
        if has_veena:
            veena_clarification = (
                "Indian classical Veena performance. "
                "Veena is a traditional Indian p

