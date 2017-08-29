from copy import deepcopy

import django_filters
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, serializers, viewsets

from parkings.authentication import ApiKeyAuthentication
from parkings.models import Parking

from ..common import ParkingFilter


class InternalAPIParkingFilter(ParkingFilter):
    status = django_filters.CharFilter(method='filter_status')

    class Meta(ParkingFilter.Meta):
        fields = deepcopy(ParkingFilter.Meta.fields)
        fields.update({
            'registration_number': ['exact'],
        })

    def filter_status(self, queryset, name, value):
        now = timezone.now()
        valid_parkings = Q(time_start__lte=now) & (Q(time_end__gte=now) | Q(time_end__isnull=True))

        if value == Parking.VALID:
            return queryset.filter(valid_parkings)
        elif value == Parking.NOT_VALID:
            return queryset.exclude(valid_parkings)

        return queryset


class InternalAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')

    class Meta:
        model = Parking
        fields = '__all__'


class InternalAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.order_by('time_start')
    serializer_class = InternalAPIParkingSerializer
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    filter_class = InternalAPIParkingFilter
