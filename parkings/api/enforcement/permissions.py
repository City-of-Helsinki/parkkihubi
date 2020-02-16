from rest_framework.permissions import BasePermission

from parkings.models import Enforcer


class IsEnforcer(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        try:
            user.enforcer
            return True
        except Enforcer.DoesNotExist:
            pass

        return False
