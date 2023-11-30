import datetime
import json

import pytest
from django.conf import settings
from django.urls import reverse
from freezegun import freeze_time

from parkings.factories.parking import create_payment_zone
from parkings.models import EnforcementDomain, Parking

from ..utils import (
    ALL_METHODS, check_method_status_codes, check_required_fields, delete,
    patch, post, put)

list_url = reverse('operator:v1:parking-list')


def get_detail_url(obj):
    return reverse('operator:v1:parking-detail', kwargs={'pk': obj.pk})


@pytest.fixture
def new_parking_data():
    return {
        'zone': 3,
        'registration_number': 'JLH-247',
        'time_start': '2016-12-10T20:34:38Z',
        'time_end': '2016-12-10T23:33:29Z',
        'location': {'coordinates': [60.16896809536978, 24.942075065834615], 'type': 'Point'},
    }


@pytest.fixture
def updated_parking_data():
    return {
        'zone': 2,
        'registration_number': 'VSM-162',
        'time_start': '2016-12-12T20:34:38Z',
        'time_end': '2016-12-12T23:33:29Z',
        'location': {'coordinates': [60.16899227603715, 24.9482582558314], 'type': 'Point'},
    }


def check_parking_data_matches_parking_object(parking_data, parking_obj):
    """
    Check that a parking data dict and an actual Parking object match.
    """

    # string or integer valued fields should match 1:1
    for field in {'registration_number'}:
        assert parking_data[field] == getattr(parking_obj, field)

    assert parking_data['zone'] == parking_obj.zone.casted_code

    assert parking_data['time_start'] == parking_obj.time_start.strftime('%Y-%m-%dT%H:%M:%SZ')

    obj_time_end = parking_obj.time_end.strftime('%Y-%m-%dT%H:%M:%SZ') if parking_obj.time_end else None
    assert parking_data['time_end'] == obj_time_end
    obj_location = json.loads(parking_obj.location.geojson) if parking_obj.location else None
    assert parking_data['location'] == obj_location


def check_response_parking_data(posted_parking_data, response_parking_data):
    """
    Check that parking data dict in a response has the right fields and matches the posted one.
    """
    expected_keys = {
        'id', 'zone', 'registration_number',
        'terminal_number',
        'time_start', 'time_end',
        'location', 'created_at', 'modified_at',
        'status', 'domain',
    }

    posted_data_keys = set(posted_parking_data)
    returned_data_keys = set(response_parking_data)
    assert returned_data_keys == expected_keys

    # assert common fields equal
    for key in returned_data_keys & posted_data_keys:
        assert response_parking_data[key] == posted_parking_data[key]

    assert 'is_disc_parking' not in set(response_parking_data)


def test_disallowed_methods(operator_api_client, parking):
    list_disallowed_methods = ('get', 'put', 'patch', 'delete')
    check_method_status_codes(operator_api_client, list_url, list_disallowed_methods, 405)

    detail_disallowed_methods = ('get', 'post')
    check_method_status_codes(operator_api_client, get_detail_url(parking), detail_disallowed_methods, 405)


def test_unauthenticated_and_normal_users_cannot_do_anything(api_client, user_api_client, parking):
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(api_client, urls, ALL_METHODS, 401)
    check_method_status_codes(user_api_client, urls, ALL_METHODS, 403, error_code='permission_denied')


def test_parking_required_fields(operator_api_client, parking):
    expected_required_fields = {'registration_number', 'time_start', 'zone'}
    check_required_fields(operator_api_client, list_url, expected_required_fields)
    check_required_fields(operator_api_client, get_detail_url(parking), expected_required_fields, detail_endpoint=True)


def test_post_parking(operator_api_client, operator, new_parking_data):
    create_payment_zone(
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    response_parking_data = post(operator_api_client, list_url, new_parking_data)

    # check data in the response
    check_response_parking_data(new_parking_data, response_parking_data)

    # check the actual object
    new_parking = Parking.objects.get(id=response_parking_data['id'])
    check_parking_data_matches_parking_object(new_parking_data, new_parking)

    # operator should be autopopulated
    assert new_parking.operator == operator
    assert new_parking.domain.code == response_parking_data['domain']


def test_post_parking_optional_fields_omitted(operator_api_client, new_parking_data):
    new_parking_data.pop('time_end')
    new_parking_data.pop('location')

    create_payment_zone(
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    response_parking_data = post(operator_api_client, list_url, new_parking_data)

    new_parking_data['time_end'] = None
    new_parking_data['location'] = None
    check_response_parking_data(new_parking_data, response_parking_data)
    new_parking = Parking.objects.get(id=response_parking_data['id'])
    check_parking_data_matches_parking_object(new_parking_data, new_parking)


def test_post_parking_optional_fields_null(operator_api_client, new_parking_data):
    new_parking_data['time_end'] = None
    new_parking_data['location'] = None

    create_payment_zone(
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())
    response_parking_data = post(operator_api_client, list_url, new_parking_data)

    check_response_parking_data(new_parking_data, response_parking_data)
    new_parking = Parking.objects.get(id=response_parking_data['id'])
    check_parking_data_matches_parking_object(new_parking_data, new_parking)


@pytest.mark.parametrize('mode', ['normal', 'method-override'])
def test_put_parking(mode, operator_api_client, parking, updated_parking_data):
    detail_url = get_detail_url(parking)
    create_payment_zone(code='2', number=2, domain=EnforcementDomain.get_default_domain())

    response_parking_data = put(
        operator_api_client, detail_url, updated_parking_data,
        use_method_override=(mode == 'method-override'),
    )

    # check data in the response
    check_response_parking_data(updated_parking_data, response_parking_data)

    # check the actual object
    parking.refresh_from_db()
    check_parking_data_matches_parking_object(updated_parking_data, parking)


def test_put_parking_optional_fields_omitted(operator_api_client, parking, updated_parking_data):
    detail_url = get_detail_url(parking)
    create_payment_zone(code='2', number=2, domain=EnforcementDomain.get_default_domain())
    updated_parking_data.pop('time_end')
    updated_parking_data.pop('location')

    response_parking_data = put(operator_api_client, detail_url, updated_parking_data)

    updated_parking_data['time_end'] = None
    updated_parking_data['location'] = None
    check_response_parking_data(updated_parking_data, response_parking_data)
    parking.refresh_from_db()
    check_parking_data_matches_parking_object(updated_parking_data, parking)


def test_put_parking_optional_fields_null(operator_api_client, parking, updated_parking_data):
    detail_url = get_detail_url(parking)
    create_payment_zone(code='2', number=2, domain=EnforcementDomain.get_default_domain())
    updated_parking_data['time_end'] = None
    updated_parking_data['location'] = None

    response_parking_data = put(operator_api_client, detail_url, updated_parking_data)

    check_response_parking_data(updated_parking_data, response_parking_data)
    parking.refresh_from_db()
    check_parking_data_matches_parking_object(updated_parking_data, parking)


@pytest.mark.parametrize('mode', ['normal', 'method-override'])
def test_patch_parking(mode, operator_api_client, parking):
    detail_url = get_detail_url(parking)
    new_zone_number = parking.zone.number % 3 + 1
    new_zone = create_payment_zone(
        code=str(new_zone_number),
        number=new_zone_number,
        id=new_zone_number,
        domain=EnforcementDomain.get_default_domain())

    response_parking_data = patch(
        operator_api_client, detail_url, {'zone': new_zone.id},
        use_method_override=(mode == 'method-override'),
    )

    # check data in the response
    check_response_parking_data({'zone': new_zone.id}, response_parking_data)

    # check the actual object
    parking.refresh_from_db()
    assert parking.zone.number == new_zone.number
    assert parking.domain.code == response_parking_data['domain']


@pytest.mark.parametrize('mode', ['normal', 'method-override'])
def test_delete_parking(mode, operator_api_client, parking):
    detail_url = get_detail_url(parking)

    delete(
        operator_api_client,
        detail_url,
        use_method_override=(mode == 'method-override'),
    )

    assert not Parking.objects.filter(id=parking.id).exists()


@pytest.mark.parametrize('method', [
    'FOO', '', '-', 'OPTIONS', 'HEAD', 'POST', 'GET', 'put', 'Put',
])
def test_invalid_method_override(method, operator_api_client, parking):
    url = get_detail_url(parking) + '?method=' + method

    response = operator_api_client.post(url)

    assert response.status_code == 405
    assert response.reason_phrase == 'Method Override Not Allowed'
    assert response.content == b''


def test_operator_cannot_be_set(operator_api_client, operator, operator_2, new_parking_data, updated_parking_data):
    new_parking_data['operator'] = str(operator_2.id)

    create_payment_zone(
        id=new_parking_data['zone'],
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    # POST
    response_parking_data = post(operator_api_client, list_url, new_parking_data)
    new_parking = Parking.objects.get(id=response_parking_data['id'])
    assert new_parking.operator == operator

    create_payment_zone(
        id=updated_parking_data['zone'],
        code=str(updated_parking_data['zone']),
        number=updated_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    # PUT
    detail_url = get_detail_url(new_parking)
    put(operator_api_client, detail_url, updated_parking_data)
    new_parking.refresh_from_db()
    assert new_parking.operator == operator

    # PATCH
    patch(operator_api_client, detail_url, {'operator': str(operator_2.id)})
    new_parking.refresh_from_db()
    assert new_parking.operator == operator


def test_cannot_modify_other_than_own_parkings(operator_2_api_client, parking, new_parking_data):
    detail_url = get_detail_url(parking)
    put(operator_2_api_client, detail_url, new_parking_data, 404)
    patch(operator_2_api_client, detail_url, new_parking_data, 404)
    delete(operator_2_api_client, detail_url, 404)


def test_cannot_modify_parking_after_modify_period(operator_api_client, new_parking_data, updated_parking_data):
    for data in [new_parking_data, updated_parking_data]:
        create_payment_zone(
            id=data['zone'],
            code=str(data['zone']),
            number=data['zone'],
            domain=EnforcementDomain.get_default_domain())

    start_time = datetime.datetime(2010, 1, 1, 12, 00)
    error_message = 'Grace period has passed. Only "time_end" can be updated via PATCH.'
    error_code = 'grace_period_over'

    with freeze_time(start_time):
        response_parking_data = post(operator_api_client, list_url, new_parking_data)

    new_parking = Parking.objects.get(id=response_parking_data['id'])
    end_time = start_time + settings.PARKKIHUBI_TIME_PARKINGS_EDITABLE + datetime.timedelta(minutes=1)

    with freeze_time(end_time):

        # PUT
        error_data = put(operator_api_client, get_detail_url(new_parking), updated_parking_data, 403)
        assert error_message in error_data['detail']
        assert error_data['code'] == error_code

        # PATCH other fields than 'time_end'
        for field_name in updated_parking_data:
            if field_name == 'time_end':
                continue
            parking_data = {field_name: updated_parking_data[field_name]}
            error_data = patch(operator_api_client, get_detail_url(new_parking), parking_data, 403)
            assert error_message in error_data['detail']
            assert error_data['code'] == error_code


def test_can_modify_time_end_after_modify_period(operator_api_client, new_parking_data):
    create_payment_zone(
        id=new_parking_data['zone'],
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    start_time = datetime.datetime(2010, 1, 1, 12, 00)

    with freeze_time(start_time):
        response_parking_data = post(operator_api_client, list_url, new_parking_data)

    new_parking = Parking.objects.get(id=response_parking_data['id'])
    end_time = start_time + settings.PARKKIHUBI_TIME_PARKINGS_EDITABLE + datetime.timedelta(minutes=1)

    with freeze_time(end_time):
        parking_data = {'time_end': '2016-12-12T23:33:29Z'}
        patch(operator_api_client, get_detail_url(new_parking), parking_data, 200)
        new_parking.refresh_from_db()
        assert new_parking.time_end.day == 12  # old day was 10


def test_time_start_cannot_be_after_time_end(operator_api_client, parking, new_parking_data):
    create_payment_zone(
        id=new_parking_data['zone'],
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())
    new_parking_data['time_start'] = '2116-12-10T23:33:29Z'
    detail_url = get_detail_url(parking)
    error_message = '"time_start" cannot be after "time_end".'

    # POST
    error_data = post(operator_api_client, list_url, new_parking_data, status_code=400)
    assert error_message in error_data['non_field_errors']

    # PUT
    error_data = put(operator_api_client, detail_url, new_parking_data, status_code=400)
    assert error_message in error_data['non_field_errors']

    # PATCH
    patch_data = {'time_start': '2116-12-10T23:33:29Z'}
    error_data = patch(operator_api_client, detail_url, patch_data, status_code=400)
    assert error_message in error_data['non_field_errors']


def test_parking_registration_number_special_chars(operator_api_client, new_parking_data):
    create_payment_zone(
        id=new_parking_data['zone'],
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    new_parking_data['registration_number'] = 'ÅÄÖÆØ-:'

    response_parking_data = post(operator_api_client, list_url, new_parking_data)

    check_response_parking_data(new_parking_data, response_parking_data)
    new_parking = Parking.objects.get(id=response_parking_data['id'])
    check_parking_data_matches_parking_object(new_parking_data, new_parking)


def test_default_enforcement_domain_is_used_on_parking_creation_if_not_specified(
    operator_api_client, new_parking_data
):
    create_payment_zone(
        id=new_parking_data['zone'],
        code=str(new_parking_data['zone']),
        number=new_parking_data['zone'],
        domain=EnforcementDomain.get_default_domain())

    response_parking_data = post(operator_api_client, list_url, new_parking_data)

    assert response_parking_data['domain'] == EnforcementDomain.get_default_domain().code


def test_enforcement_domain_can_be_specified_on_parking_creation(operator_api_client, new_parking_data):
    enforcement_domain = EnforcementDomain.objects.create(code='ESP', name='Espoo')
    new_parking_data.update(domain=enforcement_domain.code)
    create_payment_zone(id=new_parking_data['zone'],
                        code=str(new_parking_data['zone']),
                        number=new_parking_data['zone'],
                        domain=enforcement_domain)

    response_parking_data = post(operator_api_client, list_url, new_parking_data)

    assert not response_parking_data['domain'] == EnforcementDomain.get_default_domain().code
    assert response_parking_data['domain'] == enforcement_domain.code


def test_post_zone_as_string_or_integer(operator_api_client, new_parking_data):
    new_parking_data['zone'] = '2'
    create_payment_zone(code=str(new_parking_data['zone']), domain=EnforcementDomain.get_default_domain())
    response_parking_data = post(operator_api_client, list_url, new_parking_data)
    assert response_parking_data['zone'] == 2

    new_parking_data['zone'] = 5
    create_payment_zone(code=str(new_parking_data['zone']), domain=EnforcementDomain.get_default_domain())
    response_parking_data = post(operator_api_client, list_url, new_parking_data)
    assert response_parking_data['zone'] == 5

    new_parking_data['zone'] = '5A'
    create_payment_zone(code=str(new_parking_data['zone']), domain=EnforcementDomain.get_default_domain())
    response_parking_data = post(operator_api_client, list_url, new_parking_data)
    assert response_parking_data['zone'] == '5A'


def test_zone_in_correct_domain_is_set_for_parking(operator_api_client, new_parking_data):
    domain_1 = EnforcementDomain.get_default_domain()
    domain_2 = EnforcementDomain.objects.create(code='ESP', name='Espoo')

    zone_1 = create_payment_zone(code=str(new_parking_data['zone']), number=new_parking_data['zone'], domain=domain_1)
    zone_2 = create_payment_zone(code=str(new_parking_data['zone']), number=new_parking_data['zone'], domain=domain_2)

    response_parking_data_1 = post(operator_api_client, list_url, new_parking_data)

    new_parking_data['domain'] = domain_2.code
    response_parking_data_2 = post(operator_api_client, list_url, new_parking_data)

    new_parking_1 = Parking.objects.get(id=response_parking_data_1['id'])
    new_parking_2 = Parking.objects.get(id=response_parking_data_2['id'])

    assert new_parking_1.zone == zone_1
    assert new_parking_2.zone == zone_2
