import json
from datetime import datetime

import pytest
from django.core.urlresolvers import reverse

from parkings.models import Parking

from ..utils import ALL_METHODS, check_list_endpoint_base_fields, check_method_status_codes, get, get_ids_from_results

list_url = reverse('internal:v1:parking-list')


def get_detail_url(obj):
    return reverse('internal:v1:parking-detail', kwargs={'pk': obj.pk})


def check_parking_data_keys(parking_data):
    assert set(parking_data.keys()) == {
        'id', 'created_at', 'modified_at', 'parking_area',
        'location', 'operator', 'registration_number',
        'time_start', 'time_end', 'zone', 'status',
    }


def check_parking_data_matches_parking_object(parking_data, parking_obj):
    """
    Check that a parking data dict and an actual Parking object match.
    """

    # string and integer valued fields should match 1:1
    for field in {'registration_number', 'zone'}:
        assert parking_data[field] == getattr(parking_obj, field)

    assert parking_data['id'] == str(parking_obj.id)
    assert parking_data['created_at'] == parking_obj.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    assert parking_data['modified_at'] == parking_obj.modified_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    assert parking_data['time_start'] == parking_obj.time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['time_end'] == parking_obj.time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['operator'] == str(parking_obj.operator_id)
    assert parking_data['location'] == json.loads(parking_obj.location.geojson)


def test_other_than_staff_cannot_do_anything(unauthenticated_api_client, operator_api_client, parking):
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(unauthenticated_api_client, urls, ALL_METHODS, 401)
    check_method_status_codes(operator_api_client, urls, ALL_METHODS, 403, error_code='permission_denied')


def test_disallowed_methods(staff_api_client, parking):
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(staff_api_client, urls, disallowed_methods, 405)


def test_get_list_check_data(staff_api_client, parking):
    data = get(staff_api_client, list_url)
    assert len(data['results']) == 1
    parking_data = data['results'][0]
    check_parking_data_keys(parking_data)
    check_parking_data_matches_parking_object(data['results'][0], parking)


def test_get_detail_check_data(staff_api_client, parking):
    parking_data = get(staff_api_client, get_detail_url(parking))
    check_parking_data_keys(parking_data)
    check_parking_data_matches_parking_object(parking_data, parking)


def test_list_endpoint_base_fields(staff_api_client):
    parking_data = get(staff_api_client, list_url)
    check_list_endpoint_base_fields(parking_data)


def test_is_valid_field(staff_api_client, past_parking, current_parking, future_parking):
    parking_data = get(staff_api_client, get_detail_url(past_parking))
    assert parking_data['status'] == Parking.NOT_VALID

    parking_data = get(staff_api_client, get_detail_url(current_parking))
    assert parking_data['status'] == Parking.VALID

    parking_data = get(staff_api_client, get_detail_url(future_parking))
    assert parking_data['status'] == Parking.NOT_VALID


def test_is_valid_filter(staff_api_client, past_parking, current_parking, future_parking):
    results = get(staff_api_client, list_url + '?status=valid')['results']
    assert get_ids_from_results(results) == {current_parking.id}

    results = get(staff_api_client, list_url + '?status=not_valid')['results']
    assert get_ids_from_results(results) == {past_parking.id, future_parking.id}


def test_registration_number_filter(operator, staff_api_client, parking_factory):
    parking_1 = parking_factory(registration_number='ABC-123', operator=operator)
    parking_2 = parking_factory(registration_number='ZYX-987', operator=operator)
    parking_3 = parking_factory(registration_number='ZYX-987', operator=operator)

    results = get(staff_api_client, list_url + '?registration_number=ABC-123')['results']
    assert get_ids_from_results(results) == {parking_1.id}

    results = get(staff_api_client, list_url + '?registration_number=ZYX-987')['results']
    assert get_ids_from_results(results) == {parking_2.id, parking_3.id}

    results = get(staff_api_client, list_url + '?registration_number=LOL-777')['results']
    assert len(results) == 0


@pytest.mark.parametrize('filtering, expected_parking_index', [
    ('time_start_lte=2017-01-01', 0),
    ('time_start_gte=2017-01-01', 1),
    ('time_end_lte=2019-01-01', 0),
    ('time_end_gte=2019-01-01', 1),
    ('time_start_gte=2015-01-01&time_end_lte=2019-01-01', 0),
])
def test_time_filters(operator, staff_api_client, parking_factory, filtering, expected_parking_index):
    parkings = [
        parking_factory(time_start=datetime(2016, 1, 1), time_end=datetime(2018, 1, 1), operator=operator),
        parking_factory(time_start=datetime(2018, 1, 1), time_end=datetime(2020, 1, 1), operator=operator)
    ]
    expected_id = {parkings[expected_parking_index].id}

    results = get(staff_api_client, list_url + '?' + filtering)['results']
    assert get_ids_from_results(results) == expected_id
