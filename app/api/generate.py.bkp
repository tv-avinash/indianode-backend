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

router = APIRouter(prefix="/api/music")

OUTPUT_DIR = "outputs"


# -----------------------------
# Request schema (frontend-agnostic)
# -----------------------------
class GenerateRequest(BaseModel):
    description: Optional[str] = None
    prompt: Optional[str] = None
    preset: Optional[str] = None
    instruments: Optional[List[str]] = []
    duration: int = 10


# -----------------------------
# Generate music (enqueue only)
# -----------------------------
@router.post("/generate")
def generate_music(req: GenerateRequest):
    job_id = str(uuid.uuid4())

    # -----------------------------
    # LOG: raw frontend input
    # -----------------------------
    print("\n🎯 /api/music/generate RECEIVED")
    print("  preset     :", req.preset)
    print("  instruments:", req.instruments)
    print("  description:", req.description)
    print("  prompt     :", req.prompt)
    print("  duration   :", req.duration)

    # Build final text prompt
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

    print("\n🧱 BUILT PROMPT (pre-intent):")
    print(final_prompt)

    if not final_prompt:
        raise HTTPException(
            status_code=400,
            detail="No musical description provided"
        )

    # -----------------------------
    # LLM intent analysis
    # -----------------------------
    intent = analyze_intent(final_prompt)

    print("\n🧠 INTENT ANALYZER OUTPUT:")
    for k, v in intent.items():
        print(f"  {k}: {v}")

    payload = {
        "prompt": intent.get("music_prompt", final_prompt),
        "duration": intent.get("duration", req.duration),

        # inferred metadata (LLM)
        "instrument": intent.get("instrument"),
        "style": intent.get("style"),
        "tempo": intent.get("tempo"),
        "mood": intent.get("mood"),
        "language": intent.get("language"),
    }

    print("\n🎼 FINAL PAYLOAD → MUSICGEN TASK:")
    for k, v in payload.items():
        print(f"  {k}: {v}")

    # Enqueue Celery task (unchanged)
    generate_music_task.delay(job_id, payload)

    return {
        "job_id": job_id,
        "status": "queued",
    }


# -----------------------------
# Job status (Celery + filesystem)
# -----------------------------
@router.get("/status/{job_id}")
def job_status(job_id: str):
    wav_path = os.path.join(OUTPUT_DIR, f"{job_id}.wav")
    result = AsyncResult(job_id, app=celery_app)

    if os.path.exists(wav_path):
        return {
            "status": "done",
            "result": wav_path,
        }

    if result.state == "PENDING":
        return {"status": "queued"}

    if result.state == "STARTED":
        return {"status": "running"}

    if result.state == "FAILURE":
        return {
            "status": "error",
            "error": str(result.info),
        }

    return {"status": result.state}


# -----------------------------
# Download generated WAV
# -----------------------------
@router.get("/download/{job_id}")
def download_audio(job_id: str):
    wav_path = os.path.join(OUTPUT_DIR, f"{job_id}.wav")

    if not os.path.exists(wav_path):
        raise HTTPException(status_code=404, detail="Audio not ready")

    return FileResponse(
        wav_path,
        media_type="audio/wav",
        filename=f"{job_id}.wav",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-store",
        },
    )


# -----------------------------
# Download generated MP4 (WhatsApp-safe)
# -----------------------------
@router.get("/download-mp4/{job_id}")
def download_video(job_id: str):
    mp4_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

    if not os.path.exists(mp4_path):
        raise HTTPException(status_code=404, detail="Video not ready")

    return FileResponse(
        mp4_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{job_id}.mp4"',
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-store",
        },
    )

