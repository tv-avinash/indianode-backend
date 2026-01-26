# app/services/classical_postprocess_service.py

import subprocess
import os

FFMPEG = "/usr/bin/ffmpeg"
FFPROBE = "/usr/bin/ffprobe"


def run(cmd: list[str]):
    print("🎻", " ".join(cmd))
    subprocess.run(cmd, check=True)


def classical_polish_audio(input_path: str, output_path: str | None = None) -> str:
    """
    PURE CLASSICAL STUDIO POLISH (NO CINEMATIC COLORING)

    Goals:
    ✅ preserve natural tone
    ✅ keep mono feel
    ✅ remove harshness
    ✅ control peaks gently
    ✅ normalize loudness
    ❌ NO drone
    ❌ NO ambience
    ❌ NO chorus
    ❌ NO echo
    ❌ NO widening
    ❌ NO ozone

    This is basically what a real acoustic engineer would do.
    """

    base, _ = os.path.splitext(input_path)

    if output_path is None:
        output_path = base + "_classical.wav"

    filter_chain = (
        # remove rumble
        "highpass=f=60,"

        # soften harsh highs (flute/veena safe)
        "equalizer=f=7000:width_type=o:width=2:g=-2,"

        # very gentle compression only
        "acompressor=threshold=-18dB:ratio=1.5:attack=20:release=150,"

        # safe broadcast loudness
        "loudnorm=I=-18:LRA=12:TP=-2"
    )

    run([
        FFMPEG, "-y",
        "-i", input_path,
        "-af", filter_chain,
        "-ar", "44100",
        "-ac", "2",
        output_path
    ])

    if not os.path.exists(output_path):
        raise RuntimeError("Classical polish failed")

    return output_path

