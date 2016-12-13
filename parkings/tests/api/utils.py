import json
from rest_framework.authtoken.models import Token


def token_authenticate(api_client, user):
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION='ApiKey ' + token.key)
    return api_client


def get(api_client, url, status_code=200):
    response = api_client.get(url)
    assert response.status_code == status_code, '%s %s' % (response.status_code, response.data)
    return json.loads(response.content.decode('utf-8'))


def check_disallowed_methods(api_client, urls, disallowed_methods):
    # accept also a single url as a string
    if isinstance(urls, str):
        urls = (urls,)

    for url in urls:
        for method in disallowed_methods:
            response = getattr(api_client, method)(url)
            assert response.status_code == 405, (
                '%s %s %s %s' % (method, url, response.status_code, response.data)
            )


def check_list_endpoint_base_fields(data):
    assert set(data.keys()) == {'next', 'previous', 'count', 'results'}
