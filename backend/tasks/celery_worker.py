from backend.extensions import celery
from backend.config import Config

# Configure the existing Celery instance from extensions
celery.conf.update(
    broker_url=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
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