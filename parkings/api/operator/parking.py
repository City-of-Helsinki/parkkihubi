from rest_framework import mixins, serializers, viewsets

from parkings.models import Parking


class OperatorAPIParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = '__all__'


class OperatorAPIParkingViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Parking.objects.all()
    serializer_class = OperatorAPIParkingSerializer
