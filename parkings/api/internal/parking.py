import django_filters
from django.utils import timezone
from rest_framework import permissions, serializers, viewsets

from parkings.models import Address, Parking


class InternalAPIAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('city', 'postal_code', 'street')


class InternalAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')
    address = InternalAPIAddressSerializer()

    class Meta:
        model = Parking
        fields = '__all__'


class InternalAPIParkingFilter(django_filters.rest_framework.FilterSet):
    status = django_filters.CharFilter(method='filter_status')
    registration_number = django_filters.CharFilter()
    time_start_gte = django_filters.DateTimeFilter(name='time_start', lookup_expr='gte')
    time_start_lte = django_filters.DateTimeFilter(name='time_start', lookup_expr='lte')
    time_end_gte = django_filters.DateTimeFilter(name='time_end', lookup_expr='gte')
    time_end_lte = django_filters.DateTimeFilter(name='time_end', lookup_expr='lte')

    class Meta:
        model = Parking
        fields = ('status', 'registration_number', 'time_start_gte', 'time_start_lte', 'time_end_gte', 'time_end_lte')

    def filter_status(self, queryset, name, value):
        now = timezone.now()

        if value == Parking.VALID:
            return queryset.filter(time_start__lte=now, time_end__gte=now)
        elif value == Parking.NOT_VALID:
            return queryset.exclude(time_start__lte=now, time_end__gte=now)

        return queryset


class InternalAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = InternalAPIParkingSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_class = InternalAPIParkingFilter
