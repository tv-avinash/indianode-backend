import numpy as np
import librosa
import soundfile as sf
from scipy.signal import fftconvolve


class AudioMixer:
    """
    Studio Blend Mixer (final polish)

    Adds:
    ✓ ducking
    ✓ stronger bgm
    ✓ stereo width
    ✓ soft vocal compression
    ✓ tiny room ambience (key!)
    ✓ glued mix

    Result:
    Vocal sits INSIDE music, not on top
    """

    def __init__(
        self,
        sr=44100,
        music_gain_db=5,
        vocal_gain_db=-5,      # softer vocal
        music_duck_db=5,
        frame_ms=40
    ):
        self.sr = sr
        self.music_gain_db = music_gain_db
        self.vocal_gain_db = vocal_gain_db
        self.music_duck_db = music_duck_db
        self.frame = int(sr * frame_ms / 1000)

    # -------------------------

    def db(self, x):
        return 10 ** (x / 20)

    def rms(self, x):
        return np.sqrt(np.mean(x**2) + 1e-9)

    # -------------------------
    # tiny room reverb
    # -------------------------

    def room_reverb(self, x):
        ir_len = int(self.sr * 0.08)  # 80 ms tiny room
        ir = np.exp(-np.linspace(0, 4, ir_len))
        wet = fftconvolve(x, ir)[:len(x)]
        return x * 0.85 + wet * 0.15  # subtle only

    # -------------------------
    # soft compressor
    # -------------------------

    def compress(self, x, thresh=0.2, ratio=3):

        out = np.copy(x)

        for i in range(len(x)):
            s = x[i]
            if abs(s) > thresh:
                excess = abs(s) - thresh
                s = np.sign(s) * (thresh + excess / ratio)
            out[i] = s

        return out

    # -------------------------
    # stereo widen
    # -------------------------

    def widen(self, mono, width=0.35):
        left = mono * (1 + width)
        right = mono * (1 - width)
        return np.vstack([left, right])

    # -------------------------
    # main mix
    # -------------------------

    def mix(self, vocal_path, music_path, out_path):

        print("Loading audio...")

        vocal, _ = librosa.load(vocal_path, sr=self.sr, mono=True)
        music, _ = librosa.load(music_path, sr=self.sr, mono=True)

        L = min(len(vocal), len(music))
        vocal = vocal[:L]
        music = music[:L]

        # gains
        vocal *= self.db(self.vocal_gain_db)
        music *= self.db(self.music_gain_db)

        # soften vocal
        vocal = self.compress(vocal)
        vocal = self.room_reverb(vocal)

        out = np.zeros(L)

        threshold = 0.02

        for i in range(0, L, self.frame):

            v = vocal[i:i+self.frame]
            m = music[i:i+self.frame]

            if self.rms(v) > threshold:
                m *= self.db(-self.music_duck_db)

            out[i:i+self.frame] = v + m

        stereo = self.widen(out)

        peak = np.max(np.abs(stereo))
        if peak > 0.95:
            stereo = stereo / peak * 0.95

        sf.write(out_path, stereo.T, self.sr)

        print("✅ Final studio blend ready:", out_path)

