from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, mixins, permissions, serializers, viewsets

from parkings.models import Address, Operator, Parking


class OperatorAPIAddressSerializer(serializers.ModelSerializer):
    city = serializers.CharField(required=True)
    postal_code = serializers.CharField(required=True)
    street = serializers.CharField(required=True)

    class Meta:
        model = Address
        fields = ('city', 'postal_code', 'street')


class OperatorAPIParkingSerializer(serializers.ModelSerializer):
    address = OperatorAPIAddressSerializer(allow_null=True, required=False)

    class Meta:
        model = Parking
        fields = '__all__'
        read_only_fields = ('operator',)

    @transaction.atomic
    def create(self, validated_data):
        address_data = validated_data.pop('address', None)

        if address_data:
            validated_data['address'], _ = Address.objects.get_or_create(
                city=address_data['city'],
                postal_code=address_data['postal_code'],
                street=address_data['street'],
            )

        return Parking.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        address_data = validated_data.get('address')

        if address_data:
            validated_data['address'], _ = Address.objects.get_or_create(
                city=address_data['city'],
                postal_code=address_data['postal_code'],
                street=address_data['street'],
            )

        for attr, value in validated_data.items():
            # does not handle many-to-many fields
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate(self, data):
        if self.instance and (now() - self.instance.created_at) > settings.PARKINGS_TIME_EDITABLE:
            if set(data.keys()) != {'time_end'}:
                raise exceptions.PermissionDenied(
                    _('Grace period has passed. Only "time_end" can be updated via PATCH.')
                )

        if self.instance:
            # a partial update might be missing one or both of the time fields
            time_start = data.get('time_start', self.instance.time_start)
            time_end = data.get('time_end', self.instance.time_end)
        else:
            time_start = data['time_start']
            time_end = data['time_end']

        if time_start > time_end:
            raise serializers.ValidationError(_('"time_start" cannot be after "time_end".'))

        return data


class OperatorAPIParkingPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow only operators to create/modify a parking.
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
        Allow operators to modify only their own parkings.
        """
        return request.user.operator == obj.operator


class OperatorAPIParkingViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    queryset = Parking.objects.all()
    serializer_class = OperatorAPIParkingSerializer
    permission_classes = (OperatorAPIParkingPermission,)

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user.operator)
