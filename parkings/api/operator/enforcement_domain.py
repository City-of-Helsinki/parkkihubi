from rest_framework import serializers
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from parkings.models import EnforcementDomain

from .operator_permission import OperatorApiHasPermission


class EnforcementDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnforcementDomain
        fields = ("code", "name")


class EnforcementDomainViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [OperatorApiHasPermission]
    serializer_class = EnforcementDomainSerializer
    queryset = EnforcementDomain.objects.all()
