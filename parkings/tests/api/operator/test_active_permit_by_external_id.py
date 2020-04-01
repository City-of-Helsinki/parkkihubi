from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)

from parkings.models import EnforcementDomain, Permit

from ....factories.permit import (
    generate_areas, generate_external_ids, generate_subjects)

list_url = reverse('operator:v1:activepermit-list')


def check_response_keys(response_data):
    expected_keys = {
        'id', 'domain', 'external_id',
        'series', 'subjects', 'areas'
    }

    assert expected_keys == set(response_data.keys())


def test_operator_can_post_active_permit_by_external_id(operator_api_client, active_permit):
    enforcement_domain = EnforcementDomain.objects.create(code='ESP', name='EspooDomain')
    data = {
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(),
        'domain': enforcement_domain.code,
    }

    response = operator_api_client.post(list_url, data=data)

    assert response.status_code == HTTP_201_CREATED
    assert response.json()['series'] == active_permit.series.id
    check_response_keys(response.json())


def test_operator_cannot_view_permit_in_active_series_owned_by_other_operator(
    operator_api_client, active_permit, permit
):
    response = operator_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['count'] == 0
    assert Permit.objects.count() == 2


def test_operator_can_only_view_permit_in_active_series_owned_by_themselves(
    operator_api_client, active_permit, operator,
    permit_series_factory, permit_factory, permit
):
    operator_owned_active_permitseries = permit_series_factory(active=True, owner=operator.user)
    operator_permit = permit_factory(series=operator_owned_active_permitseries)

    response = operator_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['count'] == 1
    assert Permit.objects.count() == 3
    assert response.json()['results'][0]['id'] == operator_permit.id
    assert response.json()['results'][0]['series'] == operator_owned_active_permitseries.id


def get_active_permit_by_ext_id_detail_url(active_permit):
    return reverse(
        'operator:v1:activepermit-detail',
        kwargs={'external_id': active_permit.external_id}
    )


def test_operator_can_only_delete_permit_in_active_series_owned_by_themselves(
    operator_api_client, active_permit, permit, operator,
    permit_series_factory, permit_factory
):
    url = get_active_permit_by_ext_id_detail_url(active_permit)

    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert Permit.objects.count() == 2

    operator_owned_active_permitseries = permit_series_factory(active=True, owner=operator.user)
    operator_permit = permit_factory(series=operator_owned_active_permitseries)

    url = get_active_permit_by_ext_id_detail_url(operator_permit)

    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_204_NO_CONTENT
    assert not Permit.objects.filter(id=operator_permit.id).exists()
