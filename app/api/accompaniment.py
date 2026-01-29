from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from app.celery_app import celery_app

import uuid
import shutil
import os

router = APIRouter(prefix="/api/accompaniment", tags=["accompaniment"])

TMP_DIR = "/tmp"


# =====================================================
# Generate  (enqueue celery job)
# =====================================================
@router.post("/generate")
async def generate_accompaniment(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    path = f"{TMP_DIR}/{job_id}.wav"

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    task = celery_app.send_task(
        "accompaniment.generate",
        args=[path],
        queue="gpu",
    )

    return {"job_id": task.id}


# =====================================================
# Status
# =====================================================
@router.get("/status/{job_id}")
def status(job_id: str):
    job = AsyncResult(job_id, app=celery_app)
    return {"status": job.state}


# =====================================================
# Download (REAL FILE STREAM)
# =====================================================
@router.get("/download/{job_id}")
def download(job_id: str):
    job = AsyncResult(job_id, app=celery_app)

    # still processing
    if job.state != "SUCCESS":
        return {"error": "file_not_ready"}

    # celery task returns: "final_video.mp4"
    output_path = job.result

    if not output_path or not os.path.exists(output_path):
        return {"error": "file_not_found"}

    return FileResponse(
        path=output_path,
        filename="indianode_accompaniment.mp4",
        media_type="video/mp4"
    )

