import subprocess
import uuid
import os
from celery import shared_task

SMART_DIR = "/home/supersu/smart_bgm_service"
SCRIPT = f"{SMART_DIR}/bgm_video_pipeline.py"
PYTHON = f"{SMART_DIR}/smart_venv/bin/python"


def run(cmd):
    subprocess.run(cmd, check=True)


@shared_task(name="bgm.generate")
def generate_bgm(input_path: str):

    uid = str(uuid.uuid4())

    out_path = f"/tmp/{uid}_bgm.mp4"

    run([
        PYTHON,
        SCRIPT,
        input_path,
        out_path
    ])

    return out_path

