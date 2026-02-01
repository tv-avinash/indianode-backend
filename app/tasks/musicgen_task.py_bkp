# app/tasks/musicgen_task.py

import os
import torch
import soundfile as sf
import subprocess
from PIL import Image

from audiocraft.models import MusicGen

from app.celery_app import celery_app
from app.services.job_store import job_store
from app.services.audio_postprocess_service import enhance_audio
from app.services.mastering.mastering_service import master_audio

# ⭐ NEW → classical clean chain
from app.services.classical_postprocess_service import classical_polish_audio

# 🔥 AI judge only — no DSP
from app.services.audio_quality_service import check_audio_quality
from app.services.prompt_repair_service import repair_prompt

# ✅ NEW — technical crack/hiss repair ONLY (no musical changes)
from app.services.audio_technical_qa import (
    check_audio_technical_quality,
    repair_audio_technical
)


# -------------------------------------------------
# Paths
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

MAX_RETRIES = 4  # ✅ unchanged


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
@celery_app.task(name="musicgen.generate", queue="gpu")
def generate_music_task(job_id: str, payload: dict):
    try:
        print(f"\n🎼 Generating music | job={job_id}")

        job_store.set_running(job_id)

        prompt = payload.get("prompt", "")
        image_path = payload.get("image_path")
        mode = payload.get("mode", "cinematic")
        duration = int(payload.get("duration", 10))

        print("\n" + "=" * 60)
        print("🎯 INITIAL PROMPT")
        print(prompt)
        print("=" * 60 + "\n")

        model = load_musicgen(mode)
        model.set_generation_params(duration=duration)
        duration_str = str(duration)

        # =================================================
        # 🔥 GENERATE + AI QUALITY LOOP (UNCHANGED)
        # =================================================
        wav_path = None

        for attempt in range(1, MAX_RETRIES + 1):

            print(f"\n🎵 Generation attempt {attempt}/{MAX_RETRIES}")

            with torch.no_grad():
                wav = model.generate([prompt])[0]

            wav_path = os.path.abspath(
                os.path.join(OUTPUT_DIR, f"{job_id}_attempt{attempt}.wav")
            )

            sf.write(
                wav_path,
                wav.cpu().numpy().T,
                samplerate=32000,
                subtype="PCM_16"
            )

            # =================================================
            # 🔧 NEW — technical crack/hiss/clipping repair ONLY
            # (safe DSP, does NOT change music)
            # =================================================
            tech_ok, issues = check_audio_technical_quality(wav_path)
            if not tech_ok:
                print("🔧 Technical issues detected:", issues)
                wav_path = repair_audio_technical(wav_path)

            # =================================================
            # EXISTING AI QUALITY CHECK (UNCHANGED)
            # =================================================
            passed, reason = check_audio_quality(wav_path, prompt)

            if passed:
                print("✅ Audio quality PASSED")
                break

            print(f"❌ Audio rejected: {reason}")
            prompt = repair_prompt(prompt, reason)

            print("🔧 Repaired prompt:")
            print(prompt)

        if wav_path is None:
            raise RuntimeError("Audio generation failed")

        print("✅ RAW WAV:", wav_path)

        # =================================================
        # ⭐ MODE-SPECIFIC PIPELINE (UNCHANGED)
        # =================================================

        if mode == "classical":
            print("🎻 Classical mode → clean acoustic polish only")

            wav_path = os.path.abspath(
                classical_polish_audio(wav_path)
            )

            print("🎻 CLASSICAL POLISHED WAV:", wav_path)

        else:
            try:
                print("✨ Running enhancement...")
                wav_path = os.path.abspath(enhance_audio(wav_path))
                print("✨ ENHANCED WAV:", wav_path)
            except Exception as e:
                print("⚠️ Enhancement failed:", e)

            try:
                print("🎚 Running mastering (Ozone)...")

                mastered_path = os.path.abspath(
                    os.path.join(OUTPUT_DIR, f"{job_id}_mastered.wav")
                )

                wav_path = master_audio(wav_path, mastered_path)

                print("🎚 MASTERED WAV:", wav_path)

            except Exception as e:
                print("⚠️ Mastering failed, using enhanced audio:", e)

        # =================================================
        # ✅ canonical {job_id}.wav for frontend (UNCHANGED)
        # =================================================
        final_wav_path = os.path.abspath(
            os.path.join(OUTPUT_DIR, f"{job_id}.wav")
        )

        subprocess.run(["cp", wav_path, final_wav_path], check=True)

        wav_path = final_wav_path
        print("📦 FINAL WAV (frontend compatible):", wav_path)

        # -------------------------------------------------
        # MP4 output (UNCHANGED)
        # -------------------------------------------------
        mp4_path = os.path.abspath(
            os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
        )

        if image_path:
            image_path = os.path.abspath(image_path)

            if not os.path.exists(image_path):
                raise RuntimeError(f"Image not found: {image_path}")

            fixed_img = image_path + "_fixed.jpg"

            Image.open(image_path).convert("RGB").save(
                fixed_img,
                "JPEG",
                quality=95
            )

            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-framerate", "30",
                "-t", duration_str,
                "-i", fixed_img,
                "-i", wav_path,
                "-vf",
                "scale=1080:1080:force_original_aspect_ratio=decrease,"
                "pad=1080:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-c:a", "aac",
                "-shortest",
                mp4_path
            ]
        else:
            cmd = [
                FFMPEG, "-y",
                "-f", "lavfi",
                "-i", f"color=c=black:s=1080x1080:r=30:d={duration_str}",
                "-i", wav_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-c:a", "aac",
                "-shortest",
                mp4_path
            ]

        subprocess.run(cmd, check=True)

        job_store.set_done(job_id, mp4_path)
        return mp4_path

    except Exception as e:
        print("❌ TASK FAILED:", e)
        job_store.set_error(job_id, str(e))
        raise

