# app/services/karaoke_ai/studio_mixer.py

import numpy as np
import librosa
import soundfile as sf
import subprocess


class StudioMixer:
    """
    Studio-grade automatic mixer

    Goal:
    Make vocal sit INSIDE music, not above it.
    """

    def __init__(self, sr=44100):
        self.sr = sr

    # =========================================================
    # utils
    # =========================================================

    def _normalize(self, x):
        peak = np.max(np.abs(x)) + 1e-9
        return x / peak

    def _match_length(self, a, b):
        L = max(len(a), len(b))
        a = np.pad(a, (0, L - len(a)))
        b = np.pad(b, (0, L - len(b)))
        return a, b

    # =========================================================
    # vocal compression (IMPORTANT)
    # =========================================================

    def _compress(self, x, threshold=0.25, ratio=4.0):
        """
        Simple soft compressor
        reduces 'bold mic voice' effect
        """
        y = x.copy()

        mask = np.abs(y) > threshold
        y[mask] = np.sign(y[mask]) * (
            threshold + (np.abs(y[mask]) - threshold) / ratio
        )

        return y

    # =========================================================
    # small room reverb (puts vocal in same space as bgm)
    # =========================================================

    def _reverb(self, x, amount=0.12):
        delay = int(0.03 * self.sr)  # 30ms room reflection
        wet = np.pad(x, (delay, 0))[:-delay]
        return x + wet * amount

    # =========================================================
    # main mix
    # =========================================================

    def mix(
        self,
        vocal_path: str,
        music_path: str,
        out_path: str,
        vocal_gain_db: float = -4.0,
        music_gain_db: float = +4.0,
    ):
        print("🎧 Loading audio...")

        vocal, _ = librosa.load(vocal_path, sr=self.sr, mono=True)
        music, _ = librosa.load(music_path, sr=self.sr, mono=True)

        vocal, music = self._match_length(vocal, music)

        # =====================================================
        # Gains
        # =====================================================

        vocal *= 10 ** (vocal_gain_db / 20)
        music *= 10 ** (music_gain_db / 20)

        # =====================================================
        # Studio processing
        # =====================================================

        vocal = self._compress(vocal)     # tame peaks
        vocal = self._reverb(vocal)       # glue to mix

        # =====================================================
        # Mix
        # =====================================================

        mix = vocal + music

        # limiter
        mix = self._normalize(mix) * 0.95

        temp = out_path.replace(".wav", "_temp.wav")
        sf.write(temp, mix, self.sr)

        # =====================================================
        # Loudness normalize (pro sound)
        # =====================================================

        print("🎚 Applying mastering loudness normalization...")

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", temp,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            out_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"✅ Studio mix ready: {out_path}")

