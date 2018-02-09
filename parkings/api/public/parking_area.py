from rest_framework import permissions, viewsets
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer, GeometrySerializerMethodField)

from parkings.models import ParkingArea

from ..common import WGS84InBBoxFilter


class ParkingAreaSerializer(GeoFeatureModelSerializer):
    wgs84_areas = GeometrySerializerMethodField()

    def get_wgs84_areas(self, area):
        return area.geom.transform(4326, clone=True)

    class Meta:
        model = ParkingArea
        geo_field = 'wgs84_areas'
        fields = (
            'id',
            'capacity_estimate',
        )


class PublicAPIParkingAreaViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = ParkingArea.objects.order_by('origin_id')
    serializer_class = ParkingAreaSerializer
    pagination_class = GeoJsonPagination
    bbox_filter_field = 'geom'
    filter_backends = (WGS84InBBoxFilter,)
    bbox_filter_include_overlapping = True
