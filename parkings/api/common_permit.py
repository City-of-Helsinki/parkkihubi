from django.db import transaction
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from ..models import EnforcementDomain, Permit, PermitSeries


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
        with transaction.atomic():
            obj_to_activate = self.get_object()
            old_actives = self.queryset.filter(active=True)

            if obj_to_activate.active and old_actives.count() == 1:
                return Response({'status': 'No change'})

            if not obj_to_activate.active:
                obj_to_activate.active = True
                obj_to_activate.save()

            for obj in old_actives.exclude(pk=obj_to_activate.pk):
                obj.active = False
                obj.save()

            prunable_series = PermitSeries.objects.prunable()
            Permit.objects.filter(series__in=prunable_series).delete()
            prunable_series.delete()

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
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if self.instance is None:
            if attrs.get('domain', None) is None:
                attrs['domain'] = EnforcementDomain.get_default_domain()
            instance = Permit(self.instance, **attrs)
            instance.clean()
        else:
            instance = self.instance
            for key in attrs:
                setattr(instance, key, attrs[key])
            instance.clean()
        return super(PermitSerializer, self).validate(attrs)


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
        latest_active_permit_series = PermitSeries.objects.latest_active()
        if not latest_active_permit_series:
            raise NotFound(_("Active permit series doesn't exist"))
        serializer.save(series=latest_active_permit_series)

    def get_queryset(self):
        return super().get_queryset().filter(series__owner=self.request.user)
