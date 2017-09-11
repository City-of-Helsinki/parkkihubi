import pytz
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, permissions, serializers, viewsets

from parkings.authentication import ApiKeyAuthentication
from parkings.models import Operator, Parking

from ..common import ParkingException, ParkingFilter


class OperatorAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')

    class Meta:
        model = Parking
        fields = (
            'id', 'created_at', 'modified_at', 'location', 'registration_number', 'time_start', 'time_end', 'zone',
            'status',
        )

        # these are needed because by default a PUT request that does not contain some optional field
        # works the same way as PATCH would, ie. not updating that field to null on the target object,
        # which seems wrong. see https://github.com/encode/django-rest-framework/issues/3648
        extra_kwargs = {
            'location': {'default': None},
            'time_end': {'default': None},
        }

    def __init__(self, *args, **kwargs):
        super(OperatorAPIParkingSerializer, self).__init__(*args, **kwargs)
        self.fields['time_start'].timezone = pytz.utc
        self.fields['time_end'].timezone = pytz.utc

    def validate(self, data):
        if self.instance and (now() - self.instance.created_at) > settings.PARKKIHUBI_TIME_PARKINGS_EDITABLE:
            if set(data.keys()) != {'time_end'}:
                raise ParkingException(
                    _('Grace period has passed. Only "time_end" can be updated via PATCH.'),
                    code='grace_period_over',
                )

        if self.instance:
            # a partial update might be missing one or both of the time fields
            time_start = data.get('time_start', self.instance.time_start)
            time_end = data.get('time_end', self.instance.time_end)
        else:
            time_start = data['time_start']
            time_end = data['time_end']

        if time_end is not None and time_start > time_end:
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
    queryset = Parking.objects.order_by('time_start')
    serializer_class = OperatorAPIParkingSerializer
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (OperatorAPIParkingPermission,)
    filter_class = ParkingFilter

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user.operator)

    def get_queryset(self):
        return super().get_queryset().filter(operator=self.request.user.operator)
