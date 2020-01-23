import datetime

import pytest
from django.utils.timezone import now

from parkings.models import ParkingArea, ParkingCount


def test_str():
    assert str(ParkingArea(origin_id='TEST_ID')) == 'Parking Area TEST_ID'


@pytest.mark.django_db
def test_estimated_capacity(parking_area):
    parking_area.capacity_estimate = 123
    assert parking_area.estimated_capacity == 123
    parking_area.capacity_estimate = None
    by_area = parking_area.estimate_capacity_by_area()
    assert parking_area.estimated_capacity == by_area


@pytest.mark.django_db
def test_estimate_capacity_by_area(parking_area):
    assert parking_area.estimate_capacity_by_area() == int(
        round(parking_area.geom.area * 0.07328))


@pytest.mark.django_db
def test_future_parking_count(parking_area_factory):
    time_future = now() + datetime.timedelta(hours=1)
    time = datetime.datetime(
        time_future.year,
        time_future.month,
        time_future.day,
        time_future.hour,
        tzinfo=time_future.tzinfo,
    )

    region = parking_area_factory()
    ParkingCount.objects.create(
        is_forecast=True, number=10, parking_area=region, time=time
    )
    region_q = ParkingArea.objects.with_parking_count(at_time=time)
    assert region_q.first().parking_count == 10
