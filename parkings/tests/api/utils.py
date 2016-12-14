import json

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


def check_method_status_codes(api_client, urls, methods, status_code):
    # accept also a single url as a string
    if isinstance(urls, str):
        urls = (urls,)

    for url in urls:
        for method in methods:
            response = getattr(api_client, method)(url)
            assert response.status_code == status_code, (
                '%s %s expected %s, got %s %s' % (method, url, status_code, response.status_code, response.data)
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

    assert required_fields == expected_required_fields
