from rest_framework import mixins

from ..common_permit import PermitSeriesViewSet
from .permissions import IsOperator


class OperatorPermitSeriesViewSet(mixins.DestroyModelMixin, PermitSeriesViewSet):
    permission_classes = [IsOperator]
