from rest_framework import permissions, serializers, viewsets

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
    permission_classes = [permissions.IsAdminUser]
    queryset = Operator.objects.order_by('name')
    serializer_class = OperatorSerializer
