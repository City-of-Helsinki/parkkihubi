from rest_framework import viewsets
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField

from parkings.models import ParkingArea

from ..common import WGS84InBBoxFilter


class ParkingAreaSerializer(GeoFeatureModelSerializer):
    wgs84_areas = GeometrySerializerMethodField()

    def get_wgs84_areas(self, area):
        return area.areas.transform(4326, clone=True)

    class Meta:
        model = ParkingArea
        geo_field = 'wgs84_areas'
        fields = (
            'id',
            'space_amount_estimate',
        )


class PublicAPIParkingAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ParkingArea.objects.all()
    serializer_class = ParkingAreaSerializer
    pagination_class = GeoJsonPagination
    bbox_filter_field = 'areas'
    filter_backends = (WGS84InBBoxFilter,)
    bbox_filter_include_overlapping = True
