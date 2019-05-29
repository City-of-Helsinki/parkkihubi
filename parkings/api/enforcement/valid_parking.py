import datetime

import django_filters
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, serializers, viewsets

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
        label=_("Registration number"), method='filter_reg_num', required=True)
    time = django_filters.IsoDateTimeFilter(
        label=_("Time"), method='filter_time')

    class Meta:
        model = Parking
        fields = []

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

        :type queryset: parkings.models.ParkingQuerySet
        :type name: str
        :type value: datetime.datetime
        """
        time = value if value else timezone.now()
        valid_parkings = queryset.valid_at(time)
        return valid_parkings


class ValidParkingViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Parking.objects.order_by('-time_end')
    serializer_class = ValidParkingSerializer
    filter_class = ValidParkingFilter

    def filter_queryset(self, queryset):
        """
        Filter the queryset by given filters.

        If there is no valid parkings for the given registration number
        at given time, but there is a parking that was valid within
        grace duration (G) from given time, then return the parking that
        has the latest ending time and has started before the given time.

        The grace duration G defaults to 15 minutes, but is configurable
        with the PARKKIHUBI_TIME_OLD_PARKINGS_VISIBLE setting.
        """
        filtered_queryset = super().filter_queryset(queryset)

        if filtered_queryset:
            return filtered_queryset

        return self._filter_last_valid_if_within_grace_duration(queryset)

    def _filter_last_valid_if_within_grace_duration(self, queryset):
        """
        Filter to last valid parking if it ends within grace duration.
        """
        filter_params = self._get_filter_params(queryset)
        reg_num = filter_params['reg_num']
        time = filter_params.get('time') or timezone.now()
        some_time_ago = time - get_grace_duration()
        valid_some_time_ago = (
            queryset
            .registration_number_like(reg_num)
            .ends_after(some_time_ago)
            .starts_before(time))

        return valid_some_time_ago.order_by('-time_end')[:1]

    def _get_filter_params(self, queryset):
        filterset = self._get_filterset(queryset)
        is_valid = filterset.is_valid()
        assert is_valid
        return filterset.form.cleaned_data

    def _get_filterset(self, queryset):
        filter_backend = self.filter_backends[0]()
        return filter_backend.get_filterset(self.request, queryset, self)


def get_grace_duration(default=datetime.timedelta(minutes=15)):
    value = getattr(settings, 'PARKKIHUBI_TIME_OLD_PARKINGS_VISIBLE', None)
    assert value is None or isinstance(value, datetime.timedelta)
    return value if value is not None else default
