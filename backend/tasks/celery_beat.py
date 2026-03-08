from celery import Celery
from celery.schedules import crontab
from backend.config import Config

# Initialize Celery
celery = Celery(
    'hospital_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

# Configure Celery Beat schedule
celery.conf.beat_schedule = {
    # Send reminders every day at 8 AM
    'send-daily-reminders': {
        'task': 'tasks.send_appointment_reminders',
        'schedule': crontab(hour=8, minute=0),
        'args': ()
    },
    
    # Generate monthly reports on 1st day of month at 9 AM
    'generate-monthly-reports': {
        'task': 'tasks.generate_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),
        'args': ()
    },
    
    # Clean up old exports every day at 2 AM
    'cleanup-old-exports': {
        'task': 'tasks.cleanup_old_exports',
        'schedule': crontab(hour=2, minute=0),
        'args': ()
    },
}

celery.conf.timezone = 'UTC'