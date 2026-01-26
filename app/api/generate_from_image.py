# app/api/generate_from_image.py

import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form

from app.tasks.musicgen_task import generate_music_task

OUTPUT_DIR = "outputs"

router = APIRouter(
    prefix="/api/music",
    tags=["image-music"]
)


# -------------------------------------------------
# Generate music from image (Flow-2 enqueue)
# -------------------------------------------------
@router.post("/generate-from-image")
async def generate_from_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    duration: int = Form(30),
):
    job_id = str(uuid.uuid4())

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save uploaded image (used later for MP4 overlay)
    image_path = os.path.join(OUTPUT_DIR, f"{job_id}.jpg")
    with open(image_path, "wb") as f:
        f.write(await image.read())

    payload = {
        "prompt": prompt,
        "duration": duration,
        "image_path": image_path,  # 👈 used by task to render MP4
    }

    # Enqueue SAME Celery task, but Flow-2 payload
    generate_music_task.delay(job_id, payload)

    return {
        "job_id": job_id,
        "status": "queued",
        "source": "image",
    }


# -------------------------------------------------
# Flow-2 STATUS (DO NOT TOUCH Flow-1)
# -------------------------------------------------
@router.get("/status-image/{job_id}")
def image_job_status(job_id: str):
    wav_path = os.path.join(OUTPUT_DIR, f"{job_id}.wav")
    mp4_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

    if os.path.exists(mp4_path):
        return {"status": "done"}

    if os.path.exists(wav_path):
        return {"status": "rendering_video"}

    return {"status": "queued"}

