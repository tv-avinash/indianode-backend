from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.queue_test_store import (
    enqueue,
    get_job,
    queue_position,
)

router = APIRouter(prefix="/api/queue-test")


# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------

# Empirical factor:
# MusicGen ~ 1.2x – 1.5x realtime depending on GPU & model
# We stay conservative
SECONDS_PER_AUDIO_SECOND = 1.5


# -------------------------------------------------------------------
# MODELS
# -------------------------------------------------------------------

class TestRequest(BaseModel):
    prompt: str
    duration: int = 10   # seconds


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def estimate_eta_seconds(position: int, duration: int) -> int:
    """
    Estimate ETA based on:
    - number of jobs ahead
    - requested duration
    """
    if position <= 0:
        return 0

    per_job = int(duration * SECONDS_PER_AUDIO_SECOND)
    return position * per_job


# -------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------

@router.post("/generate")
def generate(req: TestRequest):
    payload = {
        "prompt": req.prompt,
        "duration": req.duration,
    }

    job_id = enqueue(payload)

    # Position is calculated immediately after enqueue
    pos = queue_position(job_id)

    return {
        "job_id": job_id,
        "status": "queued",
        "queue_position": pos,
        "eta_seconds": estimate_eta_seconds(pos, req.duration),
    }


@router.get("/status/{job_id}")
def status(job_id: str):
    job = get_job(job_id)

    if not job:
        return {
            "status": "not_found",
        }

    if job["status"] == "queued":
        pos = queue_position(job_id)

        return {
            "status": "queued",
            "queue_position": pos,
            "eta_seconds": estimate_eta_seconds(
                pos,
                job["payload"]["duration"],
            ),
        }

    # running / done / error
    return job

