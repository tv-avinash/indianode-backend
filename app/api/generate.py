# app/api/generate.py

import uuid
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from celery.result import AsyncResult

from app.celery_app import celery_app
from app.tasks.musicgen_task import generate_music_task
from app.intelligence.intent_analyzer import analyze_intent
from app.intelligence.prompt_enhancer import enhance_prompt
# ✅ QUALITY GUARDRAILS
from app.music_prompt.quality_guardrails import apply_quality_guardrails
from app.intelligence.prompt_enhancer import enhance_prompt
from app.intelligence.intent_expander import expand_prompt
router = APIRouter(prefix="/api/music", tags=["music"])

OUTPUT_DIR = "outputs"
MIN_WORDS_FOR_DIRECT_PROMPT = 6


# -----------------------------
# Request schema
# -----------------------------
class GenerateRequest(BaseModel):
    description: Optional[str] = None
    prompt: Optional[str] = None
    preset: Optional[str] = None
    instruments: Optional[List[str]] = []
    duration: int = 10

    # ⭐ NEW (ONLY ADDITION)
    # receives frontend checkbox value
    mode: str = "cinematic"


# -----------------------------
# Generate music
# -----------------------------
@router.post("/generate")
def generate_music(req: GenerateRequest):
    job_id = str(uuid.uuid4())

    print("\n🎯 /api/music/generate")
    print("preset:", req.preset)
    print("instruments:", req.instruments)
    print("prompt:", req.prompt)
    print("duration:", req.duration)
    print("mode:", req.mode)  # ⭐ helpful debug

    parts = []

    if req.preset:
        parts.append(f"{req.preset} style music")

    if req.instruments:
        parts.append("featuring " + ", ".join(req.instruments))

    if req.description:
        parts.append(req.description)

    if req.prompt:
        parts.append(req.prompt)

    final_prompt = ". ".join(parts).strip()

    if not final_prompt:
        raise HTTPException(400, "No musical description provided")

    word_count = len(final_prompt.split())

    #if word_count < MIN_WORDS_FOR_DIRECT_PROMPT:
    #intent = analyze_intent(final_prompt)
    #music_prompt = build_music_prompt_from_intent(intent)
    #else:
    #music_prompt = final_prompt
    print("\n================ PROMPT PIPELINE ================")
    print("🟡 USER INPUT:")
    print(final_prompt)
    print(f"🔥 MODE RAW VALUE -> [{req.mode}] (type={type(req.mode)})")
    expanded = expand_prompt(
    final_prompt,
    instruments=req.instruments,
    preset=req.preset,
    mode=req.mode
    )
    music_prompt = expanded
    #expanded = expand_prompt(final_prompt)     # NEW layer
    #music_prompt = enhance_prompt(expanded)   # existing layer
    #music_prompt = expanded
    print("\n================ PROMPT PIPELINE ================")
    print("🟡 EXPANDED:")
    print(expanded)
    print("\n================ PROMPT PIPELINE ================")
    print("🟡 final to musicgen:")
    print(music_prompt)
    #music_prompt = enhance_prompt(final_prompt)
    # ✅ APPLY GUARDRAILS (NO SIDE EFFECTS)
    guarded_prompt = apply_quality_guardrails(
        music_prompt,
        req.instruments or []
    )

    print("\n🎼 FINAL PROMPT SENT TO MUSICGEN:")
    print(guarded_prompt)

    payload = {
        "prompt": guarded_prompt,
        "duration": req.duration,

        # ⭐ NEW (ONLY ADDITION)
        "mode": req.mode
    }

    generate_music_task.delay(job_id, payload)

    return {"job_id": job_id, "status": "queued"}


# -----------------------------
# Job status
# -----------------------------
@router.get("/status/{job_id}")
def job_status(job_id: str):
    wav_path = os.path.join(OUTPUT_DIR, f"{job_id}.wav")
    result = AsyncResult(job_id, app=celery_app)

    if os.path.exists(wav_path):
        return {"status": "done"}

    if result.state in ("PENDING", "STARTED"):
        return {"status": "running"}

    if result.state == "FAILURE":
        return {"status": "error", "error": str(result.info)}

    return {"status": result.state}


# -----------------------------
# Download WAV
# -----------------------------
@router.get("/download/{job_id}")
def download_audio(job_id: str):
    path = os.path.join(OUTPUT_DIR, f"{job_id}.wav")
    if not os.path.exists(path):
        raise HTTPException(404, "Audio not ready")
    return FileResponse(path, media_type="audio/wav", filename=f"{job_id}.wav")


# -----------------------------
# Download MP4
# -----------------------------
@router.get("/download-mp4/{job_id}")
def download_video(job_id: str):
    path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    if not os.path.exists(path):
        raise HTTPException(404, "Video not ready")
    return FileResponse(path, media_type="video/mp4", filename=f"{job_id}.mp4")


# -----------------------------
# Intent → Prompt
# -----------------------------
def build_music_prompt_from_intent(intent: dict) -> str:
    parts = []

    tempo_map = {
        "slow": "80 bpm",
        "medium": "100 bpm",
        "fast": "130 bpm"
    }

    if intent.get("genre"):
        parts.append(intent["genre"])

    if intent.get("instruments"):
        parts.append(", ".join(intent["instruments"]))

    if intent.get("tempo"):
        parts.append(tempo_map.get(intent["tempo"], "100 bpm"))

    # 🔥 always add tightness keywords
    parts.extend([
        "tight rhythm",
        "precise timing",
        "clear articulation",
        "short phrases",
        "dry mix",
        "close mic recording",
        "studio quality",
        "wide stereo"
    ])

    if intent.get("vocals") == "none":
        parts.append("instrumental")

    return ", ".join(parts)

