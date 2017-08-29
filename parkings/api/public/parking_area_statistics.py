from django.db.models import Case, Count, When
from django.utils import timezone
from rest_framework import serializers, viewsets

from parkings.models import ParkingArea
from parkings.pagination import PublicAPIPagination

from ..common import WGS84InBBoxFilter


class ParkingAreaStatisticsSerializer(serializers.ModelSerializer):
    current_parking_count = serializers.SerializerMethodField()

    def get_current_parking_count(self, area):
        return self.blur_count(area['current_parking_count'])

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
    pagination_class = PublicAPIPagination
    bbox_filter_field = 'geom'
    filter_backends = (WGS84InBBoxFilter,)
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        now = timezone.now()

        return ParkingArea.objects.annotate(
            current_parking_count=Count(
                Case(
                    When(
                        parking__time_start__lte=now,
                        parking__time_end__gte=now,
                        then=1,
                    )
                )
            )
        ).values('id', 'current_parking_count').order_by('origin_id')
