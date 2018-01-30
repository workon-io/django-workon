from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.utils import timezone
import workon.utils

__all__ = [
    "authenticate_user",
]

def authenticate_user(request, user, remember=True, backend=None, expiry=60 * 60 * 24 * 365 * 10):
    if user:
        if not hasattr(user, 'backend'):
            if backend:
                user.backend = backend
            elif hasattr(settings, 'AUTHENTICATION_BACKENDS') and len(settings.AUTHENTICATION_BACKENDS):
                user.backend = settings.AUTHENTICATION_BACKENDS[0]
            else:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
        if request.user.is_authenticated:
            auth.logout(request)
        auth.login(request, user)
        request.session.set_expiry(expiry if remember else 0)
        return True
    else:
        return False
