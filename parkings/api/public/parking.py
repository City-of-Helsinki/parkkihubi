from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers, viewsets

from parkings.models import Parking


class PublicAPIParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = ('id', 'parking_area', 'location', 'time_start', 'time_end', 'zone')
        ordering = ('time_start',)


class PublicAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = PublicAPIParkingSerializer

    def get_queryset(self):
        time_parkings_hidden = getattr(settings, 'PARKKIHUBI_TIME_PARKINGS_HIDDEN', timedelta(days=7))
        return super().get_queryset().filter(time_end__lte=(timezone.now() - time_parkings_hidden))
