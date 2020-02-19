import pytest
from django.core.management import call_command
from django.utils.timezone import now

from parkings.models import ParkingCount

from ..management.commands import (
    cache_parking_counts_by_parking_area, cache_parking_counts_by_region)


@pytest.mark.django_db
def test_cache_parking_counts_by_parking_area_without_parkings():
    with pytest.raises(Exception) as e:
        call_command(cache_parking_counts_by_parking_area.Command())
    assert "No Parking objects found." in str(e)


@pytest.mark.django_db
def test_cache_parking_counts_by_region_without_parkings():
    with pytest.raises(Exception) as e:
        call_command(cache_parking_counts_by_region.Command())
    assert "No Parking objects found." in str(e)


@pytest.mark.django_db
def test_cache_parking_counts_by_parking_area(
    parking_area_factory, parking_factory, parking_count=100
):
    time_now = now().replace(minute=0, second=0, microsecond=0)

    parking_area = parking_area_factory()
    parking_factory.create_batch(
        parking_count, time_start=time_now, location=parking_area.geom.centroid
    )

    call_command(cache_parking_counts_by_parking_area.Command())

    pc = ParkingCount.objects.get(
        parking_area=parking_area,
        time=time_now,
    )
    assert pc.number == parking_count


@pytest.mark.django_db
def test_cache_parking_counts_by_region(
    region_factory, parking_factory, parking_count=100
):
    time_now = now().replace(minute=0, second=0, microsecond=0)

    region = region_factory()
    parking_factory.create_batch(
        parking_count, time_start=time_now, location=region.geom.centroid
    )

    call_command(cache_parking_counts_by_region.Command())

    pc = ParkingCount.objects.get(
        region=region,
        time=time_now,
    )
    assert pc.number == parking_count
