from datetime import datetime

import pytest
from django.urls import reverse
from django.utils.timezone import utc
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)

from ..utils import (
    ALL_METHODS, check_list_endpoint_base_fields, check_method_status_codes,
    check_response_objects, get, get_ids_from_results)

list_url = reverse('enforcement:v1:valid_parking-list')


def list_url_for(reg_num):
    return '{url}?reg_num={reg_num}'.format(url=list_url, reg_num=reg_num)


list_url_for_abc = list_url_for('ABC-123')


def get_url(kind, parking):
    if kind == 'list':
        return list_url
    elif kind == 'list_by_reg_num':
        return list_url_for(parking.registration_number)
    else:
        assert kind == 'detail'
        return reverse('enforcement:v1:valid_parking-detail',
                       kwargs={'pk': parking.pk})


ALL_URL_KINDS = ['list', 'list_by_reg_num', 'detail']


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_permission_checks(api_client, operator_api_client, parking, url_kind):
    url = get_url(url_kind, parking)
    check_method_status_codes(
        api_client, [url], ALL_METHODS, HTTP_401_UNAUTHORIZED)
    check_method_status_codes(
        operator_api_client, [url], ALL_METHODS, HTTP_403_FORBIDDEN,
        error_code='permission_denied')


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_disallowed_methods(staff_api_client, parking, url_kind):
    url = get_url(url_kind, parking)
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    check_method_status_codes(
        staff_api_client, [url], disallowed_methods, 405)


def test_reg_num_is_required(staff_api_client, parking):
    response = staff_api_client.get(list_url)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data == {'reg_num': ['This field is required.']}


def test_list_endpoint_base_fields(staff_api_client):
    parking_data = get(staff_api_client, list_url_for_abc)
    check_list_endpoint_base_fields(parking_data)


def test_list_endpoint_data(staff_api_client, parking):
    data = get(staff_api_client, get_url('list_by_reg_num', parking))
    assert len(data['results']) == 1
    parking_data = data['results'][0]
    check_parking_data_keys(parking_data)
    check_parking_data_matches_parking_object(data['results'][0], parking)


def check_parking_data_keys(parking_data):
    assert set(parking_data.keys()) == {
        'id', 'created_at', 'modified_at',
        'registration_number',
        'time_start', 'time_end', 'zone',
        'operator', 'operator_name',
    }


def check_parking_data_matches_parking_object(parking_data, parking_obj):
    """
    Check that a parking data dict and an actual Parking object match.
    """

    # string and integer valued fields should match 1:1
    for field in {'registration_number', 'zone'}:
        assert parking_data[field] == getattr(parking_obj, field)

    assert parking_data['id'] == str(parking_obj.id)  # UUID -> str
    assert parking_data['operator'] == str(parking_obj.operator.id)
    assert parking_data['created_at'] == iso8601_us(parking_obj.created_at)
    assert parking_data['modified_at'] == iso8601_us(parking_obj.modified_at)
    assert parking_data['time_start'] == iso8601(parking_obj.time_start)
    assert parking_data['time_end'] == iso8601(parking_obj.time_end)
    assert parking_data['operator_name'] == str(parking_obj.operator.name)


def iso8601(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def iso8601_us(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def test_registration_number_filter(operator, staff_api_client, parking_factory):
    p1 = parking_factory(registration_number='ABC-123', operator=operator)
    p2 = parking_factory(registration_number='ZYX-987', operator=operator)
    p3 = parking_factory(registration_number='ZYX-987', operator=operator)
    p4 = parking_factory(registration_number='Zyx987 ', operator=operator)

    results = get(staff_api_client, list_url_for('ABC-123'))['results']
    assert get_ids_from_results(results) == {p1.id}

    results = get(staff_api_client, list_url_for('ZYX-987'))['results']
    assert get_ids_from_results(results) == {p2.id, p3.id, p4.id}

    results = get(staff_api_client, list_url_for('zyx987'))['results']
    assert get_ids_from_results(results) == {p2.id, p3.id, p4.id}

    results = get(staff_api_client, list_url_for('LOL-777'))['results']
    assert not results


@pytest.mark.parametrize('name', [
    'before_all',
    'at_start_of_1st',
    'after_start_of_1st',
    'before_end_of_1st',
    'between_1st_and_2nd',
    'after_start_of_2nd',
    'before_end_of_2nd',
    'at_end_of_2nd',
    'less_than_15min_after_2nd',
    'more_than_15min_after_2nd',
    'less_than_day_after_2nd',
    'more_than_day_after_2nd',
    'now',
])
def test_time_filtering(operator, staff_api_client, parking_factory, name):
    p1 = parking_factory(
        registration_number='ABC-123',
        time_start=datetime(2012, 1, 1, 12, 0, 0, tzinfo=utc),
        time_end=datetime(2014, 1, 1, 12, 0, 0, tzinfo=utc),
        operator=operator)
    p2 = parking_factory(
        registration_number='ABC-123',
        time_start=datetime(2014, 1, 1, 12, 0, 0, tzinfo=utc),
        time_end=datetime(2016, 1, 1, 12, 0, 0, tzinfo=utc),
        operator=operator)
    p3 = parking_factory(registration_number='ABC-123')

    (time, expected_parkings) = {
        'before_all': ('2000-01-01T12:00:00Z', []),
        'at_start_of_1st': ('2012-01-01T12:00:00Z', [p1]),
        'after_start_of_1st': ('2012-01-01T12:00:01Z', [p1]),
        'before_end_of_1st': ('2014-01-01T11:59:59Z', [p1]),
        'between_1st_and_2nd': ('2014-01-01T12:00:00Z', [p1, p2]),
        'after_start_of_2nd': ('2014-01-01T12:00:01Z', [p2]),
        'before_end_of_2nd': ('2016-01-01T11:59:59Z', [p2]),
        'at_end_of_2nd': ('2016-01-01T12:00:00Z', [p2]),
        'less_than_15min_after_2nd': ('2016-01-01T12:14:59Z', [p2]),
        'more_than_15min_after_2nd': ('2016-01-02T12:15:01Z', []),
        'less_than_day_after_2nd': ('2016-01-01T22:00:00Z', []),
        'more_than_day_after_2nd': ('2016-01-02T13:00:00Z', []),
        'now': ('', [p3]),
    }[name]

    filtering = '&time={}'.format(time) if time else ''
    response = get(staff_api_client, list_url_for_abc + filtering)
    check_response_objects(response, expected_parkings)
