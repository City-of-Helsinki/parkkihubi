from datetime import datetime

import pytest
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import utc
from rest_framework.status import (
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)

from parkings.factories import EnforcerFactory
from parkings.factories.parking import create_payment_zone

from ..utils import (
    ALL_METHODS, check_list_endpoint_base_fields, check_method_status_codes,
    check_response_objects, get, get_ids_from_results)

list_url = reverse('enforcement:v1:valid_parking-list')


def list_url_for(reg_num=None, time=None):
    assert reg_num or time
    if not time:
        return '{url}?reg_num={reg_num}'.format(url=list_url, reg_num=reg_num)
    elif not reg_num:
        return '{url}?time={time}'.format(url=list_url, time=time)
    else:
        return '{url}?reg_num={reg_num}&time={time}'.format(url=list_url, reg_num=reg_num, time=iso8601(time))


list_url_for_abc = list_url_for('ABC-123')


def get_url(kind, parking):
    if kind == 'list':
        return list_url
    elif kind == 'list_by_reg_num':
        return list_url_for(reg_num=parking.registration_number)
    elif kind == 'list_by_time':
        return list_url_for(time=datetime.now())
    elif kind == 'list_by_reg_num_and_time':
        return list_url_for(reg_num=parking.registration_number, time=datetime.now())
    else:
        assert kind == 'detail'
        return reverse('enforcement:v1:valid_parking-detail',
                       kwargs={'pk': parking.pk})


def get_parking_object(parking_type, parking, disc_parking):
    if parking_type == 'paid':
        return parking
    else:
        assert parking_type == 'disc_parking'
        return disc_parking


ALL_URL_KINDS = ['list', 'list_by_reg_num', 'list_by_time', 'list_by_reg_num_and_time', 'detail']
ALL_PARKING_KINDS = ['paid', 'disc_parking']


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_permission_checks(api_client, operator_api_client, parking, url_kind):
    url = get_url(url_kind, parking)
    check_method_status_codes(
        api_client, [url], ALL_METHODS, HTTP_401_UNAUTHORIZED)
    check_method_status_codes(
        operator_api_client, [url], ALL_METHODS, HTTP_403_FORBIDDEN,
        error_code='permission_denied')


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_disallowed_methods(enforcer_api_client, parking, url_kind):
    url = get_url(url_kind, parking)
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    check_method_status_codes(
        enforcer_api_client, [url], disallowed_methods, 405)


def test_reg_num_or_time_is_required(enforcer_api_client, parking):
    response = enforcer_api_client.get(list_url)
    error_message = 'Either time or registration number required.'
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert error_message in response.data


def test_list_endpoint_base_fields(enforcer_api_client):
    parking_data = get(enforcer_api_client, list_url_for_abc)
    check_list_endpoint_base_fields(parking_data)


@pytest.mark.parametrize('parking_type', ALL_PARKING_KINDS)
def test_list_endpoint_data(enforcer_api_client, parking_type, parking, disc_parking, enforcer):
    parking_object = get_parking_object(parking_type, parking, disc_parking)
    parking_object.domain = enforcer.enforced_domain
    parking_object.save()

    data = get(enforcer_api_client, get_url('list_by_reg_num', parking_object))
    assert len(data['results']) == 1
    parking_data = data['results'][0]
    check_parking_data_keys(parking_data)
    check_parking_data_matches_parking_object(data['results'][0], parking_object)


def check_parking_data_keys(parking_data):
    parking_data_keys = {
        'id', 'created_at', 'modified_at',
        'registration_number',
        'time_start', 'time_end', 'zone',
        'operator', 'operator_name',
    }

    if parking_data.get('is_disc_parking'):
        parking_data_keys.add('is_disc_parking')

    assert set(parking_data.keys()) == parking_data_keys


def check_parking_data_matches_parking_object(parking_data, parking_obj):
    """
    Check that a parking data dict and an actual Parking object match.
    """
    assert parking_data['registration_number'] == getattr(parking_obj, 'registration_number')
    assert parking_data['zone'] == (parking_obj.zone.casted_code
                                    if parking_obj.zone else None)
    assert parking_data['id'] == str(parking_obj.id)  # UUID -> str
    assert parking_data['operator'] == str(parking_obj.operator.id)
    assert parking_data['created_at'] == iso8601_us(parking_obj.created_at)
    assert parking_data['modified_at'] == iso8601_us(parking_obj.modified_at)
    assert parking_data['time_start'] == iso8601(parking_obj.time_start)
    assert parking_data['time_end'] == iso8601(parking_obj.time_end)
    assert parking_data['operator_name'] == str(parking_obj.operator.name)
    assert parking_data.get('is_disc_parking', False) == parking_obj.is_disc_parking


def iso8601(dt):
    if not dt:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def iso8601_us(dt):
    if not dt:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def test_registration_number_filter(operator, enforcer_api_client, parking_factory, enforcer):
    p1 = parking_factory(registration_number='ABC-123', operator=operator, domain=enforcer.enforced_domain)
    p2 = parking_factory(registration_number='ZYX-987', operator=operator, domain=enforcer.enforced_domain)
    p3 = parking_factory(registration_number='ZYX-987', operator=operator, domain=enforcer.enforced_domain)
    p4 = parking_factory(registration_number='Zyx987 ', operator=operator, domain=enforcer.enforced_domain)

    results = get(enforcer_api_client, list_url_for('ABC-123'))['results']
    assert get_ids_from_results(results) == {p1.id}

    results = get(enforcer_api_client, list_url_for('ZYX-987'))['results']
    assert get_ids_from_results(results) == {p2.id, p3.id, p4.id}

    results = get(enforcer_api_client, list_url_for('zyx987'))['results']
    assert get_ids_from_results(results) == {p2.id, p3.id, p4.id}

    results = get(enforcer_api_client, list_url_for('LOL-777'))['results']
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
def test_time_filtering(operator, enforcer_api_client, parking_factory, name, enforcer):
    p1 = parking_factory(
        registration_number='ABC-123',
        time_start=datetime(2012, 1, 1, 12, 0, 0, tzinfo=utc),
        time_end=datetime(2014, 1, 1, 12, 0, 0, tzinfo=utc),
        operator=operator,
        domain=enforcer.enforced_domain)
    p2 = parking_factory(
        registration_number='ABC-123',
        time_start=datetime(2014, 1, 1, 12, 0, 0, tzinfo=utc),
        time_end=datetime(2016, 1, 1, 12, 0, 0, tzinfo=utc),
        operator=operator,
        domain=enforcer.enforced_domain)
    p3 = parking_factory(registration_number='ABC-123', domain=enforcer.enforced_domain)

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
    response = get(enforcer_api_client, list_url_for_abc + filtering)
    check_response_objects(response, expected_parkings)


@pytest.mark.parametrize('parking_type', ALL_PARKING_KINDS)
@override_settings(PARKKIHUBI_NONE_END_TIME_REPLACEMENT='2030-12-31T23:59:59Z')
def test_null_time_end_is_replaced_correctly(parking_type, enforcer_api_client, parking, disc_parking, enforcer):
    parking_object = get_parking_object(parking_type, parking, disc_parking)
    parking_object.time_end = None
    parking_object.domain = enforcer.enforced_domain
    parking_object.save()
    data = get(enforcer_api_client, get_url('list_by_reg_num', parking_object))
    parking_data = data['results'][0]
    check_parking_data_keys(parking_data)

    assert parking_data['time_end'] == '2030-12-31T23:59:59Z'


def test_enforcer_can_view_only_parkings_from_domain_they_enforce(
    enforcer_api_client, parking_factory, staff_user, enforcer
):
    visible_parking = parking_factory(registration_number='ABC-123', domain=enforcer.enforced_domain)
    parking_factory(registration_number='ABC-123')  # Parking belonging to different domain

    response = get(enforcer_api_client, list_url_for('ABC-123'))

    assert response['count'] == 1
    assert response['results'][0]['id'] == str(visible_parking.id)


def test_endpoint_can_return_zone_as_string_or_integer(
    enforcer_api_client, parking, enforcer
):
    parking_object = parking
    parking_object.domain = enforcer.enforced_domain
    parking_object.save()

    parking_object.zone.code = '5'
    parking_object.zone.save()
    data = get(enforcer_api_client, get_url('list_by_reg_num', parking_object))
    parking_data = data['results'][0]
    assert parking_data['zone'] == 5

    parking_object.zone.code = '5A'
    parking_object.zone.save()
    data = get(enforcer_api_client, get_url('list_by_reg_num', parking_object))
    parking_data = data['results'][0]
    assert parking_data['zone'] == '5A'


def test_endpoint_returns_parkings_with_same_zone_code_in_correct_domain(
        enforcer_api_client, staff_api_client, operator, enforcer, parking_factory, staff_user
):
    zone_1 = create_payment_zone(code='Z', domain=enforcer.enforced_domain)
    EnforcerFactory(user=staff_user)
    domain = staff_user.enforcer.enforced_domain
    zone_2 = create_payment_zone(code='Z', domain=domain)

    assert zone_1.domain.code != zone_2.domain.code

    parking_1 = parking_factory(registration_number="ABC-123", operator=operator, zone=zone_1)
    parking_1.domain = zone_1.domain
    parking_1.save()

    parking_2 = parking_factory(registration_number="ABC-123", operator=operator, zone=zone_2)
    parking_2.domain = zone_2.domain
    parking_2.save()

    data_1 = get(enforcer_api_client, get_url('list_by_reg_num', parking_1))
    assert len(data_1['results']) == 1
    parking_data_1 = data_1['results'][0]
    assert parking_data_1['id'] == str(parking_1.id)
    assert parking_data_1['zone'] == 'Z'

    data_2 = get(staff_api_client, get_url('list_by_reg_num', parking_2))
    assert len(data_2['results']) == 1
    parking_data_2 = data_2['results'][0]
    assert parking_data_2['id'] == str(parking_2.id)
    assert parking_data_2['zone'] == 'Z'
