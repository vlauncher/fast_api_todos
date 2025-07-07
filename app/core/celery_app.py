from celery import Celery
from app.core.config import settings

celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(task_serializer='json', result_serializer='json', accept_content=['json'])

import app.core.tasks
