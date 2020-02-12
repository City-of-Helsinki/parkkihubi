from rest_framework import serializers

from parkings.models import EnforcementDomain

from ..common_permit import (
    ActivePermitByExternalIdSerializer, ActivePermitByExternalIdViewSet,
    PermitSerializer, PermitViewSet)
from .operator_permission import OperatorApiHasPermission


class OperatorPermitSerializer(PermitSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())

    class Meta(PermitSerializer.Meta):
        fields = PermitSerializer.Meta.fields + ['domain']


class OperatorPermitViewSet(PermitViewSet):
    serializer_class = OperatorPermitSerializer
    permission_classes = [OperatorApiHasPermission]


class OperatorActivePermitByExtIdSerializer(ActivePermitByExternalIdSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())

    class Meta(ActivePermitByExternalIdSerializer.Meta):
        fields = ActivePermitByExternalIdSerializer.Meta.fields + ['domain']


class OperatorActivePermitByExternalIdViewSet(ActivePermitByExternalIdViewSet):
    permission_classes = [OperatorApiHasPermission]
    serializer_class = OperatorActivePermitByExtIdSerializer
