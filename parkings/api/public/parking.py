from datetime import timedelta

import django_filters
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework_gis.filters import InBBoxFilter

from parkings.models import Parking

from ..common import ParkingFilter


class PublicAPIParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ('id', 'parking_area', 'location', 'time_start', 'time_end', 'zone')
        ordering = ('time_start',)


class UUIDInFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class PublicAPIParkingFilter(ParkingFilter):
    parking_area = UUIDInFilter(name='parking_area_id', widget=django_filters.widgets.CSVWidget())
    zone = NumberInFilter(name='zone', widget=django_filters.widgets.CSVWidget())


class PublicAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.order_by('time_start')
    serializer_class = PublicAPIParkingSerializer
    filter_class = PublicAPIParkingFilter
    bbox_filter_field = 'location'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, InBBoxFilter)

    def get_queryset(self):
        time_parkings_hidden = getattr(settings, 'PARKKIHUBI_TIME_PARKINGS_HIDDEN', timedelta(days=7))
        return super().get_queryset().filter(
            time_end__lte=(timezone.now() - time_parkings_hidden)
        ).exclude(
            time_end__isnull=True
        )
