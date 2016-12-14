from django.utils import timezone
from rest_framework import permissions, serializers, viewsets

from parkings.models import Parking


class InternalAPIParkingSerializer(serializers.ModelSerializer):
    #is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Parking
        fields = '__all__'

    #def get_is_valid(self, obj):
    #    return obj.time_start <= timezone.now() <= obj.time_end


class InternalAPIParkingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parking.objects.all()
    serializer_class = InternalAPIParkingSerializer
    permission_classes = (permissions.IsAdminUser,)
