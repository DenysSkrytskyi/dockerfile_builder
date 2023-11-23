import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dockerfile_publisher.settings")

# Create a Celery instance and configure it using the settings from Django.
app = Celery("dockerfile_publisher")

# set timezone , use fr
app.conf.enable_utc = False 
app.conf.timezone = 'Europe/Berlin'

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()