import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN


def _get_api_client(api_user, monitoring_api_client, enforcer_api_client,
                    operator_api_client, staff_api_client, user_api_client):
    if api_user == 'monitor':
        client = monitoring_api_client
    elif api_user == 'enforcer':
        client = enforcer_api_client
    elif api_user == 'operator':
        client = operator_api_client
    elif api_user == 'staff':
        client = staff_api_client
    else:
        client = user_api_client

    return client


@pytest.mark.parametrize(
    'api_user, status_code',
    [
        ('monitor', HTTP_200_OK),
        ('enforcer', HTTP_403_FORBIDDEN),
        ('operator', HTTP_403_FORBIDDEN),
        ('staff', HTTP_403_FORBIDDEN),
        ('user', HTTP_403_FORBIDDEN)
    ]
)
@pytest.mark.parametrize(
    'endpoint',
    ['valid_parking-list', 'region-list', 'regionstatistics-list']
)
def test_get_monitor_api_permission(
    api_user, monitoring_api_client, enforcer_api_client, operator_api_client,
    staff_api_client, user_api_client, status_code, endpoint
):
    client = _get_api_client(api_user, monitoring_api_client, enforcer_api_client,
                             operator_api_client, staff_api_client, user_api_client)

    list_url = reverse('monitoring:v1:{}'.format(endpoint))
    if endpoint == 'valid_parking-list':
        list_url += '?time=2020-04-02T15:56:43Z'
    response = client.get(list_url)
    assert response.status_code == status_code
