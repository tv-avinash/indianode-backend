import os
import subprocess
import soundfile as sf
import numpy as np
from scipy.signal import fftconvolve


class AIMastering:
    """
    Final musical mastering chain

    Adds:
    - Demucs separation
    - Vocal softening
    - SMALL room reverb (glue)
    - Stereo widening
    - Loudness normalize

    This removes karaoke feeling completely.
    """

    def db_to_gain(self, db):
        return 10 ** (db / 20)

    # -------------------------
    # simple compressor
    # -------------------------
    def compress(self, x, threshold=0.25, ratio=3):
        out = np.copy(x)
        mask = np.abs(out) > threshold
        out[mask] = np.sign(out[mask]) * (
            threshold + (np.abs(out[mask]) - threshold) / ratio
        )
        return out

    # -------------------------
    # tiny room reverb (MAGIC step)
    # -------------------------
    def add_room_reverb(self, x, sr, amount=0.12):
        length = int(0.04 * sr)  # 40ms room
        impulse = np.exp(-np.linspace(0, 4, length))

        if x.ndim == 1:
            wet = fftconvolve(x, impulse, mode="full")[:len(x)]
        else:
            wet = np.vstack([
                fftconvolve(x[:,0], impulse, mode="full")[:len(x)],
                fftconvolve(x[:,1], impulse, mode="full")[:len(x)]
            ]).T

        return (1 - amount) * x + amount * wet

    # -------------------------
    # stereo widen
    # -------------------------
    def widen(self, stereo, amount=1.4):
        mid = (stereo[:,0] + stereo[:,1]) / 2
        side = (stereo[:,0] - stereo[:,1]) / 2
        side *= amount
        left = mid + side
        right = mid - side
        return np.stack([left, right], axis=1)

    # -------------------------
    # normalize
    # -------------------------
    def normalize(self, x, target=0.98):
        peak = np.max(np.abs(x))
        if peak > 0:
            x = x / peak * target
        return x

    # -------------------------
    # MAIN
    # -------------------------
    def mix(self, input_wav, out_path):
        print("🎧 Separating with Demucs...")

        subprocess.run(["demucs", "-n", "htdemucs", input_wav], check=True)

        base = os.path.splitext(os.path.basename(input_wav))[0]
        stem_dir = f"separated/htdemucs/{base}"

        vocals, sr = sf.read(f"{stem_dir}/vocals.wav")
        drums, _ = sf.read(f"{stem_dir}/drums.wav")
        bass, _ = sf.read(f"{stem_dir}/bass.wav")
        other, _ = sf.read(f"{stem_dir}/other.wav")

        min_len = min(len(vocals), len(drums), len(bass), len(other))

        vocals = vocals[:min_len]
        music = (drums + bass + other)[:min_len]

        print("🎛 Mixing musically...")

        # soften vocal
        vocals = self.compress(vocals)
        vocals *= self.db_to_gain(-3)

        # 🔥 ADD ROOM REVERB (key step)
        vocals = self.add_room_reverb(vocals, sr, amount=0.10)

        # stronger + wider bgm
        music = self.widen(music, 1.5)
        music *= self.db_to_gain(+3)

        mix = vocals + music

        mix = self.normalize(mix)

        print("💾 Exporting final master...")

        sf.write(out_path, mix, sr)

        print("✅ Done:", out_path)

