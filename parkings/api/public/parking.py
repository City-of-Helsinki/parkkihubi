from datetime import timedelta

import django_filters
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework_gis.filters import InBBoxFilter

from parkings.models import Parking


class PublicAPIParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ('id', 'parking_area', 'location', 'time_start', 'time_end', 'zone')
        ordering = ('time_start',)


class UUIDInFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class PublicAPIParkingFilter(django_filters.rest_framework.FilterSet):
    time_start_gte = django_filters.IsoDateTimeFilter(name='time_start', lookup_expr='gte')
    time_start_lte = django_filters.IsoDateTimeFilter(name='time_start', lookup_expr='lte')
    time_end_gte = django_filters.IsoDateTimeFilter(name='time_end', lookup_expr='gte')
    time_end_lte = django_filters.IsoDateTimeFilter(name='time_end', lookup_expr='lte')
    parking_area = UUIDInFilter(name='parking_area_id', widget=django_filters.widgets.CSVWidget())
    zone = NumberInFilter(name='zone', widget=django_filters.widgets.CSVWidget())

    class Meta:
        model = Parking
        fields = ('time_start_gte', 'time_start_lte', 'time_end_gte', 'time_end_lte', 'parking_area', 'zone')


class PublicAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = PublicAPIParkingSerializer
    filter_class = PublicAPIParkingFilter
    bbox_filter_field = 'location'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, InBBoxFilter)

    def get_queryset(self):
        time_parkings_hidden = getattr(settings, 'PARKKIHUBI_TIME_PARKINGS_HIDDEN', timedelta(days=7))
        return super().get_queryset().filter(time_end__lte=(timezone.now() - time_parkings_hidden))
