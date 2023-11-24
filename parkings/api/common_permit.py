from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from ..models import Permit, PermitArea, PermitSeries


class PermitSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermitSeries
        fields = ['id', 'created_at', 'modified_at', 'active']
        read_only_fields = fields


class CreateAndReadOnlyModelViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    pass


class PermitSeriesViewSet(CreateAndReadOnlyModelViewSet):
    queryset = PermitSeries.objects.all()
    serializer_class = PermitSeriesSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        return self.execute_activation(Q())

    def execute_activation(self, deactivate_id_filter):
        with transaction.atomic():
            obj_to_activate = self.get_object()
            to_deactivate = (
                self.get_queryset()
                .filter(active=True)
                .filter(deactivate_id_filter)
                .exclude(pk=obj_to_activate.pk))

            if obj_to_activate.active and to_deactivate.count() == 0:
                return Response({'status': 'No change'})

            if not obj_to_activate.active:
                obj_to_activate.active = True
                obj_to_activate.save(update_fields=['active'])

            to_deactivate.update(active=False)

            PermitSeries.delete_prunable_series()

            return Response({'status': 'OK'})


class PermitListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        permits = [Permit(**item) for item in validated_data]
        return Permit.objects.bulk_create(permits)


class PermitSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = PermitListSerializer
        model = Permit
        fields = [
            'id',
            'series',
            'external_id',
            'subjects',
            'areas',
            'properties',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        series_field = self.fields['series']
        series_qs = series_field.get_queryset()
        if series_qs:
            series_field.queryset = series_qs.filter(owner=user)

    def validate(self, attrs):
        attrs = super(PermitSerializer, self).validate(attrs)
        self._validate_areas(attrs)
        return attrs

    def _validate_areas(self, attrs):
        user = self.context['request'].user
        domain = self.instance.domain if self.instance else attrs['domain']
        areas = PermitArea.objects.for_user(user).filter(domain=domain)
        area_identifiers = set(x['area'] for x in attrs.get('areas', []))
        found = areas.filter(identifier__in=area_identifiers)
        if found.count() != len(area_identifiers):
            found_identifiers = found.values_list('identifier', flat=True)
            unknown_areas = sorted(area_identifiers - set(found_identifiers))
            unknown_list = ', '.join(unknown_areas)
            raise serializers.ValidationError({
                'areas': _("Unknown identifiers: {}").format(unknown_list),
            })


class PermitViewSet(viewsets.ModelViewSet):
    queryset = Permit.objects.all()
    serializer_class = PermitSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['series', 'external_id']

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(series__owner=self.request.user)


class ActivePermitByExternalIdSerializer(PermitSerializer):
    class Meta(PermitSerializer.Meta):
        read_only_fields = ['id', 'series']


class ActivePermitByExternalIdViewSet(viewsets.ModelViewSet):
    queryset = Permit.objects.active().exclude(external_id=None)
    serializer_class = ActivePermitByExternalIdSerializer
    lookup_field = 'external_id'

    def perform_create(self, serializer):
        latest_active_permit_series = (
            self.get_series_queryset().latest_active())
        if not latest_active_permit_series:
            raise NotFound(_("Active permit series doesn't exist"))
        serializer.save(series=latest_active_permit_series)

    def get_queryset(self):
        return super().get_queryset().filter(series__owner=self.request.user)

    def get_series_queryset(self):
        return PermitSeries.objects.filter(owner=self.request.user)
