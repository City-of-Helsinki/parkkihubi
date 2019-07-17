import datetime

from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response

from ...models import (
    Parking, ParkingCheck, PaymentZone, PermitArea, PermitLookupItem)
from ...models.constants import GK25FIN_SRID, WGS84_SRID


class AwareDateTimeField(serializers.DateTimeField):
    default_error_messages = dict(
        serializers.DateField.default_error_messages,
        timezone="Timezone is required",
    )

    def enforce_timezone(self, value):
        if not timezone.is_aware(value):
            self.fail('timezone')
        return super().enforce_timezone(value)


class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)


class CheckParkingSerializer(serializers.Serializer):
    registration_number = serializers.CharField(max_length=20)
    location = LocationSerializer()
    time = AwareDateTimeField(required=False)


class CheckParking(generics.GenericAPIView):
    """
    Check if parking is valid for given registration number and location.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CheckParkingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        # Parse input parameters with the serializer
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        # Read input parameters to variables
        time = params.get("time") or timezone.now()
        registration_number = params.get("registration_number")
        (wgs84_location, gk25_location) = get_location(params)

        zone = get_payment_zone(gk25_location)
        area = get_permit_area(gk25_location)

        (allowed_by, parking, end_time) = check_parking(
            registration_number, zone, area, time)

        allowed = bool(allowed_by)

        if not allowed:
            # If no matching parking or permit was found, try to find
            # one that has just expired, i.e. was valid a few minutes
            # ago (where "a few minutes" is the grace duration)
            past_time = time - get_grace_duration()
            (_allowed_by, parking, end_time) = check_parking(
                registration_number, zone, area, past_time)

        result = {
            "allowed": allowed,
            "end_time": end_time,
            "location": {
                "payment_zone": zone,
                "permit_area": area,
            },
            "time": time,
        }

        ParkingCheck.objects.create(
            time=time,
            time_overridden=bool(params.get("time")),
            registration_number=registration_number,
            location=wgs84_location,
            result=result,
            allowed=allowed,
            found_parking=parking,
        )

        return Response(result)


def get_location(params):
    longitude = params["location"]["longitude"]
    latitude = params["location"]["latitude"]
    wgs84_location = Point(longitude, latitude, srid=WGS84_SRID)
    gk25_location = wgs84_location.transform(GK25FIN_SRID, clone=True)
    return (wgs84_location, gk25_location)


def get_payment_zone(location):
    zone_numbers = (
        PaymentZone.objects
        .filter(geom__contains=location)
        .order_by("-number")[:1]
        .values_list("number", flat=True))
    return zone_numbers[0] if zone_numbers else None


def get_permit_area(location):
    area = PermitArea.objects.filter(geom__contains=location).first()
    return area.identifier if area else None


def check_parking(registration_number, zone, area, time):
    """
    Check parking allowance from the database.

    :type registration_number: str
    :type zone: int|None
    :type area: str|None
    :type time: datetime.datetime
    :rtype: (str, Parking|None, datetime.datetime)
    """
    active_parkings = (
        Parking.objects
        .registration_number_like(registration_number)
        .valid_at(time)
        .only("id", "zone", "time_end"))
    for parking in active_parkings:
        if zone is None or parking.zone <= zone:
            return ("parking", parking, parking.time_end)

    if area:
        permit_end_time = (
            PermitLookupItem.objects
            .active()
            .by_time(time)
            .by_subject(registration_number)
            .by_area(area)
            .values_list("end_time", flat=True)
            .first())

        if permit_end_time:
            return ("permit", None, permit_end_time)

    return (None, None, None)


def get_grace_duration(default=datetime.timedelta(minutes=15)):
    setting = getattr(settings, "PARKKIHUBI_TIME_OLD_PARKINGS_VISIBLE", None)
    result = setting if setting is not None else default
    assert isinstance(result, datetime.timedelta)
    return result
