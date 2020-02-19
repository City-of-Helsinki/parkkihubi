from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from parkings.models import EnforcementDomain, PermitArea

from ..enforcement.test_check_parking import create_area_geom

list_url = reverse('operator:v1:permitarea-list')


def test_endpoint_returns_list_of_permitareas(operator_api_client, operator):
    domain = EnforcementDomain.objects.create(code='ESP', name='Espoo')
    PermitArea.objects.create(
        name='AreaOne', geom=create_area_geom(),
        identifier='A',
        permitted_user=operator.user,
        domain=domain
    )

    response = operator_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    expected_keys = {'code', 'domain', 'name'}
    assert json_response['count'] == 1
    assert set(json_response['results'][0]) == expected_keys
    assert json_response['results'][0]['domain'] == domain.code
    assert json_response['results'][0]['code'] == 'A'
    assert json_response['results'][0]['name'] == 'AreaOne'


def test_endpoint_returns_only_the_list_of_permitted_permitareas(
    operator_api_client, operator, staff_user
):
    domain = EnforcementDomain.objects.create(code='ESP', name='Espoo')
    PermitArea.objects.create(
        name='AreaOne', geom=create_area_geom(),
        identifier='A',
        permitted_user=operator.user,
        domain=domain
    )
    PermitArea.objects.create(
        name='AreaTwo', geom=create_area_geom(),
        identifier='B',
        permitted_user=staff_user,
        domain=domain
    )

    response = operator_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 1
    assert json_response['results'][0]['code'] == 'A'
    assert PermitArea.objects.count() == 2
