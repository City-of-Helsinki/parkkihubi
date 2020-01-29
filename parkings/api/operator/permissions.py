from rest_framework import permissions

from parkings.models import Operator


class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow only operators to proceed further.
        """
        user = request.user

        if not user.is_authenticated:
            return False

        try:
            user.operator
            return True
        except Operator.DoesNotExist:
            pass

        return False
