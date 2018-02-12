import pytest

from parkings.models import ParkingArea


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
