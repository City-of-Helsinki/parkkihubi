import django_filters
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets

from ...models import PermitArea, PermitLookupItem
from ...pagination import CursorPagination
from .permissions import IsEnforcer


class ValidPermitItemSerializer(serializers.ModelSerializer):
    permit_id = serializers.IntegerField(source='permit.id')
    area = serializers.SlugRelatedField(slug_field='identifier', queryset=PermitArea.objects.all())
    operator = serializers.CharField(source='permit.series.owner.operator.id')
    operator_name = serializers.CharField(source='permit.series.owner.operator.name')
    properties = serializers.JSONField(source='permit.properties')

    class Meta:
        model = PermitLookupItem
        fields = [
            'id',
            'permit_id',
            'area',
            'registration_number',
            'start_time',
            'end_time',
            'operator',
            'operator_name',
            'properties',
        ]


class ValidPermitItemFilter(django_filters.rest_framework.FilterSet):
    reg_num = django_filters.CharFilter(
        label=_("Registration number"), method='filter_reg_num')
    time = django_filters.IsoDateTimeFilter(
        label=_("Time"), method='filter_time')

    class Meta:
        model = PermitLookupItem
        fields = []

    def filter_reg_num(self, queryset, name, value):
        return queryset.by_subject(value)

    def filter_time(self, queryset, name, value):
        return queryset.by_time(value)


class ValidPermitItemViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsEnforcer]
    queryset = PermitLookupItem.objects.active()
    serializer_class = ValidPermitItemSerializer
    filterset_class = ValidPermitItemFilter
    pagination_class = CursorPagination

    def get_queryset(self):
        domain = self.request.user.enforcer.enforced_domain
        return super().get_queryset().filter(permit__domain=domain)
