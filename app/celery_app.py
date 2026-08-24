from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "code_reviewer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.celery_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_acks_late=True,          # re-deliver task if worker dies mid-processing
    worker_prefetch_multiplier=1,  # fair dispatch across workers
    task_time_limit=120,
)
