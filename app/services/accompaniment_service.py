import subprocess
import sys
import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SCRIPT = os.path.join(BASE_DIR, "smart_arranger_style_aware.py")
PYTHON = sys.executable


def run(cmd: str):
    subprocess.run(cmd, shell=True, check=True)


def generate_accompaniment(input_path: str):
    uid = str(uuid.uuid4())

    # =================================================
    # ⭐ STEP 1 — HARD COMPRESS AUDIO (IMPORTANT)
    # converts ANYTHING -> small mono wav
    # =================================================
    wav_path = f"/tmp/{uid}_compressed.wav"

    run(
        f'ffmpeg -y -i "{input_path}" '
        f'-ac 1 '              # mono
        f'-ar 16000 '          # lower sample rate
        f'-b:a 64k '           # compress
        f'-map_metadata -1 '
        f'"{wav_path}"'
    )

    # =================================================
    # ⭐ STEP 2 — run arranger
    # =================================================
    run(f'"{PYTHON}" "{SCRIPT}" "{wav_path}"')

    # =================================================
    return "final_video.mp4"

