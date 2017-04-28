from django.utils import timezone
from rest_framework import serializers, viewsets

from parkings.models import Parking, ParkingArea

from ..common import WGS84InBBoxFilter


class ParkingAreaStatisticsSerializer(serializers.ModelSerializer):
    current_parking_count = serializers.SerializerMethodField()

    def get_current_parking_count(self, area):
        count = Parking.objects.filter(
            parking_area=area,
            time_end__gte=timezone.now(),
            time_start__lte=timezone.now(),
        ).count()
        return self.blur_count(count)

    def blur_count(self, count):
        """
        Returns a blurred count, which is supposed to hide individual
        parkings.
        """
        if count <= 3:
            return 0
        else:
            return count

    class Meta:
        model = ParkingArea
        fields = (
            'id',
            'current_parking_count',
        )


class PublicAPIParkingAreaStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ParkingArea.objects.all()
    serializer_class = ParkingAreaStatisticsSerializer
    bbox_filter_field = 'areas'
    filter_backends = (WGS84InBBoxFilter,)
    bbox_filter_include_overlapping = True
