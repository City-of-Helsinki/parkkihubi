from rest_framework import serializers, viewsets

from ...models import Region
from ...pagination import Pagination
from ..common import WGS84InBBoxFilter
from ..utils import parse_timestamp_or_now
from .permissions import IsMonitor


class RegionStatisticsSerializer(serializers.ModelSerializer):
    parking_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Region
        fields = (
            'id',
            'parking_count',
        )


class RegionStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsMonitor]
    queryset = Region.objects.all()
    serializer_class = RegionStatisticsSerializer
    pagination_class = Pagination
    bbox_filter_field = 'geom'
    filter_backends = [WGS84InBBoxFilter]
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        time = parse_timestamp_or_now(self.request.query_params.get('time'))
        return (
            super().get_queryset()
            .with_parking_count(time)
            .values('id', 'parking_count')
            .order_by('id')
            .filter(parking_count__gt=0, domain=self.request.user.monitor.domain))
