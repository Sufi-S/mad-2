from celery import Celery
from backend.config import Config

# Initialize Celery
celery = Celery(
    'hospital_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    result_expires=3600,
)

# Auto-discover tasks
celery.autodiscover_tasks(['backend.tasks'])

if __name__ == '__main__':
    celery.start()