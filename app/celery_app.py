from celery import Celery

celery_app = Celery(
    "indianode",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

import app.tasks.musicgen_task  # noqa

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

import app.tasks.accompaniment_task
