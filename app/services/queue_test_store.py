import redis
import time
import json
import uuid

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

QUEUE_KEY = "test:music:queue"
JOB_KEY = "test:music:jobs"

AVG_JOB_TIME = 30  # seconds (estimate)

def enqueue(payload):
    job_id = str(uuid.uuid4())

    job = {
        "job_id": job_id,
        "status": "queued",
        "created_at": time.time(),
        "payload": payload,
    }

    r.hset(JOB_KEY, job_id, json.dumps(job))
    r.rpush(QUEUE_KEY, job_id)

    return job_id

def get_job(job_id):
    raw = r.hget(JOB_KEY, job_id)
    return json.loads(raw) if raw else None

def queue_position(job_id):
    q = r.lrange(QUEUE_KEY, 0, -1)
    return q.index(job_id) + 1 if job_id in q else None

def queue_length():
    return r.llen(QUEUE_KEY)

