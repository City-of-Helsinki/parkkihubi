import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)

from ....factories.permit import (
    create_permit_area, generate_areas, generate_external_ids,
    generate_subjects)

list_url = reverse('enforcement:v1:activepermit-list')


@pytest.mark.django_db
def test_post_active_permit_by_external_id(staff_api_client, permit_series):
    permit_series.active = True
    permit_series.save()
    data = {
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas()
    }

    response = staff_api_client.post(list_url, data=data)

    assert response.status_code == HTTP_201_CREATED
    assert response.data['series'] == permit_series.id


@pytest.mark.django_db
def test_patch_active_permit_by_external_id(staff_api_client, active_permit):
    areas = generate_areas()
    create_permit_area('X1')
    areas[0].update(area='X1')
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = staff_api_client.patch(active_permit_by_external_id_url, data={'areas': areas})

    assert response.status_code == HTTP_200_OK
    assert response.data['areas'] == areas


@pytest.mark.django_db
def test_put_active_permit_by_external_id(staff_api_client, active_permit):
    areas = generate_areas(count=2)
    response = staff_api_client.get(list_url)
    put_data = response.data['results'][0]
    put_data.update(areas=areas)
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = staff_api_client.put(active_permit_by_external_id_url, data=put_data)

    assert response.status_code == HTTP_200_OK
    assert response.data['areas'] == areas


@pytest.mark.django_db
def test_post_active_permit_by_external_id_fails_if_no_active_series_exists(staff_api_client, permit):
    data = {
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas()
    }

    response = staff_api_client.post(list_url, data=data)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.data == {'detail': "Active permit series doesn't exist"}


def test_invalid_put_active_permit_by_external_id(staff_api_client, active_permit):
    areas = generate_areas()
    del areas[0]['start_time']
    response = staff_api_client.get(list_url)
    put_data = response.data['results'][0]
    put_data.update(areas=areas)
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = staff_api_client.put(active_permit_by_external_id_url, data=put_data)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert set(response.data.keys()) == {'areas'}


def test_invalid_patch_active_permit_by_external_id(staff_api_client, active_permit):
    areas = generate_areas()
    del areas[0]['start_time']
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = staff_api_client.patch(active_permit_by_external_id_url, data={'areas': areas})

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert set(response.data.keys()) == {'areas'}


def test_get_active_permit_by_external_id(staff_api_client, active_permit, permit):
    response = staff_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['id'] != permit.id
    assert response.data['results'][0]['id'] == active_permit.id
