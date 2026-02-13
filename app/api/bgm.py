# app/api/bgm.py

import os
import uuid
import shutil

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse

from app.bgm.bgm_tasks import generate_bgm_task

router = APIRouter(prefix="/api/bgm", tags=["bgm"])

UPLOAD_DIR = "bgm_jobs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =====================================================
# POST /api/bgm/process
# =====================================================
@router.post("/process")
async def process_video(
    file: UploadFile = File(...),
    prompt: str = Form("")
):
    job_id = uuid.uuid4().hex[:8]

    in_path = f"{UPLOAD_DIR}/{job_id}_in.mp4"
    out_path = f"{UPLOAD_DIR}/{job_id}_out.mp4"

    with open(in_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    print("TYPE:", type(generate_bgm_task))
    print("HAS DELAY:", hasattr(generate_bgm_task, "delay"))
    print("CALLING DELAY NOW")
    generate_bgm_task.delay(in_path, out_path, prompt)

    return {"job_id": job_id}


# =====================================================
# GET /api/bgm/status/{job}
# =====================================================
@router.get("/status/{job_id}")
def status(job_id: str):
    out_path = f"{UPLOAD_DIR}/{job_id}_out.mp4"

    if os.path.exists(out_path):
        return {"status": "done"}

    return {"status": "processing"}


# =====================================================
# GET /api/bgm/download/{job}
# =====================================================
@router.get("/download/{job_id}")
def download(job_id: str):
    path = f"{UPLOAD_DIR}/{job_id}_out.mp4"
    return FileResponse(path, media_type="video/mp4", filename="bgm_video.mp4")

