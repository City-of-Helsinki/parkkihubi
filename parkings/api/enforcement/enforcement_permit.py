from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from ..common_permit import (
    ActivePermitByExternalIdViewSet, PermitSeriesViewSet, PermitViewSet)
from .permissions import IsEnforcer


class EnforcementPermitSeriesViewSet(PermitSeriesViewSet):
    permission_classes = [IsEnforcer]


class _ForcedDomain:
    def to_internal_value(self, data):
        # Call super first, since it makes sure that data is a mapping
        result = super().to_internal_value(data)
        if 'domain' in data:
            raise ValidationError({'domain': [_("Not allowed")]})
        return result

    def validate(self, attrs):
        if self.instance is None:
            assert 'domain' not in attrs
            user = self.context['request'].user
            attrs['domain'] = user.enforcer.enforced_domain
        return super().validate(attrs)


class EnforcementPermitSerializer(
        _ForcedDomain, PermitViewSet.serializer_class):
    pass


class EnforcementPermitViewSet(PermitViewSet):
    permission_classes = [IsEnforcer]
    serializer_class = EnforcementPermitSerializer


class EnforcementActivePermitSerializer(
        _ForcedDomain, ActivePermitByExternalIdViewSet.serializer_class):
    pass


class EnforcementActivePermitByExternalIdViewSet(ActivePermitByExternalIdViewSet):
    permission_classes = [IsEnforcer]
    serializer_class = EnforcementActivePermitSerializer
