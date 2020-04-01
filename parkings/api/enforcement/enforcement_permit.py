from ..common_permit import (
    ActivePermitByExternalIdViewSet, PermitSeriesViewSet, PermitViewSet)
from .permissions import IsEnforcer


class EnforcementPermitSeriesViewSet(PermitSeriesViewSet):
    permission_classes = [IsEnforcer]


class EnforcementPermitViewSet(PermitViewSet):
    permission_classes = [IsEnforcer]


class EnforcementActivePermitByExternalIdViewSet(ActivePermitByExternalIdViewSet):
    permission_classes = [IsEnforcer]
