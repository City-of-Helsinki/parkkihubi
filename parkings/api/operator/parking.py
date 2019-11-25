import pytz
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos.point import Point
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, permissions, serializers, viewsets
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from parkings.api.enforcement.check_parking import LocationSerializer
from parkings.models import Operator, Parking, ParkingTerminal

from ..common import ParkingException


class OperatorAPIParkingSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_state')

    class Meta:
        model = Parking
        fields = (
            'id', 'created_at', 'modified_at',
            'location', 'terminal_number',
            'registration_number',
            'time_start', 'time_end',
            'zone',
            'status',
        )

        # these are needed because by default a PUT request that does not contain some optional field
        # works the same way as PATCH would, ie. not updating that field to null on the target object,
        # which seems wrong. see https://github.com/encode/django-rest-framework/issues/3648
        extra_kwargs = {
            'location': {'default': None},
            'terminal_number': {'default': ''},
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


class ParkingRulesSerializer(serializers.Serializer):
    after = serializers.DateTimeField()
    policy = serializers.CharField()
    maximum_duration = serializers.IntegerField()


class ParkingLotInfoSerializer(serializers.Serializer):
    location = LocationSerializer()
    zone = serializers.IntegerField()
    terminal_number = serializers.CharField()
    rules = serializers.ListField(child=ParkingRulesSerializer())


class OperatorAPIParkingPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allow only operators to create/modify a parking.
        """
        user = request.user

        if not user.is_authenticated:
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
    permission_classes = [OperatorAPIParkingPermission]
    queryset = Parking.objects.order_by('time_start')
    serializer_class = OperatorAPIParkingSerializer

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user.operator)

    def get_queryset(self):
        return super().get_queryset().filter(operator=self.request.user.operator)


class OperatorAPIParkingLotInfo(GenericAPIView):
    """
    Fetch information with a POST request about a specific parking lot with either location coordinates
    or terminal number. The information includes the location (coordinates), zone, terminal
    number and a list of parking rules related to the queried parking lot.
    """
    permission_classes = [OperatorAPIParkingPermission]
    serializer_class = ParkingLotInfoSerializer
    http_method_names = ['post']

    def post(self, request):
        location = request.data.get('location')
        terminal_number = request.data.get('terminal_number')

        if not location and not terminal_number:
            raise ParseError(detail='No search parameters entered.')

        terminal_obj = self._get_terminal_object(
            coordinates=location.get('coordinates') if location else None,
            terminal_number=terminal_number if terminal_number else None)
        data = self._get_serializer_data(terminal_obj)
        serializer = self.get_serializer(data=data)

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)

    def _get_serializer_data(self, terminal):
        if not terminal:
            return {}

        return {
            'location': {
                'longitude': terminal.location.x,
                'latitude': terminal.location.y,
            },
            'zone': terminal.zone,
            'terminal_number': terminal.number,
            'rules': [  # TODO: the rules are static data for now.
                {
                    'after': '1970-01-01T00:00',
                    'policy': 'unknown',
                    'maximum_duration': 60,
                },
            ]
        }

    def _get_terminal_object(self, coordinates=None, terminal_number=None):
        terminal = (
            get_object_or_404(ParkingTerminal, number=terminal_number) if terminal_number
            else self._get_closest_terminal_with_location(coordinates))

        if not terminal:
            raise NotFound(detail='No terminal was found.')

        return terminal

    def _get_closest_terminal_with_location(self, coordinates):
        """
        Get the parking terminal which is within 100m to
        the coordinates in a location JSON object taken
        from the POST data.

        :param coordinates: List of x and y coordinates.
        :return: ParkingTerminal Object.
        """
        if not coordinates or len(coordinates) != 2:
            return None

        location_point = Point(x=coordinates[0], y=coordinates[1], srid=4326)
        closest_terminal = ParkingTerminal.objects.annotate(
            distance=Distance('location', location_point)
        ).filter(distance__lte=100).order_by('distance').first()

        return closest_terminal
