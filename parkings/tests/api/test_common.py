from datetime import datetime

import pytest
from django.core.urlresolvers import reverse

from parkings.models import Parking

from .utils import check_list_endpoint_base_fields, get, get_ids_from_results


@pytest.fixture(params=['operator', 'internal'])
def api_specific_values(request, operator_api_client, staff_api_client):
    """
    Returns API specific stuff in a tuple: (api_client, list_url, get_detail_url())
    """
    if request.param == 'operator':
        return (
            operator_api_client,
            reverse('operator:v1:parking-list'),
            lambda obj: reverse('operator:v1:parking-detail', kwargs={'pk': obj.pk}),
        )
    elif request.param == 'internal':
        return (
            staff_api_client,
            reverse('internal:v1:parking-list'),
            lambda obj: reverse('internal:v1:parking-detail', kwargs={'pk': obj.pk}),
        )


def test_list_endpoint_base_fields(api_specific_values):
    (api_client, list_url, get_detail_url) = api_specific_values

    parking_data = get(api_client, list_url)
    check_list_endpoint_base_fields(parking_data)


def test_is_valid_field(api_specific_values, past_parking, current_parking, future_parking):
    (api_client, list_url, get_detail_url) = api_specific_values

    parking_data = get(api_client, get_detail_url(past_parking))
    assert parking_data['status'] == Parking.NOT_VALID

    parking_data = get(api_client, get_detail_url(current_parking))
    assert parking_data['status'] == Parking.VALID

    parking_data = get(api_client, get_detail_url(future_parking))
    assert parking_data['status'] == Parking.NOT_VALID


def test_is_valid_filter(api_specific_values, past_parking, current_parking, future_parking):
    (api_client, list_url, get_detail_url) = api_specific_values

    results = get(api_client, list_url + '?status=valid')['results']
    assert get_ids_from_results(results) == {current_parking.id}

    results = get(api_client, list_url + '?status=not_valid')['results']
    assert get_ids_from_results(results) == {past_parking.id, future_parking.id}


def test_registration_number_filter(api_specific_values, operator, parking_factory):
    (api_client, list_url, get_detail_url) = api_specific_values

    parking_1 = parking_factory(registration_number='ABC-123', operator=operator)
    parking_2 = parking_factory(registration_number='ZYX-987', operator=operator)
    parking_3 = parking_factory(registration_number='ZYX-987', operator=operator)

    results = get(api_client, list_url + '?registration_number=ABC-123')['results']
    assert get_ids_from_results(results) == {parking_1.id}

    results = get(api_client, list_url + '?registration_number=ZYX-987')['results']
    assert get_ids_from_results(results) == {parking_2.id, parking_3.id}

    results = get(api_client, list_url + '?registration_number=LOL-777')['results']
    assert len(results) == 0


@pytest.mark.parametrize('filtering, expected_parking_index', [
    ('time_start_lte=2017-01-01', 0),
    ('time_start_gte=2017-01-01', 1),
    ('time_end_lte=2019-01-01', 0),
    ('time_end_gte=2019-01-01', 1),
    ('time_start_gte=2015-01-01&time_end_lte=2019-01-01', 0),
])
def test_time_filters(api_specific_values, operator, parking_factory, filtering, expected_parking_index):
    (api_client, list_url, get_detail_url) = api_specific_values

    parkings = [
        parking_factory(time_start=datetime(2016, 1, 1), time_end=datetime(2018, 1, 1), operator=operator),
        parking_factory(time_start=datetime(2018, 1, 1), time_end=datetime(2020, 1, 1), operator=operator)
    ]
    expected_id = {parkings[expected_parking_index].id}

    results = get(api_client, list_url + '?' + filtering)['results']
    assert get_ids_from_results(results) == expected_id
