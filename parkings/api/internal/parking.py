from rest_framework import permissions, serializers, viewsets

from parkings.authentication import ApiKeyAuthentication
from parkings.models import Parking

from ..common import ParkingFilter


class InternalAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')

    class Meta:
        model = Parking
        fields = '__all__'


class InternalAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = InternalAPIParkingSerializer
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    filter_class = ParkingFilter
