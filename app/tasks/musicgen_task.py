# app/tasks/musicgen_task.py

import os
import torch
import soundfile as sf
import subprocess

from audiocraft.models import MusicGen
from celery import shared_task

from app.services.job_store import job_store
from app.services.audio_postprocess_service import enhance_audio
from app.services.classical_postprocess_service import classical_polish_audio
from app.services.audio_quality_service import check_audio_quality
from app.services.audio_repair_service import repair_generation
from app.services.audio_technical_qa import (
    check_audio_technical_quality,
    repair_audio_technical
)


# -------------------------------------------------
# Paths (UNCHANGED)
# -------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FFMPEG = "/usr/bin/ffmpeg"

_MODEL = None
_MODEL_NAME = None

MAX_RETRIES = 4


# -------------------------------------------------
# Load model once (UNCHANGED)
# -------------------------------------------------
def load_musicgen(mode: str):
    global _MODEL, _MODEL_NAME

    target_model = (
        "facebook/musicgen-small"
        if mode == "classical"
        else "facebook/musicgen-large"
    )

    if _MODEL is None or _MODEL_NAME != target_model:
        print(f"🎵 Loading MusicGen: {target_model}")

        _MODEL = MusicGen.get_pretrained(target_model)
        _MODEL_NAME = target_model

        _MODEL.set_generation_params(
            duration=10,
            use_sampling=True,
            top_k=250,
            temperature=1.0,
            cfg_coef=3.0
        )

    return _MODEL


# -------------------------------------------------
# Celery Task
# -------------------------------------------------
@shared_task(name="musicgen.generate", queue="gpu")
def generate_music_task(job_id: str, payload: dict):

    try:
        print(f"\n🎼 Generating music | job={job_id}")
        job_store.set_running(job_id)

        prompt = payload.get("prompt", "")
        mode = payload.get("mode", "cinematic")
        duration = int(payload.get("duration", 10))
        image_path = payload.get("image_path")   # ⭐ already passed from API

        model = load_musicgen(mode)

        # =================================================
        # GENERATE
        # =================================================
        with torch.no_grad():
            wav = model.generate([prompt])[0]

        wav_path = os.path.abspath(
            os.path.join(OUTPUT_DIR, f"{job_id}.wav")
        )

        sf.write(
            wav_path,
            wav.cpu().numpy().T,
            samplerate=32000,
            subtype="PCM_16"
        )

        # =================================================
        # POST PROCESS (UNCHANGED)
        # =================================================
        if mode == "classical":
            wav_path = os.path.abspath(classical_polish_audio(wav_path))
        else:
            wav_path = os.path.abspath(enhance_audio(wav_path))

        # =================================================
        # MP4 CREATION (ONLY THIS BLOCK UPDATED)
        # =================================================
        mp4_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

        if image_path and os.path.exists(image_path):
            print("🖼 Using uploaded image:", image_path)

            subprocess.run([
                FFMPEG, "-y",
                "-loop", "1",
                "-i", image_path,
                "-i", wav_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-shortest",
                mp4_path
            ], check=True)

        else:
            print("🎨 No image → generating indianode branded frame")

            subprocess.run([
                FFMPEG, "-y",
                "-f", "lavfi",
                "-i",
                f"color=c=black:s=1080x1080:r=30:d={duration},"
                "drawtext=text='indianode.com':"
                "fontcolor=white:fontsize=60:"
                "x=(w-text_w)/2:y=(h-text_h)/2",
                "-i", wav_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-shortest",
                mp4_path
            ], check=True)

        # =================================================
        job_store.set_done(job_id, mp4_path)
        return mp4_path

    except Exception as e:
        print("❌ Internal exception:", e)
        job_store.set_error(
            job_id,
            "This prompt needs a small tweak for best results. Please try again."
        )
        return

