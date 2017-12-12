import datetime

import django_filters
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, serializers, viewsets

from ...authentication import ApiKeyAuthentication
from ...models import Parking


class ValidParkingSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.name')

    class Meta:
        model = Parking
        fields = [
            'id',
            'created_at',
            'modified_at',
            'registration_number',
            'time_start',
            'time_end',
            'zone',
            'operator',
            'operator_name',
        ]


class ValidParkingFilter(django_filters.rest_framework.FilterSet):
    reg_num = django_filters.CharFilter(
        name='reg_num', label=_("Registration number"),
        method='filter_reg_num', required=True)
    time = django_filters.IsoDateTimeFilter(
        name='time', label=_("Time"),
        method='filter_time')

    class Meta:
        model = Parking
        fields = []
        strict = django_filters.STRICTNESS.RAISE_VALIDATION_ERROR

    def __init__(self, data=None, *args, **kwargs):
        """
        Initialize filter set with given query data.

        :type data: django.http.request.QueryDict
        """
        if data and 'time' not in data:
            data = data.copy()
            data.setdefault('time', timezone.now())
        super().__init__(data, *args, **kwargs)

    def filter_reg_num(self, queryset, name, value):
        """
        Filter by normalized registration number.

        :type queryset: parkings.models.ParkingQuerySet
        :type name: str
        :type value: str
        """
        return queryset.registration_number_like(value)

    def filter_time(self, queryset, name, value):
        """
        Filter to valid parkings at given time stamp.

        If there is no valid parkings at given time, but there is a
        parking within a day from given time, then return the parking
        that has the latest ending time.

        :type queryset: parkings.models.ParkingQuerySet
        :type name: str
        :type value: datetime.datetime
        """
        time = value if value else timezone.now()
        valid_parkings = queryset.valid_at(time)
        if valid_parkings:
            return valid_parkings
        limit = time - get_time_old_parkings_visible()
        valid_within_limit = queryset.starts_before(time).ends_after(limit)
        return valid_within_limit.order_by('-time_end')[:1]


def get_time_old_parkings_visible(default=datetime.timedelta(minutes=15)):
    value = getattr(settings, 'PARKKIHUBI_TIME_OLD_PARKINGS_VISIBLE', None)
    assert value is None or isinstance(value, datetime.timedelta)
    return value if value is not None else default


class ValidParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.order_by('-time_end')
    serializer_class = ValidParkingSerializer
    filter_class = ValidParkingFilter
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAdminUser]
