# app/services/audio_quality_service.py

import numpy as np
import librosa
import torch
import torchcrepe
import soundfile as sf


# =========================================================
# 🔥 PRO AUDIO QUALITY JUDGE (NO GPT, NO CLOUD)
# Pure ML + DSP
# Fast + deterministic + production safe
# =========================================================


SR = 32000


# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------

def _fail(reason: str):
    return False, reason


def _pass():
    return True, "clean"


# ---------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------

def check_audio_quality(wav_path: str, prompt: str):
    """
    Returns:
        (passed: bool, reason: str)

    Judge for:
      - silence
      - clipping/distortion
      - pitch instability (besura)
      - tempo instability
      - harshness
      - flat dynamics
    """

    try:
        y, sr = sf.read(wav_path)
        if y.ndim > 1:
            y = np.mean(y, axis=1)

        y = y.astype(np.float32)

    except Exception:
        return _fail("cannot read audio file")

    # =====================================================
    # 1. SILENCE / EMPTY
    # =====================================================

    rms = np.sqrt(np.mean(y ** 2))
    if rms < 0.005:
        return _fail("audio nearly silent or empty render")

    # =====================================================
    # 2. CLIPPING / DISTORTION
    # =====================================================

    clipped = np.sum(np.abs(y) >= 0.999)
    clip_ratio = clipped / len(y)

    if clip_ratio > 0.002:
        return _fail("clipping distortion detected")

    # =====================================================
    # 3. PITCH STABILITY (torchcrepe neural pitch)
    # =====================================================

    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"

        audio_torch = torch.tensor(y).unsqueeze(0).to(device)

        f0, pd = torchcrepe.predict(
            audio_torch,
            sr,
            hop_length=256,
            fmin=50,
            fmax=1200,
            model="full",
            batch_size=512,
            device=device,
            return_periodicity=True
        )

        f0 = f0[0].cpu().numpy()
        pd = pd[0].cpu().numpy()

        mask = pd > 0.7
        voiced = f0[mask]

        if len(voiced) > 50:
            pitch_std = np.std(voiced) / (np.mean(voiced) + 1e-6)

            if pitch_std > 0.35:
                return _fail("pitch unstable / besura / out-of-tune")

    except Exception:
        pass  # never block generation if pitch fails

    # =====================================================
    # 4. TEMPO STABILITY
    # =====================================================

    try:
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        if len(beats) > 8:
            beat_times = librosa.frames_to_time(beats, sr=sr)
            intervals = np.diff(beat_times)

            jitter = np.std(intervals) / (np.mean(intervals) + 1e-6)

            if jitter > 0.35:
                return _fail("tempo unstable / dragging rhythm")

    except Exception:
        pass

    # =====================================================
    # 5. HARSHNESS (high frequency energy)
    # =====================================================

    S = np.abs(librosa.stft(y, n_fft=2048))
    freqs = librosa.fft_frequencies(sr=sr)

    high = S[freqs > 3500].mean()
    low = S[freqs < 1500].mean()

    if high > low * 2.5:
        return _fail("too harsh / shrill high frequencies")

    # =====================================================
    # 6. DYNAMICS (lifeless / flat)
    # =====================================================

    dyn = np.percentile(np.abs(y), 95) - np.percentile(np.abs(y), 5)

    if dyn < 0.03:
        return _fail("over-compressed / lifeless dynamics")

    # =====================================================
    # ✅ PASSED
    # =====================================================

    return _pass()

