from fastapi import APIRouter, UploadFile, File
import uuid
import shutil
import os

from app.tasks.bgm_task import generate_bgm
from celery.result import AsyncResult
from app.celery_app import celery

router = APIRouter(prefix="/api/bgm", tags=["bgm"])


UPLOAD_DIR = "/tmp/bgm_jobs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# Generate
# =========================
@router.post("/generate")
async def generate(file: UploadFile = File(...)):

    job_id = str(uuid.uuid4())
    input_path = f"{UPLOAD_DIR}/{job_id}_input.mp4"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    task = generate_bgm.delay(input_path)

    return {"job_id": task.id}


# =========================
# Status
# =========================
@router.get("/status/{job_id}")
def status(job_id: str):

    task = AsyncResult(job_id, app=celery)

    return {"status": task.status}


# =========================
# Download
# =========================
@router.get("/download/{job_id}")
def download(job_id: str):

    task = AsyncResult(job_id, app=celery)

    if not task.successful():
        return {"error": "Not ready"}

    path = task.result

    from fastapi.responses import FileResponse
    return FileResponse(path, filename="bgm_video.mp4")

