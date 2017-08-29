import django_filters
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework_gis.filters import InBBoxFilter

from parkings.models import Parking


class ParkingFilter(django_filters.rest_framework.FilterSet):
    """
    Common filters in internal and public API.
    """
    time_end__gte = django_filters.IsoDateTimeFilter(method='filter_time_end__gte')

    class Meta:
        model = Parking
        fields = {
            'time_start': ['lte', 'gte'],
            'time_end': ['lte'],
        }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': django_filters.IsoDateTimeFilter,
            },
        }

    # we need to implement this manually to include parkings with no end_time
    def filter_time_end__gte(self, queryset, name, value):
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
