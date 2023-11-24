from django.db.models import Q
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from parkings.models import EnforcementDomain, PermitArea

from ..common_permit import (
    ActivePermitByExternalIdSerializer, ActivePermitByExternalIdViewSet,
    PermitSerializer, PermitSeriesViewSet, PermitViewSet)
from .permissions import IsOperator


class OperatorPermitSeriesViewSet(mixins.DestroyModelMixin, PermitSeriesViewSet):
    permission_classes = [IsOperator]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        serializer = PermitSeriesActivateBodySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        deactivate_id_filter = (
            Q() if params['deactivate_others'] else
            Q(pk__in=params.get('deactivate_series', [])))
        return self.execute_activation(deactivate_id_filter)


class PermitSeriesActivateBodySerializer(serializers.Serializer):
    deactivate_others = serializers.BooleanField(required=False, default=False)
    deactivate_series = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )


class OperatorPermitSerializer(PermitSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())

    class Meta(PermitSerializer.Meta):
        fields = PermitSerializer.Meta.fields + ['domain']


class OperatorPermitViewSet(PermitViewSet):
    serializer_class = OperatorPermitSerializer
    permission_classes = [IsOperator]


class OperatorActivePermitByExtIdSerializer(ActivePermitByExternalIdSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())

    class Meta(ActivePermitByExternalIdSerializer.Meta):
        fields = ActivePermitByExternalIdSerializer.Meta.fields + ['domain']


class OperatorActivePermitByExternalIdViewSet(ActivePermitByExternalIdViewSet):
    permission_classes = [IsOperator]
    serializer_class = OperatorActivePermitByExtIdSerializer


class OperatorPermitAreaSerializer(serializers.ModelSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())
    code = serializers.CharField(source='identifier')

    class Meta:
        model = PermitArea
        fields = ['code', 'domain', 'name']


class OperatorPermittedPermitAreaViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsOperator]
    serializer_class = OperatorPermitAreaSerializer

    def get_queryset(self):
        return PermitArea.objects.for_user(self.request.user)
