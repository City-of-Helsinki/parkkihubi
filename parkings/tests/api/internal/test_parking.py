import json

from django.core.urlresolvers import reverse

from ..utils import ALL_METHODS, check_method_status_codes, get

list_url = reverse('internal:v1:parking-list')


def get_detail_url(obj):
    return reverse('internal:v1:parking-detail', kwargs={'pk': obj.pk})


def check_parking_data_keys(parking_data):
    assert set(parking_data.keys()) == {
        'id', 'created_at', 'modified_at', 'address', 'parking_area',
        'device_identifier', 'location', 'operator', 'registration_number',
        'resident_code', 'special_code', 'time_start', 'time_end', 'zone',
        'status',
    }


def check_parking_data_matches_parking_object(parking_data, parking_obj):
    """
    Check that a parking data dict and an actual Parking object match.
    """

    # string and integer valued fields should match 1:1
    for field in {'device_identifier', 'registration_number', 'resident_code', 'special_code', 'zone'}:
        assert parking_data[field] == getattr(parking_obj, field)

    assert parking_data['id'] == str(parking_obj.id)
    assert parking_data['created_at'] == parking_obj.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    assert parking_data['modified_at'] == parking_obj.modified_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    assert parking_data['time_start'] == parking_obj.time_start.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['time_end'] == parking_obj.time_end.strftime('%Y-%m-%dT%H:%M:%SZ')
    assert parking_data['operator'] == str(parking_obj.operator_id)
    assert parking_data['location'] == json.loads(parking_obj.location.geojson)

    if parking_obj.address:
        address = parking_obj.address
        assert parking_data['address'] == {
            'city': address.city, 'postal_code': address.postal_code, 'street': address.street
        }
    else:
        assert parking_data['address'] is None


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
