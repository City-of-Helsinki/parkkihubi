import django_filters
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework_gis.filters import InBBoxFilter

from parkings.models import Parking


class ParkingFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.CharFilter(method='filter_status')
    registration_number = django_filters.CharFilter()
    time_start_gte = django_filters.DateTimeFilter(name='time_start', lookup_expr='gte')
    time_start_lte = django_filters.DateTimeFilter(name='time_start', lookup_expr='lte')
    time_end_gte = django_filters.DateTimeFilter(method='filter_time_end_gte')
    time_end_lte = django_filters.DateTimeFilter(name='time_end', lookup_expr='lte')

    class Meta:
        model = Parking
        fields = ('status', 'registration_number', 'time_start_gte', 'time_start_lte', 'time_end_gte', 'time_end_lte')

    def filter_status(self, queryset, name, value):
        now = timezone.now()
        valid_parkings = Q(time_start__lte=now) & (Q(time_end__gte=now) | Q(time_end__isnull=True))

        if value == Parking.VALID:
            return queryset.filter(valid_parkings)
        elif value == Parking.NOT_VALID:
            return queryset.exclude(valid_parkings)

        return queryset

    # we need to implement this manually to include parkings with no end_time
    def filter_time_end_gte(self, queryset, name, value):
        return queryset.filter(Q(time_end__gte=value) | Q(time_end__isnull=True))


class ParkingException(exceptions.APIException):
    status_code = 403
    default_detail = _('Unknown error.')
    default_code = 'unknown_error'


class WGS84InBBoxFilter(InBBoxFilter):
    """Works like a normal InBBoxFilter but converts WGS84 to ETRS89"""
    def get_filter_bbox(self, request):
        bbox = super().get_filter_bbox(request)
        if bbox is None:
            return bbox

        bbox.srid = 4326
        bbox.transform(3879)
        return bbox
