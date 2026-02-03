# app/services/mastering/mastering_service.py

import subprocess
from pathlib import Path


# -------------------------------------------------
# PATHS
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

REAPER = "/home/supersu/opt/REAPER/reaper"
TEMPLATE = BASE_DIR / "indianode_master_template.rpp"


# -------------------------------------------------
# MASTER
# -------------------------------------------------

def master_audio(input_wav: str, output_wav: str):
    """
    Headless mastering using REAPER batchconvert mode.
    This mode does NOT touch audio drivers (safe for servers).
    """

    input_wav = str(Path(input_wav).resolve())
    output_wav = str(Path(output_wav).resolve())

    print("\n🔥 OZONE MASTERING (TRUE HEADLESS BATCH MODE)")
    print("IN :", input_wav)
    print("OUT:", output_wav)

    cmd = [
        REAPER,
        "-nosplash",
        "-batchconvert",          # ⭐ THIS IS THE FIX
        str(TEMPLATE),
        input_wav,
        output_wav
    ]

    print("CMD:", " ".join(cmd))

    subprocess.run(cmd, check=True)

    return output_wav

