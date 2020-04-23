import rest_framework_gis.serializers as gis_serializers
from rest_framework import serializers

from ...models import Parking, PaymentZone


class ParkingSerializer(gis_serializers.GeoFeatureModelSerializer):
    operator_name = serializers.CharField(
        source='operator.name', read_only=True)
    zone = serializers.SlugRelatedField(
        slug_field='code', queryset=PaymentZone.objects.all())

    class Meta:
        model = Parking
        fields = [
            'id',
            'registration_number',
            'location',
            'region',
            'zone',
            'terminal_number',
            'operator_name',
            'time_start',
            'time_end',
            'created_at',
            'modified_at',
        ]
        geo_field = 'location'  # Stored already in SRID 4326 / WGS84

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.zone:
            representation['properties']['zone'] = instance.zone.casted_code
        return representation
