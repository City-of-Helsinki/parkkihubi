import datetime

from django.utils import timezone

from parkings.models import Parking, ParkingArea, ParkingCount, Region


def check_if_parkings_exist():
    if not Parking.objects.exists():
        raise Exception("No Parking objects found.")


def cache_parking_counts_by_region():
    check_if_parkings_exist()
    parkings_start_instance = (
        ParkingCount.objects.filter(region__isnull=False, is_forecast=False)
        .order_by("time")
        .last()
    )
    if parkings_start_instance:
        parkings_start = parkings_start_instance.time
    else:
        first_parking = Parking.objects.all().order_by("time_start").first()
        parkings_start = min(first_parking.time_start, timezone.now())

    last_parking = Parking.objects.order_by("-time_start").first()
    parkings_end = min(last_parking.time_start, timezone.now())

    hour = parkings_start.replace(minute=0, second=0, microsecond=0)

    while hour <= parkings_end:
        regions = (
            Region.objects.all()
            .with_parking_count(hour)
            .values("id", "parking_count")
        )
        ParkingCount.objects.bulk_create(
            (
                ParkingCount(
                    number=region["parking_count"],
                    region_id=region["id"],
                    time=hour,
                )
                for region in regions
            ),
            ignore_conflicts=True,
        )
        hour = hour + datetime.timedelta(hours=1)


def cache_parking_counts_by_parking_area():
    check_if_parkings_exist()
    parkings_start_instance = (
        ParkingCount.objects.filter(parking_area__isnull=False, is_forecast=False)
        .order_by("time")
        .last()
    )
    if parkings_start_instance:
        parkings_start = parkings_start_instance.time
    else:
        first_parking = Parking.objects.all().order_by("time_start").first()
        parkings_start = min(first_parking.time_start, timezone.now())

    last_parking = Parking.objects.order_by("-time_start").first()
    parkings_end = min(last_parking.time_start, timezone.now())

    hour = parkings_start.replace(minute=0, second=0, microsecond=0)

    while hour <= parkings_end:
        parking_areas = (
            ParkingArea.objects.all()
            .with_parking_count(hour)
            .values("id", "parking_count")
        )
        ParkingCount.objects.bulk_create(
            (
                ParkingCount(
                    number=parking_area["parking_count"],
                    parking_area_id=parking_area["id"],
                    time=hour,
                )
                for parking_area in parking_areas
            ),
            ignore_conflicts=True,
        )
        hour = hour + datetime.timedelta(hours=1)
