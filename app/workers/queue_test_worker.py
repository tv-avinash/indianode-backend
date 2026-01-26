import time
import json
import redis
import os
import sys

# ✅ Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

from app.tasks.musicgen_task import generate_music_task

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

PENDING_QUEUE = "test:music:queue"
PROCESSING_QUEUE = "test:music:processing"
JOB_KEY = "test:music:jobs"
GPU_LOCK_KEY = "gpu:busy"

print("🟢 Queue Test Worker started (SAFE MODE)")

while True:
    # ✅ ATOMIC dequeue (no job loss)
    job_id = r.brpoplpush(
        PENDING_QUEUE,
        PROCESSING_QUEUE,
        timeout=5
    )

    if not job_id:
        continue

    job_raw = r.hget(JOB_KEY, job_id)

    if not job_raw:
        print("⚠️ Missing metadata, re-queueing:", job_id)
        r.lrem(PROCESSING_QUEUE, 0, job_id)
        r.rpush(PENDING_QUEUE, job_id)
        time.sleep(1)
        continue

    job = json.loads(job_raw)

    # 🔒 GPU lock (single GPU safety)
    while r.get(GPU_LOCK_KEY):
        time.sleep(2)

    r.set(GPU_LOCK_KEY, "1")

    try:
        print("▶ Processing job", job_id)

        job["status"] = "running"
        r.hset(JOB_KEY, job_id, json.dumps(job))

        payload = job["payload"]

        generate_music_task(job_id, payload)

        job["status"] = "done"
        job["result"] = f"outputs/{job_id}.wav"
        r.hset(JOB_KEY, job_id, json.dumps(job))

        print("✔ Finished job", job_id)

        # ✅ Remove from processing queue
        r.lrem(PROCESSING_QUEUE, 0, job_id)

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        r.hset(JOB_KEY, job_id, json.dumps(job))

        print("❌ Error:", e)

        # 🔁 Requeue on failure
        r.lrem(PROCESSING_QUEUE, 0, job_id)
        r.rpush(PENDING_QUEUE, job_id)

    finally:
        r.delete(GPU_LOCK_KEY)

