from celery.schedules import crontab
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arabalar.settings')

app = Celery('arabalar')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()




app.conf.beat_schedule = {
    'cleanup-duplicates-every-day': {
        'task': 'books.tasks.cleanup_duplicates',
        'schedule': crontab(hour=0, minute=0),  # type: ignore
    },
}