import json
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
from freezegun import freeze_time

from parkings.models import Parking

from ..utils import check_list_endpoint_base_fields, check_method_status_codes, check_response_objects, get

list_url = reverse('public:v1:parking-list')


def get_detail_url(obj):
    return reverse('public:v1:parking-detail', kwargs={'pk': obj.pk})


def check_parking_data_keys_public(parking_data):
    assert set(parking_data.keys()) == {'id', 'parking_area', 'location', 'time_start', 'time_end', 'zone'}


def check_parking_data_matches_parking_object_public(parking_data, parking_obj):
    assert parking_data['id'] == str(parking_obj.id)
    assert parking_data['time_start'] == parking_obj.time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['time_end'] == parking_obj.time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['location'] == json.loads(parking_obj.location.geojson)
    assert parking_data['zone'] == parking_obj.zone


@pytest.fixture
def parking_in_past(parking_factory):
    return parking_factory(
        time_start=datetime(2016, 2, 18, 8, 0, 0, tzinfo=utc),
        time_end=datetime(2016, 2, 18, 10, 0, 0, tzinfo=utc),
    )


def test_list_endpoint_base_fields(api_client):
    parking_data = get(api_client, list_url)
    check_list_endpoint_base_fields(parking_data)


def test_disallowed_methods(api_client, parking_in_past):
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    urls = (list_url, get_detail_url(parking_in_past))
    check_method_status_codes(api_client, urls, disallowed_methods, 405)


def test_get_list_check_data(api_client, parking_in_past):
    data = get(api_client, list_url)
    assert len(data['results']) == 1

    parking_data = data['results'][0]
    check_parking_data_keys_public(parking_data)
    check_parking_data_matches_parking_object_public(parking_data, parking_in_past)


def test_get_detail_check_data(api_client, parking_in_past):
    parking_data = get(api_client, get_detail_url(parking_in_past))
    check_parking_data_keys_public(parking_data)
    check_parking_data_matches_parking_object_public(parking_data, parking_in_past)


def test_new_parking_hidden_period(api_client, parking_factory):
    time_hidden = getattr(settings, 'PARKKIHUBI_TIME_PARKINGS_HIDDEN', timedelta(days=7))
    test_datetime = datetime(2010, 1, 1, 12, 00, tzinfo=utc)
    boundary_datetime = test_datetime - time_hidden

    parking_that_should_be_visible_1 = parking_factory(
        time_start=boundary_datetime - timedelta(seconds=2),
        time_end=boundary_datetime - timedelta(seconds=1),
    )

    # parkings that should be hidden
    parking_factory(
        time_start=boundary_datetime - timedelta(seconds=1),
        time_end=boundary_datetime + timedelta(seconds=1),
    )
    parking_factory(
        time_start=test_datetime - timedelta(seconds=1),
        time_end=test_datetime + timedelta(seconds=1),
    )
    parking_factory(
        time_start=test_datetime + timedelta(seconds=1),
        time_end=test_datetime + timedelta(seconds=2),
    )

    parking_that_should_be_visible_2 = parking_factory(
        time_start=boundary_datetime - timedelta(days=401),
        time_end=boundary_datetime - timedelta(days=400),
    )

    with freeze_time(test_datetime):
        response = get(api_client, list_url)

    check_response_objects(response, (parking_that_should_be_visible_1, parking_that_should_be_visible_2))


@pytest.mark.parametrize('filtering, expected_parking_indexes', [
    ('', [0, 1]),
    ('time_start_lte=2014-01-01T12:00:00Z', [0, 1]),
    ('time_start_lte=2014-01-01T11:59:59Z', [0]),
    ('time_end_gte=2014-01-01T12:00:00Z', [0, 1]),
    ('time_end_gte=2014-01-01T12:00:01Z', [1]),
    ('time_start_gte=2012-01-01T12:00:00Z', [0, 1]),
    ('time_start_gte=2012-01-01T12:00:01Z', [1]),
    ('time_end_lte=2016-01-01T12:00:00Z', [0, 1]),
    ('time_end_lte=2016-01-01T11:59:59Z', [0]),
    ('time_start_gte=2011-01-01T12:00:00Z&time_end_lte=2015-01-01T12:00:00Z', [0]),
    ('time_start_gte=2013-01-01T12:00:00Z&time_end_lte=2015-01-01T12:00:00Z', []),
])
def test_time_filters(operator, api_client, parking_factory, filtering, expected_parking_indexes):
    parkings = [
        parking_factory(
            time_start=datetime(2012, 1, 1, 12, 0, 0, tzinfo=utc),
            time_end=datetime(2014, 1, 1, 12, 0, 0, tzinfo=utc),
            operator=operator
        ),
        parking_factory(
            time_start=datetime(2014, 1, 1, 12, 0, 0, tzinfo=utc),
            time_end=datetime(2016, 1, 1, 12, 0, 0, tzinfo=utc),
            operator=operator
        )
    ]
    expected_parkings = set(parkings[index] for index in expected_parking_indexes)

    response = get(api_client, list_url + '?' + filtering)
    check_response_objects(response, expected_parkings)


def test_parking_area_filter(api_client, history_parking_factory, parking_area_factory):
    (parking_area_1, parking_area_2, parking_area_3) = parking_area_factory.create_batch(3)

    with patch.object(Parking, 'get_closest_area', return_value=parking_area_1):
        parking_1 = history_parking_factory()
    with patch.object(Parking, 'get_closest_area', return_value=parking_area_2):
        parking_2 = history_parking_factory()
        parking_3 = history_parking_factory()
    with patch.object(Parking, 'get_closest_area', return_value=parking_area_3):
        parking_4 = history_parking_factory()

    data = get(api_client, list_url)
    check_response_objects(data, (parking_1, parking_2, parking_3, parking_4))

    data = get(api_client, list_url + '?parking_area=%s' % str(parking_area_2.id))
    check_response_objects(data, (parking_2, parking_3))

    data = get(api_client, list_url + '?parking_area=%s,%s' % (str(parking_area_1.id), str(parking_area_2.id)))
    check_response_objects(data, (parking_1, parking_2, parking_3))

    data = get(api_client, list_url + '?parking_area=foobar')
    assert not data['results']


def test_zone_filter(api_client, history_parking_factory):
    parking_1 = history_parking_factory(zone=1)
    parking_2 = history_parking_factory(zone=2)
    parking_3 = history_parking_factory(zone=2)
    parking_4 = history_parking_factory(zone=3)

    data = get(api_client, list_url)['results']
    check_response_objects(data, (parking_1, parking_2, parking_3, parking_4))

    data = get(api_client, list_url + '?zone=2')
    check_response_objects(data, (parking_2, parking_3))

    data = get(api_client, list_url + '?zone=1,2')
    check_response_objects(data, (parking_1, parking_2, parking_3))

    data = get(api_client, list_url + '?zone=foobar')
    assert not data['results']


def test_bounding_box_filter(api_client, history_parking_factory):
    parking_1 = history_parking_factory(location=Point(10, 10))
    parking_2 = history_parking_factory(location=Point(20, 20))
    parking_3 = history_parking_factory(location=Point(30, 30))

    data = get(api_client, list_url)
    check_response_objects(data, (parking_1, parking_2, parking_3))

    data = get(api_client, list_url + '?in_bbox=5,5,15,15')
    check_response_objects(data, parking_1)

    data = get(api_client, list_url + '?in_bbox=5,5,25,25')
    check_response_objects(data, (parking_1, parking_2))

    data = get(api_client, list_url + '?in_bbox=80,80,85,85')
    assert not data['results']
