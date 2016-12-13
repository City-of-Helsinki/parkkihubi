from rest_framework import mixins, permissions, serializers, viewsets

from parkings.models import Operator, Parking


class OperatorAPIParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        fields = '__all__'
        read_only_fields = ('operator',)


class OperatorAPIParkingPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow only operators to create a parking.
        """
        user = request.user

        if not user.is_authenticated():
            return False

        try:
            user.operator
            return True
        except Operator.DoesNotExist:
            pass

        return False

    def has_object_permission(self, request, view, obj):
        """
        Allow only operators to modify and only their own parkings.
        """
        user = request.user

        if not user.is_authenticated():
            return False

        try:
            operator = user.operator
        except Operator.DoesNotExist:
            return False

        return operator == obj.operator


class OperatorAPIParkingViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Parking.objects.all()
    serializer_class = OperatorAPIParkingSerializer
    permission_classes = (OperatorAPIParkingPermission,)

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user.operator)
