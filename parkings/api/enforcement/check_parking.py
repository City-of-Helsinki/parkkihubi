from django.contrib.gis.geos import Point
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Parking, PaymentZone, Permit, PermitArea, PermitCacheItem


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
    latitude = serializers.CharField(max_length=200)
    longitude = serializers.CharField(max_length=200)


class CheckParkingSerializer(serializers.Serializer):
    registration_number = serializers.CharField(max_length=30)
    location = LocationSerializer()


class CheckParking(APIView):
    """
    Check if parking is valid at the current time for given registration number and location.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = CheckParkingSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            time = timezone.now()
            registration_number = Parking.normalize_reg_num(
                request.data.get("registration_number"))
            location = request.data.get("location")
            longitude = location.get("longitude")
            latitude = location.get("latitude")

            zone = parking_zone_by_location(longitude, latitude)
            area = permit_area_by_location(longitude, latitude)
            if not zone and not area:
                raise UnknownLocationException()

            if zone:
                is_valid = (
                    Parking.objects.filter(zone__lte=zone.number)
                    .registration_number_like(registration_number)
                    .valid_at(time)
                    .exists()
                )
                if is_valid:
                    end_time = (
                        Parking.objects.filter(zone__lte=zone.number)
                        .registration_number_like(registration_number)
                        .valid_at(time)
                        .order_by("-time_end")
                        .first()
                        .time_end
                    )
                    return Response({"status": "valid", "end_time": end_time})

            if area:
                is_valid = (
                    Permit.objects.active()
                    .by_time(time)
                    .by_subject(registration_number)
                    .by_area(area.identifier)
                    .exists()
                )
                if is_valid:
                    permits = (
                        Permit.objects.active()
                        .by_time(time)
                        .by_subject(registration_number)
                        .by_area(area.identifier)
                    )
                    end_time = (
                        PermitCacheItem.objects.filter(
                            permit__in=permits,
                            registration_number=registration_number,
                            area_identifier=area.identifier,
                        )
                        .order_by("-end_time")
                        .first()
                        .end_time
                    )
                    return Response({"status": "valid", "end_time": end_time})

            return Response({"status": "invalid"})
