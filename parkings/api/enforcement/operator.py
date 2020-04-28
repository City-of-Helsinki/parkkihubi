from rest_framework import serializers, viewsets

from ...models import Operator
from .permissions import IsEnforcer


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operator
        fields = [
            'id',
            'created_at',
            'modified_at',
            'name',
        ]


class OperatorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsEnforcer]
    queryset = Operator.objects.order_by('name')
    serializer_class = OperatorSerializer
