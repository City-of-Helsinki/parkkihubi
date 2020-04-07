
import datetime

import django_filters
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets

from ...models import PermitLookupItem
from .permissions import IsEnforcer


class ValidPermitSerializer(serializers.ModelSerializer):
    modified_at = serializers.DateTimeField(source="permit.modified_at")
    created_at = serializers.DateTimeField(source="permit.created_at")
    area = serializers.CharField(source="area.identifier")
    id = serializers.IntegerField(source="permit.id")

    class Meta:
        model = PermitLookupItem
        fields = (
            'id', 'created_at', 'modified_at', 'area',
            'registration_number',
            'start_time', 'end_time',
        )

class ValidPermitFilter(django_filters.rest_framework.FilterSet):
    reg_num = django_filters.CharFilter(
        label=_("Registration number"), method='filter_reg_num')
    time = django_filters.IsoDateTimeFilter(
        label=_("Time"), method='filter_time')

    class Meta:
        model = PermitLookupItem
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
        Filter to valid permits at given time stamp.

        :type queryset: parkings.models.ParkingQuerySet
        :type name: str
        :type value: datetime.datetime
        """
        time = value if value else timezone.now()
        valid_permits = queryset.by_time(time).active()
        return valid_permits

    def is_valid(self):
        super(ValidPermitFilter, self).is_valid()
        if not self.request.query_params.get("reg_num") and not self.request.query_params.get("time"):
            raise serializers.ValidationError(_("Either time or registration number required."))
        else:
            return True

class ValidPermitViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsEnforcer]
    queryset = PermitLookupItem.objects.all()
    serializer_class = ValidPermitSerializer
    filterset_class = ValidPermitFilter

    def get_queryset(self):
        return super().get_queryset().filter(permit__domain=self.request.user.enforcer.enforced_domain)
