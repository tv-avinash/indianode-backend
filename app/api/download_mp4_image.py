# app/api/download-mp4_image.py

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

OUTPUT_DIR = "outputs"

router = APIRouter(
    prefix="/api/music",
    tags=["image-music"]
)


@router.get("/download-mp4-image/{job_id}")
def download_mp4_image(job_id: str):
    """
    Download MP4 with user image overlaid (Flow-2).
    """

    mp4_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")

    if not os.path.exists(mp4_path):
        # IMPORTANT: this is the error you are seeing now
        raise HTTPException(status_code=404, detail="MP4 not ready")

    return FileResponse(
        mp4_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{job_id}.mp4"',
            "Cache-Control": "no-store",
            "Accept-Ranges": "bytes",
        },
    )

