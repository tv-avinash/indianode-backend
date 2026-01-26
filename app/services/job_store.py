import time
import json
import redis

# Use a separate Redis DB for job tracking
r = redis.Redis(
    host="localhost",
    port=6379,
    db=2,
    decode_responses=True,
)

class JobStore:
    def create(self, job_id: str):
        r.set(
            job_id,
            json.dumps({
                "status": "queued",
                "created_at": time.time(),
                "updated_at": time.time(),
                "result": None,
                "error": None,
            })
        )

    def set_running(self, job_id: str):
        self._update(job_id, status="running")

    def set_done(self, job_id: str, result: str):
        self._update(job_id, status="done", result=result)

    def set_error(self, job_id: str, error: str):
        self._update(job_id, status="error", error=error)

    def get(self, job_id: str):
        data = r.get(job_id)
        return json.loads(data) if data else None

    def _update(self, job_id: str, **fields):
        job = self.get(job_id)
        if not job:
            return
        job.update(fields)
        job["updated_at"] = time.time()
        r.set(job_id, json.dumps(job))

job_store = JobStore()

