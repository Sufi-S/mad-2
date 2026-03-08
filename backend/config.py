import os
from datetime import timedelta

class Config:
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = 'your-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Redis
    REDIS_URL = 'redis://localhost:6379/0'
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
    
    # Celery Beat Schedule
    CELERY_BEAT_SCHEDULE = {
        'send-daily-reminders': {
            'task': 'tasks.send_appointment_reminders',
            'schedule': timedelta(hours=24),  # Run daily
            'args': ()
        },
        'generate-monthly-reports': {
            'task': 'tasks.generate_monthly_reports',
            'schedule': timedelta(days=30),  # Run monthly
            'args': ()
        },
        'cleanup-old-exports': {
            'task': 'tasks.cleanup_old_exports',
            'schedule': timedelta(hours=24),  # Run daily
            'args': ()
        }
    }
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-hospital@gmail.com'
    MAIL_PASSWORD = 'your-app-password'
    MAIL_DEFAULT_SENDER = 'your-hospital@gmail.com'
    
    # Google Chat Webhook
    GOOGLE_CHAT_WEBHOOK = 'YOUR_GOOGLE_CHAT_WEBHOOK_URL'
    
    # Admin (pre-existing)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    ADMIN_EMAIL = 'admin@hospital.com'