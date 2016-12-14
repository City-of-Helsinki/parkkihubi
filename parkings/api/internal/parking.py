from rest_framework import permissions, serializers, viewsets

from parkings.models import Parking


class InternalAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')

    class Meta:
        model = Parking
        fields = '__all__'


class InternalAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = InternalAPIParkingSerializer
    permission_classes = (permissions.IsAdminUser,)
