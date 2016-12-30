from rest_framework import permissions, serializers, viewsets

from parkings.models import Parking

from ..common import AddressSerializer, ParkingFilter


class InternalAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Parking
        fields = '__all__'


class InternalAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = InternalAPIParkingSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_class = ParkingFilter
