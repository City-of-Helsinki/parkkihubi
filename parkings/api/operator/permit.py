from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from parkings.models import EnforcementDomain, Permit, PermitSeries

from ..common_permit import (
    ActivePermitByExternalIdSerializer, ActivePermitByExternalIdViewSet,
    PermitSerializer, PermitSeriesViewSet, PermitViewSet)
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


class OperatorPermitSeriesViewSet(mixins.DestroyModelMixin, PermitSeriesViewSet):
    permission_classes = [OperatorApiHasPermission]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        with transaction.atomic():
            obj_to_activate = self.get_object()
            old_actives = self.queryset.filter(active=True)

            # Always activate the specified permit series regardless of what to deactivate
            if not obj_to_activate.active:
                obj_to_activate.active = True
                obj_to_activate.save()

            deactivate_payload = OperatorPermitSeriesPayload(data=request.data)
            deactivate_payload.is_valid(raise_exception=True)
            validated_data = deactivate_payload.validated_data

            if validated_data['deactivate_others']:
                old_actives.exclude(pk=obj_to_activate.pk).update(active=False)
            else:
                ids_to_deactivate = validated_data.get('deactivate_series', [])
                old_actives.filter(id__in=ids_to_deactivate).exclude(
                    pk=obj_to_activate.pk
                ).update(active=False)

            prunable_series = PermitSeries.objects.prunable()
            Permit.objects.filter(series__in=prunable_series).delete()
            prunable_series.delete()

            return Response({'status': 'OK'})


class OperatorPermitSeriesPayload(serializers.Serializer):
    deactivate_others = serializers.BooleanField(required=False)
    deactivate_series = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    def validate(self, data):
        if 'deactivate_series' in data:
            data['deactivate_others'] = False

        if (
            'deactivate_others' in data
            or 'deactivate_series' in data
        ):
            return super().validate(data)

        raise serializers.ValidationError(
            _('Either deactivate_others or deactivate_series is required')
        )
