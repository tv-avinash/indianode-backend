# app/services/audio_cleanup_service.py

import subprocess
import os

FFMPEG = "/usr/bin/ffmpeg"


def _run(cmd: list[str]):
    print("🧹", " ".join(cmd))
    subprocess.run(cmd, check=True)


def cleanup_audio(input_path: str, output_path: str | None = None) -> str:
    """
    WORLD-CLASS STUDIO CLEANUP STAGE (SAFE)

    Purpose:
    Fix technical defects BEFORE any enhancement/mastering.

    Removes:
    ✓ hiss
    ✓ krr noise
    ✓ low rumble
    ✓ clicks/pops
    ✓ tiny cuts/glitches
    ✓ DC offset
    ✓ clipping edges

    Does NOT change:
    ✓ tone
    ✓ music feel
    ✓ dynamics (very transparent)

    100% ffmpeg native → production safe
    """

    base, _ = os.path.splitext(input_path)

    if output_path is None:
        output_path = base + "_clean.wav"

    filter_chain = (
        # remove sub rumble / AC hum
        "highpass=f=60,"

        # spectral denoise (very gentle)
        "afftdn=nf=-28:nt=w:om=o,"

        # remove clicks / tiny discontinuities
        "adeclick=window=55:overlap=75,"

        # fix clipped edges / DC issues
        "adeclip,"

        # small headroom for later FX
        "volume=0.97"
    )

    _run([
        FFMPEG, "-y",
        "-i", input_path,
        "-af", filter_chain,
        "-ar", "44100",
        "-ac", "2",
        output_path
    ])

    if not os.path.exists(output_path):
        raise RuntimeError("Cleanup failed")

    return output_path

