from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)

from parkings.models import Permit

from ....factories.permit import (
    create_permit, generate_areas, generate_external_ids, generate_subjects)

list_url = reverse('operator:v1:activepermit-list')


def check_response_keys(response_data):
    expected_keys = {
        'id', 'domain', 'external_id',
        'series', 'subjects', 'areas', 'properties'
    }

    assert expected_keys == set(response_data.keys())


def test_operator_can_post_active_permit_by_external_id(operator_api_client):
    user = operator_api_client.auth_user
    active_permit = create_permit(
        active=True, owner=user, external_id='eID-42')
    data = {
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(active_permit.domain, allowed_user=user),
        'domain': active_permit.domain.code,
    }

    response = operator_api_client.post(list_url, data=data)

    assert response.status_code == HTTP_201_CREATED
    assert response.json()['series'] == active_permit.series.id
    check_response_keys(response.json())


def test_operator_cannot_view_permit_in_active_series_owned_by_other_operator(
    operator_api_client, operator_2
):
    create_permit(active=True, external_id='E', owner=operator_2.user)
    create_permit(active=True, external_id='F', owner=operator_2.user)

    response = operator_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['count'] == 0
    assert Permit.objects.count() == 2


def test_operator_can_only_view_permit_in_active_series_owned_by_themselves(
    operator_api_client, operator, operator_2
):
    operator_permit = create_permit(
        active=True, owner=operator.user, external_id='A')
    create_permit(active=True, owner=operator_2.user, external_id='B')
    create_permit(active=False, owner=operator.user, external_id='C')

    response = operator_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['count'] == 1
    assert Permit.objects.count() == 3
    assert response.json()['results'][0]['id'] == operator_permit.id
    assert response.json()['results'][0]['series'] == operator_permit.series.id


def get_active_permit_by_ext_id_detail_url(active_permit):
    return reverse(
        'operator:v1:activepermit-detail',
        kwargs={'external_id': active_permit.external_id}
    )


def test_operator_can_only_delete_permit_in_active_series_owned_by_themselves(
    operator_api_client, operator, operator_2,
):
    create_permit(
        active=False, owner=operator.user, external_id='Eid123')
    active_permit = create_permit(
        active=True, owner=operator_2.user, external_id='Eid123')
    url = get_active_permit_by_ext_id_detail_url(active_permit)

    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert Permit.objects.count() == 2

    operator_permit = create_permit(
        active=True, owner=operator.user, external_id='Eid123')

    url = get_active_permit_by_ext_id_detail_url(operator_permit)

    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Permit.objects.filter(id=operator_permit.id).exists()
    assert Permit.objects.filter(id=active_permit.id).exists()
