# app/services/audio_technical_qa.py

"""
Technical audio QA (NOT AI)

Detects:
✓ clipping
✓ hiss/noise floor
✓ crackles / spikes
✓ DC offset

Repairs automatically using ffmpeg filters.

This runs FAST and is deterministic.
"""

import os
import subprocess
import soundfile as sf
import numpy as np


FFMPEG = "/usr/bin/ffmpeg"


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _rms(x):
    return np.sqrt(np.mean(x ** 2))


# -------------------------------------------------
# Check quality
# -------------------------------------------------

def check_audio_technical_quality(wav_path: str):
    """
    Returns:
        (passed: bool, issues: list[str])
    """

    data, sr = sf.read(wav_path)

    if data.ndim > 1:
        data = np.mean(data, axis=1)

    issues = []

    peak = np.max(np.abs(data))
    rms = _rms(data)

    # ---------------------------------
    # clipping
    # ---------------------------------
    if peak >= 0.999:
        issues.append("clipping")

    # ---------------------------------
    # noise floor / hiss
    # ---------------------------------
    if rms < 0.002:
        issues.append("too_low_volume")

    if rms > 0 and peak / rms > 50:
        issues.append("hiss_or_noise")

    # ---------------------------------
    # crackles (spikes)
    # ---------------------------------
    diffs = np.abs(np.diff(data))
    if np.max(diffs) > 0.9:
        issues.append("crackles")

    # ---------------------------------
    # DC offset
    # ---------------------------------
    if abs(np.mean(data)) > 0.01:
        issues.append("dc_offset")

    return len(issues) == 0, issues


# -------------------------------------------------
# Repair
# -------------------------------------------------

def repair_audio_technical(wav_path: str):
    """
    Uses ffmpeg filters to fix problems.
    """

    fixed_path = wav_path.replace(".wav", "_fixed.wav")

    cmd = [
        FFMPEG, "-y",
        "-i", wav_path,
        "-af",
        ",".join([
            "adeclip",         # fix clipping
            "highpass=f=40",  # remove rumble/DC
            "lowpass=f=16000",
            "afftdn=nf=-25",  # noise reduction
            "dynaudnorm",     # normalize dynamics
        ]),
        fixed_path
    ]

    subprocess.run(cmd, check=True)

    return os.path.abspath(fixed_path)

