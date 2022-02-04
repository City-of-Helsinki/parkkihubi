import csv
import datetime

from django.urls import reverse
from django.utils.timezone import utc
from rest_framework import status
from six import StringIO

from parkings.factories import ParkingCheckFactory
from parkings.factories.parking import create_payment_zone

LOCATION = 0
TERMINAL_NUMBER = 1
TIME_START = 2
TIME_END = 3
CREATED_AT = 4
MODIFIED_AT = 5
OPERATOR = 6
ZONE = 7

export_url = reverse('monitoring:v1:export-download')


def test_export_filtering_no_data_if_starts_before_range_and_ends_before_range(monitoring_api_client, parking_factory):
    start = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(time_start=start, time_end=end)
    data = {
        "time_start": "05.07.2018 13.45",
        "time_end": "06.07.2018 15.00",
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None

    for row in reader:
        parking_row = row

    assert parking_row is None


def test_export_filtering_yes_data_if_starts_before_range_and_ends_in_range(monitoring_api_client, parking_factory):
    start = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(time_start=start, time_end=end)
    data = {
        "time_start": "05.07.2018 13.45",
        "time_end": "06.07.2018 15.15",
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None

    for row in reader:
        parking_row = row

    assert parking_row is not None


def test_export_filtering_yes_data_if_starts_in_range_and_ends_in_range(monitoring_api_client, parking_factory):
    start = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(time_start=start, time_end=end)
    data = {
        "time_start": "06.07.2018 15.45",
        "time_end": "06.07.2018 18.00",
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None

    for row in reader:
        parking_row = row

    assert parking_row is not None


def test_export_filtering_yes_data_if_starts_in_range_and_ends_after_range(monitoring_api_client, parking_factory):
    start = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(time_start=start, time_end=end)
    data = {
        "time_start": "06.07.2018 15.45",
        "time_end": "07.07.2018 18.00",
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None

    for row in reader:
        parking_row = row

    assert parking_row is not None


def test_export_filtering_no_data_if_starts_after_range_and_ends_after_range(monitoring_api_client, parking_factory):
    start = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(time_start=start, time_end=end)
    data = {
        "time_start": "07.07.2018 15.45",
        "time_end": "08.07.2018 18.00",
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None

    for row in reader:
        parking_row = row

    assert parking_row is None


def test_export_filtering_yes_data_if_starts_before_range_and_ends_after_range(monitoring_api_client, parking_factory):
    start = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(time_start=start, time_end=end)
    data = {
        "time_start": "05.07.2018 15.45",
        "time_end": "08.07.2018 18.00",
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None

    for row in reader:
        parking_row = row

    assert parking_row is not None


def test_export_filtering_correct_data_no_parking_check(monitoring_api_client, parking_factory, operator_factory):
    zone1 = create_payment_zone(code=1, name="MV1")
    operator1 = operator_factory(name="op1")
    start1 = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end1 = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(
        time_start=start1,
        time_end=end1,
        operator=operator1,
        zone=zone1
    )

    zone2 = create_payment_zone(code=2, name="MV2")
    operator2 = operator_factory(name="op2")
    start2 = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end2 = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(
        time_start=start2,
        time_end=end2,
        operator=operator2,
        zone=zone2
    )

    data = {
        "time_start": "05.07.2018 15.45",
        "time_end": "08.07.2018 18.00",
        "payment_zones": [zone1.code],
        "operators": [operator1.id],
        "parking_check": False
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None
    row_count = 0

    for row in reader:
        parking_row = row
        row_count += 1

    assert parking_row is not None
    assert parking_row[OPERATOR] == operator1.name
    assert parking_row[ZONE] == zone1.name
    assert row_count == 1


def test_export_filtering_correct_data_with_parking_check(monitoring_api_client, parking_factory, operator_factory):
    zone1 = create_payment_zone(code=1, name="MV1")
    operator1 = operator_factory(name="op1")
    start1 = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end1 = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking_factory(
        time_start=start1,
        time_end=end1,
        operator=operator1,
        zone=zone1
    )

    zone2 = create_payment_zone(code=2, name="MV2")
    operator2 = operator_factory(name="op2")
    start2 = datetime.datetime(2018, 7, 6, 15, 15, tzinfo=utc)
    end2 = datetime.datetime(2018, 7, 6, 18, 45, tzinfo=utc)
    parking2 = parking_factory(
        time_start=start2,
        time_end=end2,
        operator=operator2,
        zone=zone2
    )

    ParkingCheckFactory(found_parking=parking2)

    data = {
        "time_start": "05.07.2018 15.45",
        "time_end": "08.07.2018 18.00",
        "payment_zones": [
            zone1.code,
            zone2.code,
        ],
        "operators": [
            operator1.id,
            operator2.id
        ],
        "parking_check": True
    }

    result = monitoring_api_client.post(export_url, data=data)
    assert result.status_code == status.HTTP_200_OK

    # Data doesn't get rendered by the custom renderer in tests for whatever reason. So render it manually.
    renderer = result.accepted_renderer
    reader = csv.reader(StringIO(renderer.render(result.data)))

    parking_row = None
    row_count = 0

    for row in reader:
        parking_row = row
        row_count += 1

    assert parking_row is not None
    assert parking_row[OPERATOR] == operator2.name
    assert parking_row[ZONE] == zone2.name
    assert row_count == 1
