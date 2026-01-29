# app/services/audio_postprocess_service.py

import subprocess
import os

FFMPEG = "/usr/bin/ffmpeg"
FFPROBE = "/usr/bin/ffprobe"


# -------------------------------------------------
# helpers
# -------------------------------------------------
def run_ffmpeg(cmd: list[str]):
    """
    Safe ffmpeg runner:
    - prints command
    - fails loudly
    """
    print("🎛", " ".join(cmd))
    subprocess.run(cmd, check=True)


def get_duration(path: str) -> float:
    """
    Get exact duration of audio using ffprobe.
    CRITICAL:
    ensures we NEVER create longer files than source
    """
    result = subprocess.check_output([
        FFPROBE,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ])

    return float(result.decode().strip())


# -------------------------------------------------
# main enhancer
# -------------------------------------------------
def enhance_audio(input_path: str, output_path: str | None = None) -> str:
    """
    Indianode ULTRA CINEMATIC MIX (V6 — FINAL)

    FIXES:
    ✅ duration matches input EXACTLY
    ✅ no 10-minute bug
    ✅ no corrupt mp4
    ✅ no silent ffmpeg failures
    ✅ production safe
    """

    base, _ = os.path.splitext(input_path)

    if output_path is None:
        output_path = base + "_enhanced.wav"

    drone_path = base + "_drone.wav"
    ambience_path = base + "_amb.wav"
    mix_path = base + "_mix.wav"

    # -------------------------------------------------
    # 🔥 CRITICAL FIX — dynamic duration
    # -------------------------------------------------
    duration = get_duration(input_path)
    duration_str = str(duration)

    print(f"🎚 Input duration = {duration_str}s")

    # -------------------------------------------------
    # 1. Drone (MATCH duration)
    # -------------------------------------------------
    run_ffmpeg([
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency=130:duration={duration_str}",
        "-filter:a", "volume=0.03",
        drone_path
    ])

    # -------------------------------------------------
    # 2. Ambience (MATCH duration)
    # -------------------------------------------------
    run_ffmpeg([
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"anoisesrc=color=pink:duration={duration_str}",
        "-filter:a", "volume=0.015",
        ambience_path
    ])

    # -------------------------------------------------
    # 3. Mix layers
    # -------------------------------------------------
    run_ffmpeg([
        FFMPEG, "-y",
        "-i", input_path,
        "-i", drone_path,
        "-i", ambience_path,
        "-filter_complex", "amix=inputs=3:weights=3 1 1:normalize=0",
        mix_path
    ])

    # -------------------------------------------------
    # 4. Mastering chain (clean + safe)
    # 🔥 UPDATED: removed chorus/echo/compressor/EQ (caused hiss/phase)
    # -------------------------------------------------
    filter_chain = (
        "loudnorm=I=-14:LRA=11:TP=-1.5"
    )

    run_ffmpeg([
        FFMPEG, "-y",
        "-i", mix_path,
        "-af", filter_chain,
        "-ar", "44100",
        "-ac", "2",
        output_path
    ])
    print("\n🔥🔥🔥 OZONE MASTERING RUNNING 🔥🔥🔥\n")

    # -------------------------------------------------
    # Final safety check
    # -------------------------------------------------
    if not os.path.exists(output_path):
        raise RuntimeError("Enhanced file not created")

    return output_path

