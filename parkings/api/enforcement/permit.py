from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Permit, PermitSeries


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
    permission_classes = [permissions.IsAdminUser]
    queryset = PermitSeries.objects.all()
    serializer_class = PermitSeriesSerializer

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

            return Response({'status': 'OK'})


class PermitListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        permits = [Permit(**item) for item in validated_data]
        return Permit.objects.bulk_create(permits)


class PermitSerializer(serializers.ModelSerializer):
    subjects = serializers.ListField(
        child=serializers.CharField(max_length=20),
        max_length=40)

    areas = serializers.ListField(
        child=serializers.CharField(max_length=5),
        max_length=33)

    class Meta:
        list_serializer_class = PermitListSerializer
        model = Permit
        fields = [
            'id',
            'series',
            'external_id',
            'start_time',
            'end_time',
            'subjects',
            'areas',
        ]
        read_only_fields = ['id', 'series']


class PermitViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Permit.objects.all()
    serializer_class = PermitSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['series', 'external_id']

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class ActivePermitByExternalIdViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Permit.objects.active().exclude(external_id=None)
    serializer_class = PermitSerializer
    lookup_field = 'external_id'
