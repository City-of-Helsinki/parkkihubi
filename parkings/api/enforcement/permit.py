from ..common_permit import (
    ActivePermitByExternalIdViewSet, PermitSeriesViewSet, PermitViewSet)


class EnforcementPermitSeriesViewSet(PermitSeriesViewSet):
    pass


class EnforcementPermitViewSet(PermitViewSet):
    pass


class EnforcementActivePermitByExternalIdViewSet(
    ActivePermitByExternalIdViewSet
):
    pass
