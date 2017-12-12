from rest_framework import permissions, serializers, viewsets

from ...authentication import ApiKeyAuthentication
from ...models import Operator


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
    queryset = Operator.objects.order_by('name')
    serializer_class = OperatorSerializer
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAdminUser]
