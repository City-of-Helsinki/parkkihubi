import contextlib
from functools import lru_cache

from django.conf import settings
from django.http import HttpResponseNotAllowed
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


class MethodOverrideMiddleware:
    """
    Override the HTTP method with a query parameter.

    Allows overriding the HTTP method using the `method` query string
    parameter.  Only works with POST requests and allows overriding the
    method to DELETE, PATCH or PUT.
    """

    allowed_override_methods = {"DELETE", "PATCH", "PUT"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and "method" in request.GET:
            method = request.GET["method"]

            if method not in self.allowed_override_methods:
                return HttpResponseNotAllowed(
                    permitted_methods=self.allowed_override_methods,
                    reason="Method Override Not Allowed",
                )

            # Use the specified method instead of POST
            request.method = method

            # Remove the method parameter from the query string
            request.GET = request.GET.copy()
            del request.GET["method"]

        return self.get_response(request)
