import django_filters
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets

from parkings.models import PermitArea

from ...models import PermitLookupItem
from .permissions import IsEnforcer


class ValidPermitItemSerializer(serializers.ModelSerializer):
    area = serializers.SlugRelatedField(slug_field='identifier', queryset=PermitArea.objects.all())
    operator = serializers.CharField(source='permit.series.owner.operator.id')
    operator_name = serializers.CharField(source='permit.series.owner.operator.name')

    class Meta:
        model = PermitLookupItem
        fields = [
            'area',
            'registration_number',
            'start_time',
            'end_time',
            'operator',
            'operator_name',
        ]


class ValidPermitItemFilter(django_filters.rest_framework.FilterSet):
    reg_num = django_filters.CharFilter(
        label=_("Registration number"), method='filter_reg_num')
    time = django_filters.IsoDateTimeFilter(
        label=_("Time"), method='filter_time')

    class Meta:
        model = PermitLookupItem
        fields = []

    def is_valid(self):
        super(ValidPermitItemFilter, self).is_valid()
        if not self.request.query_params.get("reg_num") and not self.request.query_params.get("time"):
            raise serializers.ValidationError(_("Either time or registration number required."))
        else:
            return True

    def filter_reg_num(self, queryset, name, value):
        return queryset.by_subject(value)

    def filter_time(self, queryset, name, value):
        return queryset.by_time(value)


class ValidPermitItemViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsEnforcer]
    queryset = PermitLookupItem.objects.active().order_by('end_time')
    serializer_class = ValidPermitItemSerializer
    filterset_class = ValidPermitItemFilter

    def get_queryset(self):
        return super().get_queryset().filter(permit__domain=self.request.user.enforcer.enforced_domain)
