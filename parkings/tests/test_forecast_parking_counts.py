import datetime
from random import Random

import pytest
from django.conf import settings
from django.utils.timezone import utc

from parkings.forecasts.forecast_parking_counts import (
    forecast_parking_area_parking_counts, forecast_region_parking_counts)
from parkings.models import ParkingCount


@pytest.mark.django_db
def test_train_parking_area_model_with_no_parking_counts(
    parking_area_factory, parking_count=100
):
    with pytest.raises(Exception) as e:
        forecast_parking_area_parking_counts()
    assert "No cached ParkingCounts found." in str(e)


@pytest.mark.django_db
def test_train_region_model_with_no_parking_counts(
    parking_area_factory, parking_count=100
):
    with pytest.raises(Exception) as e:
        forecast_region_parking_counts()
    assert "No cached ParkingCounts found." in str(e)


@pytest.mark.django_db
def test_forecast_parking_area(parking_area_factory, parking_count=settings.FORECAST_PERIOD + 100):
    start_time = datetime.datetime(2018, 1, 1, tzinfo=utc)
    parking_area = parking_area_factory()
    random = Random()
    ParkingCount.objects.bulk_create(
        (
            ParkingCount(
                number=random.randint(0, 500),
                parking_area_id=parking_area.id,
                time=start_time + datetime.timedelta(hours=i),
            )
            for i in range(parking_count)
        )
    )
    final_datetime = ParkingCount.objects.latest("time").time

    forecast_parking_area_parking_counts()

    forecast_period_start = final_datetime + datetime.timedelta(hours=1)
    forecast_period_end = final_datetime + datetime.timedelta(
        hours=settings.FORECAST_PERIOD
    )
    after_forecast_period = final_datetime + datetime.timedelta(
        hours=settings.FORECAST_PERIOD + 1
    )
    assert ParkingCount.objects.filter(
        parking_area__isnull=False, is_forecast=True, time=forecast_period_start
    ).exists()
    assert ParkingCount.objects.filter(
        parking_area__isnull=False, is_forecast=True, time=forecast_period_end
    ).exists()
    assert not ParkingCount.objects.filter(
        parking_area__isnull=False, is_forecast=True, time=after_forecast_period
    ).exists()


@pytest.mark.django_db
def test_forecast_region(region_factory, parking_count=settings.FORECAST_PERIOD + 100):
    start_time = datetime.datetime(2018, 1, 1, tzinfo=utc)
    region = region_factory()
    random = Random()
    ParkingCount.objects.bulk_create(
        (
            ParkingCount(
                number=random.randint(0, 500),
                region_id=region.id,
                time=start_time + datetime.timedelta(hours=i),
            )
            for i in range(parking_count)
        )
    )
    final_datetime = ParkingCount.objects.latest("time").time

    forecast_region_parking_counts()

    forecast_period_start = final_datetime + datetime.timedelta(hours=1)
    forecast_period_end = final_datetime + datetime.timedelta(
        hours=settings.FORECAST_PERIOD
    )
    after_forecast_period = final_datetime + datetime.timedelta(
        hours=settings.FORECAST_PERIOD + 1
    )
    assert ParkingCount.objects.filter(
        region__isnull=False, is_forecast=True, time=forecast_period_start
    ).exists()
    assert ParkingCount.objects.filter(
        region__isnull=False, is_forecast=True, time=forecast_period_end
    ).exists()
    assert not ParkingCount.objects.filter(
        region__isnull=False, is_forecast=True, time=after_forecast_period
    ).exists()


@pytest.mark.django_db
def test_forecast_2_parking_areas(parking_area_factory, parking_count=settings.FORECAST_PERIOD + 100):
    start_time = datetime.datetime(2018, 1, 1, tzinfo=utc)
    random = Random()
    parking_area = parking_area_factory(origin_id="1234")
    ParkingCount.objects.bulk_create(
        (
            ParkingCount(
                number=random.randint(0, 500),
                parking_area_id=parking_area.id,
                time=start_time + datetime.timedelta(hours=i),
            )
            for i in range(parking_count)
        )
    )
    parking_area2 = parking_area_factory(origin_id="4321")
    ParkingCount.objects.bulk_create(
        (
            ParkingCount(
                number=random.randint(0, 500),
                parking_area_id=parking_area2.id,
                time=start_time + datetime.timedelta(hours=i),
            )
            for i in range(parking_count)
        )
    )
    final_datetime = ParkingCount.objects.latest("time").time

    forecast_parking_area_parking_counts()

    forecast_period_end = final_datetime + datetime.timedelta(
        hours=settings.FORECAST_PERIOD
    )
    assert ParkingCount.objects.filter(
        parking_area=parking_area, is_forecast=True, time=forecast_period_end
    ).exists()
    assert ParkingCount.objects.filter(
        parking_area=parking_area2, is_forecast=True, time=forecast_period_end
    ).exists()


@pytest.mark.django_db
def test_forecast_2_regions(region_factory, parking_count=settings.FORECAST_PERIOD + 100):
    start_time = datetime.datetime(2018, 1, 1, tzinfo=utc)
    random = Random()

    region = region_factory(name="test1")
    ParkingCount.objects.bulk_create(
        (
            ParkingCount(
                number=random.randint(0, 500),
                region_id=region.id,
                time=start_time + datetime.timedelta(hours=i),
            )
            for i in range(parking_count)
        )
    )
    region2 = region_factory(name="test2")
    ParkingCount.objects.bulk_create(
        (
            ParkingCount(
                number=random.randint(0, 500),
                region_id=region2.id,
                time=start_time + datetime.timedelta(hours=i),
            )
            for i in range(parking_count)
        )
    )
    final_datetime = ParkingCount.objects.latest("time").time

    forecast_region_parking_counts()

    forecast_period_end = final_datetime + datetime.timedelta(
        hours=settings.FORECAST_PERIOD
    )
    assert ParkingCount.objects.filter(
        region=region, is_forecast=True, time=forecast_period_end
    ).exists()
    assert ParkingCount.objects.filter(
        region=region2, is_forecast=True, time=forecast_period_end
    ).exists()
