import json
import uuid

from rest_framework.authtoken.models import Token

ALL_METHODS = ('get', 'post', 'put', 'patch', 'delete')


def token_authenticate(api_client, user):
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='ApiKey ' + token.key)
    return api_client


def get(api_client, url, status_code=200):
    response = api_client.get(url)
    assert response.status_code == status_code, '%s %s' % (response.status_code, response.data)
    return json.loads(response.content.decode('utf-8'))


def post(api_client, url, data=None, status_code=201):
    response = api_client.post(url, data)
    assert response.status_code == status_code, '%s %s' % (response.status_code, response.data)
    return json.loads(response.content.decode('utf-8'))


def put(api_client, url, data=None, status_code=200):
    response = api_client.put(url, data)
    assert response.status_code == status_code, '%s %s' % (response.status_code, response.data)
    return json.loads(response.content.decode('utf-8'))


def patch(api_client, url, data=None, status_code=200):
    response = api_client.patch(url, data)
    assert response.status_code == status_code, '%s %s' % (response.status_code, response.data)
    return json.loads(response.content.decode('utf-8'))


def delete(api_client, url, status_code=204):
    response = api_client.delete(url)
    assert response.status_code == status_code, '%s %s' % (response.status_code, response.data)


def check_method_status_codes(api_client, urls, methods, status_code, **kwargs):
    # accept also a single url as a string
    if isinstance(urls, str):
        urls = (urls,)

    for url in urls:
        for method in methods:
            response = getattr(api_client, method)(url)
            assert response.status_code == status_code, (
                '%s %s expected %s, got %s %s' % (method, url, status_code, response.status_code, response.data)
            )
            error_code = kwargs.get('error_code')
            if error_code:
                assert response.data['code'] == error_code, (
                    '%s %s expected error_code %s, got %s' % (method, url, error_code, response.data['code'])
                )


def check_list_endpoint_base_fields(data):
    assert set(data.keys()) == {'next', 'previous', 'count', 'results'}


def check_required_fields(api_client, url, expected_required_fields, detail_endpoint=False):
    method = put if detail_endpoint else post

    # send empty data to get all required fields in an error message, they will be in form
    # { "<field name>": ["This field is required"], "<field name 2>": ["This field is required"], ...}
    response_data = method(api_client, url, {}, 400)

    required_fields = set()
    for field in response_data:
        if isinstance(response_data[field], list) and 'This field is required.' in response_data[field]:
            required_fields.add(field)

    assert required_fields == expected_required_fields, '%s != %s' % (required_fields, expected_required_fields)


def get_ids_from_results(results, as_set=True):
    id_list = [uuid.UUID(result['id']) for result in results]
    return set(id_list) if as_set else id_list


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

    if parking_obj.address:
        address = parking_obj.address
        assert parking_data['address'] == {
            'city': address.city, 'postal_code': address.postal_code, 'street': address.street
        }
    else:
        assert parking_data['address'] is None
