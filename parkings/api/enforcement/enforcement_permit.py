from ..common_permit import (
    ActivePermitByExternalIdViewSet, PermitSeriesViewSet, PermitViewSet)
from .permissions import IsEnforcer


class EnforcementPermitSeriesViewSet(PermitSeriesViewSet):
    permission_classes = [IsEnforcer]


class _ForcedDomain:
    def validate(self, attrs):
        if self.instance is None:
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
