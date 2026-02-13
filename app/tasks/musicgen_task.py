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
from app.music_prompt.quality_guardrails import apply_quality_guardrails
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

        # ✅ ALWAYS apply (classical + cinematic)
        print("🎼 PROMPT RECEIVED BY WORKER:", prompt)
        mode = payload.get("mode", "cinematic")
        duration = int(payload.get("duration", 10))
        image_path = payload.get("image_path")   # ⭐ already passed from API

        model = load_musicgen(mode)
        model.set_generation_params(duration=duration)

        # =================================================
        # GENERATE
        # =================================================
        current_prompt = prompt
        raw_path = None
        ok = False
        reason = ""

        # ============================================
        # RETRY LOOP (RAW ONLY — NO POSTPROCESS YET)
        # ============================================

        for attempt in range(MAX_RETRIES):

            print(f"🎵 Attempt {attempt+1}/{MAX_RETRIES}")

            with torch.no_grad():
                wav = model.generate([current_prompt])[0]

            raw_path = os.path.abspath(
                os.path.join(OUTPUT_DIR, f"{job_id}_raw.wav")
            )

            sf.write(
                raw_path,
                wav.cpu().numpy().T,
                samplerate=32000,
                subtype="PCM_16"
            )

            ok, reason = check_audio_quality(raw_path, current_prompt, mode)

            print("🔍 QA:", ok, reason)

            if ok:
                break

            current_prompt = repair_generation(
                model,
                current_prompt,
                reason,
                duration
            )
            print("🧠 New prompt →", current_prompt)

        if not ok:
            msg = "Some finetuning of prompt needed, Lets retry"
            job_store.set_error(job_id, msg)
            return 

        # ============================================
        # POSTPROCESS ONLY ONCE (AFTER PASS)
        # ============================================

        if mode == "classical":
            wav_path = os.path.abspath(classical_polish_audio(raw_path))
        else:
            wav_path = os.path.abspath(enhance_audio(raw_path))
        final_wav_path = os.path.abspath(
            os.path.join(OUTPUT_DIR, f"{job_id}.wav")
        )
        subprocess.run(["cp", wav_path, final_wav_path], check=True)
        wav_path = final_wav_path

        # =================================================
        # MP4 CREATION (FIXED FOR UNIVERSAL COMPATIBILITY)
        # =================================================
        # =================================================
        # MP4 CREATION (stable + compatible)
        # =================================================

        mp4_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

        COMMON_FLAGS = [
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "medium",
            "-profile:v", "baseline",
            "-level", "3.0",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-shortest",
        ]

        if image_path and os.path.exists(image_path):

            print("🖼 Normalizing uploaded image for mp4 compatibility:", image_path)

            safe_img = os.path.join(OUTPUT_DIR, f"{job_id}_frame.jpg")

            # ⭐ convert ANY image → safe 1080x1080 yuv420p jpg
            subprocess.run(
                [
                    FFMPEG, "-y",
                    "-i", image_path,
                    "-vf",
                    "scale=1080:1080:force_original_aspect_ratio=decrease,"
                    "pad=1080:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-frames:v", "1",
                    safe_img,
                ],
                check=True,
            )

            subprocess.run(
                [
                    FFMPEG, "-y",
                    "-loop", "1",
                    "-framerate", "30",
                    "-i", safe_img,   # ⭐ use normalized image
                    "-i", wav_path,
                    *COMMON_FLAGS,
                    mp4_path,
                ],
                check=True,
            )


#################################
############################################
        else:

            print("🎨 No image → generating indianode branded frame")

            subprocess.run(
                [
                    FFMPEG, "-y",
                    "-f", "lavfi",
                    "-i",
                    f"color=c=black:s=1080x1080:r=30:d={duration},"
                    "drawtext=text='INDIANODE':"
                    "fontcolor=white:"
                    "fontsize=80:"
                    "x=(w-text_w)/2:"
                    "y=(h-text_h)/2",
                    "-i", wav_path,
                    *COMMON_FLAGS,
                    mp4_path,
                ],
                check=True,
            )


        # =================================================
        job_store.set_done(job_id, mp4_path)
        return mp4_path

    except Exception as e:
        print("❌ Internal exception:", e)
        job_store.set_error(
            job_id,
            "This prompt needs a small tweak for best results. Please try again."
        )
        raise

