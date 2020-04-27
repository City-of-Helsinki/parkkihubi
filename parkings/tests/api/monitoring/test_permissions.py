import pytest
from django.contrib.auth.models import AnonymousUser, User

from parkings.api.monitoring.permissions import MonitoringApiPermission


@pytest.mark.django_db
def test_monitoring_api_permission_anonymous(rf):
    request = rf.get('/')
    request.user = None
    perm = MonitoringApiPermission()
    assert perm.has_permission(request, None) is False
    request.user = AnonymousUser()
    assert perm.has_permission(request, None) is False


@pytest.mark.django_db
def test_monitoring_api_permission_not_in_group(rf, user):
    request = rf.get('/')
    request.user = user
    perm = MonitoringApiPermission()
    assert perm.has_permission(request, None) is False


@pytest.mark.django_db
@pytest.mark.parametrize('group,allowed', [
    ('monitoring', True), ('othergrp', False)])
def test_monitoring_api_permission_by_group(group, allowed, rf, monitor_factory):
    user = User.objects.create_user('dummy-user')
    user.groups.create(name=group)
    monitor_factory(user=user)
    try:
        request = rf.get('/')
        request.user = user
        perm = MonitoringApiPermission()
        assert perm.has_permission(request, None) is allowed
    finally:
        user.monitor.delete()
        user.groups.all().delete()
        user.delete()
