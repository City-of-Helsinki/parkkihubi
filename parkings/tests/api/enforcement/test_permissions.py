import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

enforcer_endpoints = ('operator-list', 'permit-list', 'activepermit-list', 'permitseries-list')


def _get_api_client(api_user, enforcer_api_client, operator_api_client, staff_api_client, user_api_client):
    if api_user == 'enforcer_api':
        client = enforcer_api_client
    elif api_user == 'operator_api':
        client = operator_api_client
    elif api_user == 'staff_api':
        client = staff_api_client
    else:
        client = user_api_client

    return client


@pytest.mark.parametrize(
    'api_user, status_code',
    [
        ('enforcer_api', HTTP_200_OK),
        ('operator_api', HTTP_403_FORBIDDEN),
        ('staff_api', HTTP_403_FORBIDDEN),
        ('user_api', HTTP_403_FORBIDDEN)
    ]
)
def test_get_enforcement_api_permission(
    api_user, enforcer_api_client, operator_api_client,
    staff_api_client, user_api_client, status_code
):
    client = _get_api_client(api_user, enforcer_api_client, operator_api_client, staff_api_client, user_api_client)

    for endpoint in enforcer_endpoints:
        list_url = reverse('enforcement:v1:{}'.format(endpoint))
        response = client.get(list_url)
        assert response.status_code == status_code

        valid_parking_url = reverse('enforcement:v1:valid_parking-list') + '?reg_num=ABC-123'
        response = client.get(valid_parking_url)
        assert response.status_code == status_code
