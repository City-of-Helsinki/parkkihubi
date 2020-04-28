import rest_framework_gis.pagination as gis_pagination
import rest_framework_gis.serializers as gis_serializers
from rest_framework import serializers, viewsets

from ...models import ParkingArea, Region
from ..common import WGS84InBBoxFilter
from .permissions import IsMonitor

WGS84_SRID = 4326

# Square meters in square kilometer
M2_PER_KM2 = 1000000.0


class RegionSerializer(gis_serializers.GeoFeatureModelSerializer):
    wgs84_geometry = gis_serializers.GeometrySerializerMethodField()
    area_km2 = serializers.SerializerMethodField()
    spots_per_km2 = serializers.SerializerMethodField()
    parking_areas = serializers.SerializerMethodField()

    def get_wgs84_geometry(self, instance):
        return instance.geom.transform(WGS84_SRID, clone=True)

    def get_area_km2(self, instance):
        return instance.geom.area / M2_PER_KM2

    def get_spots_per_km2(self, instance):
        return M2_PER_KM2 * instance.capacity_estimate / instance.geom.area

    def get_parking_areas(self, instance):
        parking_areas = ParkingArea.objects.intersecting_region(instance)
        return [x.pk for x in parking_areas]

    class Meta:
        model = Region
        geo_field = 'wgs84_geometry'
        fields = [
            'id',
            'name',
            'capacity_estimate',
            'area_km2',
            'spots_per_km2',
            'parking_areas',
        ]


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsMonitor]
    queryset = Region.objects.all().order_by('id')
    serializer_class = RegionSerializer
    pagination_class = gis_pagination.GeoJsonPagination
    bbox_filter_field = 'geom'
    filter_backends = [WGS84InBBoxFilter]
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        return super().get_queryset().filter(domain=self.request.user.monitor.domain)
