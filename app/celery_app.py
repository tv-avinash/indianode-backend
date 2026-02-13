from celery import Celery

celery = Celery(
    "indianode",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# ✅ EXPLICIT imports (guaranteed registration)
import app.tasks.musicgen_task
import app.tasks.accompaniment_task
import app.bgm.bgm_tasks
# compatibility alias
celery_app = celery

