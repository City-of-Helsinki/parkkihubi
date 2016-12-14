import json

from django.core.urlresolvers import reverse

from parkings.models import Parking

from ..utils import ALL_METHODS, check_list_endpoint_base_fields, check_method_status_codes, get, get_ids_from_results

list_url = reverse('internal:v1:parking-list')


def get_detail_url(obj):
    return reverse('internal:v1:parking-detail', kwargs={'pk': obj.pk})


def check_parking_data(parking_data, parking_obj):
    """
    Compare parking data dict returned from the API to the actual Parking object.
    """

    # check keys
    all_fields = {'id', 'created_at', 'modified_at', 'address', 'device_identifier', 'location', 'operator',
                  'registration_number', 'resident_code', 'special_code', 'time_start', 'time_end', 'zone', 'status'}
    assert set(parking_data.keys()) == all_fields

    # string valued fields should match 1:1
    for field in {'device_identifier', 'registration_number', 'resident_code', 'special_code', 'zone'}:
        assert parking_data[field] == getattr(parking_obj, field)

    assert parking_data['id'] == str(parking_obj.id)
    assert parking_data['created_at'] == parking_obj.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    assert parking_data['modified_at'] == parking_obj.modified_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    assert parking_data['time_start'] == parking_obj.time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['time_end'] == parking_obj.time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['operator'] == str(parking_obj.operator_id)
    assert parking_data['location'] == json.loads(parking_obj.location.geojson)
    assert parking_data['address'] == str(parking_obj.address_id)


def test_list_endpoint_base_fields(staff_api_client):
    parking_data = get(staff_api_client, list_url)
    check_list_endpoint_base_fields(parking_data)


def test_disallowed_methods(staff_api_client, parking):
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(staff_api_client, urls, disallowed_methods, 405)


def test_get_list_check_data(staff_api_client, parking):
    data = get(staff_api_client, list_url)
    assert len(data['results']) == 1
    check_parking_data(data['results'][0], parking)


def test_get_detail_check_data(staff_api_client, parking):
    parking_data = get(staff_api_client, get_detail_url(parking))
    check_parking_data(parking_data, parking)


def test_other_than_staff_cannot_do_anything(api_client, operator_api_client, parking):
    urls = (list_url, get_detail_url(parking))
    check_method_status_codes(api_client, urls, ALL_METHODS, 403)
    check_method_status_codes(operator_api_client, urls, ALL_METHODS, 403)


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
