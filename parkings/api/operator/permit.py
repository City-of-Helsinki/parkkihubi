from rest_framework import serializers

from parkings.models import EnforcementDomain

from ..common_permit import PermitSerializer, PermitViewSet
from .operator_permission import OperatorApiHasPermission


class OperatorPermitSerializer(PermitSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())

    class Meta(PermitSerializer.Meta):
        fields = PermitSerializer.Meta.fields + ['domain']


class OperatorPermitViewSet(PermitViewSet):
    serializer_class = OperatorPermitSerializer
    permission_classes = [OperatorApiHasPermission]
