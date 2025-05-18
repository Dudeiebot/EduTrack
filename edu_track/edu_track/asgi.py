"""
ASGI config for edu_track project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
if not settings_module:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edu_track.settings.dev")

application = get_asgi_application()
