# app/services/audio_quality_service.py

import numpy as np
import librosa
import torch
import torchcrepe
import soundfile as sf


SR = 32000


# =========================================================
# helpers
# =========================================================

def _fail(reason):
    return False, reason


def _pass():
    return True, "clean"


# =========================================================
# musical checks
# =========================================================

def _pitch_stable(y, sr):

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

    if len(voiced) < 50:
        return True

    pitch_std = np.std(voiced) / (np.mean(voiced) + 1e-6)

    return pitch_std < 0.35


def _scale_consistency_ok(y, sr):

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    energy = chroma.sum(axis=1)

    top7 = np.argsort(energy)[-7:]
    notes = np.argmax(chroma, axis=0)

    outside = np.sum(~np.isin(notes, top7))
    ratio = outside / len(notes)

    return ratio < 0.30


def _tempo_stable(y, sr):

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    if len(beats) < 8:
        return True

    beat_times = librosa.frames_to_time(beats, sr=sr)
    intervals = np.diff(beat_times)

    jitter = np.std(intervals) / (np.mean(intervals) + 1e-6)

    return jitter < 0.35


# =========================================================
# technical
# =========================================================

def _silence_ok(y):
    return np.sqrt(np.mean(y**2)) >= 0.005


def _clipping_ok(y):
    return np.mean(np.abs(y) >= 0.999) < 0.002


def _harshness_ok(y, sr):
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)

    high = S[freqs > 3500].mean()
    low = S[freqs < 1500].mean()

    return high <= low * 2.5


def _dynamics_ok(y):
    dyn = np.percentile(np.abs(y), 95) - np.percentile(np.abs(y), 5)
    return dyn >= 0.03


# =========================================================
# MAIN
# =========================================================

def check_audio_quality(wav_path: str, prompt: str, mode: str):

    y, sr = sf.read(wav_path)

    if y.ndim > 1:
        y = np.mean(y, axis=1)

    y = y.astype(np.float32)

    print(f"🎧 Quality Judge Mode = {mode.upper()}")

    # always run technical
    if not _silence_ok(y):
        return _fail("silent")

    if not _clipping_ok(y):
        return _fail("clipping")

    if not _harshness_ok(y, sr):
        return _fail("harsh")

    if not _dynamics_ok(y):
        return _fail("flat dynamics")

    # musical strict only for classical
    if mode == "classical":

        if not _pitch_stable(y, sr):
            return _fail("pitch unstable")

        if not _scale_consistency_ok(y, sr):
            return _fail("off-key")

        if not _tempo_stable(y, sr):
            return _fail("tempo unstable")

    return _pass()

