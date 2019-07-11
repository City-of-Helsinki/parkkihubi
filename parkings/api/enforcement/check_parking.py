from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, generics, permissions, serializers
from rest_framework.response import Response

from ...models import (
    Parking, PaymentZone, Permit, PermitArea, PermitLookupItem)


class UnknownLocationException(exceptions.APIException):
    status_code = 404
    default_detail = _('Location was not found.')
    default_code = 'unknown_location_error'


def permit_area_by_location(longitude, latitude):
    location = Point(longitude, latitude, srid=4326)
    area = PermitArea.objects.filter(geom__contains=location.transform(3879, clone=True)).first()
    return area


def parking_zone_by_location(longitude, latitude):
    location = Point(longitude, latitude, srid=4326)
    zone = PaymentZone.objects.filter(geom__contains=location.transform(3879, clone=True)).first()
    return zone


class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class CheckParkingSerializer(serializers.Serializer):
    registration_number = serializers.CharField(max_length=30)
    location = LocationSerializer()
    time = serializers.DateTimeField(required=False)


class CheckParking(generics.GenericAPIView):
    """
    Check if parking is valid at the current time for given registration number and location.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CheckParkingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            time = serializer.validated_data.get('time') or timezone.now()
            registration_number = Parking.normalize_reg_num(
                serializer.validated_data.get("registration_number"))
            longitude = serializer.validated_data["location"]["longitude"]
            latitude = serializer.validated_data["location"]["latitude"]

            zone = parking_zone_by_location(longitude, latitude)
            area = permit_area_by_location(longitude, latitude)
            if not zone and not area:
                raise UnknownLocationException()

            if zone:
                valid_parking_instance = (
                    Parking.objects.filter(zone__lte=zone.number)
                    .registration_number_like(registration_number)
                    .valid_at(time)
                    .order_by("-time_end")
                    .first()
                )
                if valid_parking_instance:
                    return Response({"status": "valid", "end_time": valid_parking_instance.time_end})

            if area:
                valid_permits = (
                    Permit.objects.active()
                    .by_time(time)
                    .by_subject(registration_number)
                    .by_area(area.identifier)
                )
                valid_permitlookups = (
                    PermitLookupItem.objects.filter(
                        permit__in=valid_permits,
                        registration_number=registration_number,
                        area_identifier=area.identifier,
                    )
                    .order_by("-end_time")
                    .first()
                )
                if valid_permitlookups:
                    return Response({"status": "valid",
                                     "end_time": valid_permitlookups.end_time})

            return Response({"status": "invalid"})
