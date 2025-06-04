"""
ASGI config for clinic_base project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_base.settings')

django_asgi_app = get_asgi_application()



from clinic_base import routing


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Add other protocols here if needed, e.g., "websocket": websocket_application,

        "websocket":  AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    routing.websocket_urlpatterns
                )
            )
        ),
    }
)
