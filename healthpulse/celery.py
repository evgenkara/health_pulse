# healthpulse/celery.py
import os
from celery import Celery

# Установи модуль настроек Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthpulse.settings')

app = Celery('healthpulse')

# Загрузи настройки из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находи и регистрируй задачи в приложениях Django
app.autodiscover_tasks()
