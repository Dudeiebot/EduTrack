from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
if not settings_module:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu_track.settings.dev")

app = Celery("edu_track")

app.config_from_object("django.conf:settings", namespace="CELERY")
