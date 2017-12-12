import contextlib
from functools import lru_cache

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# No-op context manager
#
# Usable like the one coming in Python 3.7, see
# https://github.com/python/cpython/commit/0784a2e5b174d2dbf7b144d480559e650c5cf64c
nullcontext = contextlib.ExitStack


class AdminTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_overrider = nullcontext()
        if request.path.startswith(get_admin_url_path_prefix()):
            admin_tz = getattr(settings, 'ADMIN_TIME_ZONE', None)
            if admin_tz:
                tz_overrider = timezone.override(admin_tz)
        with tz_overrider:
            return self.get_response(request)


@lru_cache()
def get_admin_url_path_prefix():
    return reverse('admin:index')
