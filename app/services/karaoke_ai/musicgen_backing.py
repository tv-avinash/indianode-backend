import torch
import librosa
import soundfile as sf
import numpy as np
from audiocraft.models import MusicGen


class MusicGenBacking:
    """
    Professional MusicGen backing generator.

    KEY:
    - split long songs into chunks
    - generate each separately
    - stitch back

    Prevents drift + crying artifacts.
    """

    def __init__(self, chunk_seconds=20):
        print("🚀 Loading MusicGen MELODY model...")

        self.model = MusicGen.get_pretrained("facebook/musicgen-melody")

        self.chunk_seconds = chunk_seconds

        self.model.set_generation_params(
            temperature=0.9,
            top_k=250,
            cfg_coef=3.0
        )

    # -------------------------------------------------
    def generate_chunk(self, chunk, sr, prompt):

        duration = len(chunk) / sr
        self.model.set_generation_params(duration=duration)

        wav_tensor = torch.tensor(chunk).unsqueeze(0)

        with torch.no_grad():
            out = self.model.generate_with_chroma(
                descriptions=[prompt],
                melody_wavs=wav_tensor,
                melody_sample_rate=sr
            )

        return out[0].cpu().numpy().T

    # -------------------------------------------------
    def generate(self, vocal_path, out_path, style="carnatic classical instrumental"):

        print("🎤 Loading vocal...")
        wav, sr = librosa.load(vocal_path, sr=32000, mono=True)

        chunk_len = int(sr * self.chunk_seconds)

        prompt = (
            f"{style}, only instruments, "
            "veena, mridangam, flute, strings, studio quality, no vocals"
        )

        pieces = []

        print("🎼 Generating in chunks...")

        for i in range(0, len(wav), chunk_len):
            chunk = wav[i:i+chunk_len]

            print(f"   chunk {i//chunk_len + 1}")

            audio = self.generate_chunk(chunk, sr, prompt)

            pieces.append(audio)

        final = np.concatenate(pieces, axis=0)

        sf.write(out_path, final, 32000)

        print("✅ Backing saved:", out_path)

