from django.conf import settings
from rest_framework import permissions


class MonitoringApiPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        user_groups = request.user.groups
        group_name = getattr(settings, 'MONITORING_GROUP_NAME', 'monitoring')

        is_in_monitoring_group = (user_groups.filter(name=group_name).exists())

        return is_in_monitoring_group
