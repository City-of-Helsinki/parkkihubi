from rest_framework import permissions

from parkings.models import Monitor


class IsMonitor(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow only monitors to proceed further.
        """
        user = request.user

        if not user.is_authenticated:
            return False

        try:
            user.monitor
            return True
        except Monitor.DoesNotExist:
            pass

        return False
