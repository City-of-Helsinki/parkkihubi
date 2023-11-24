from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND)

from ....factories.permit import (
    create_permit, create_permit_area, create_permit_series, generate_areas,
    generate_external_ids, generate_subjects)
from ....models import PermitSeries

list_url = reverse('enforcement:v1:activepermit-list')


def create_active_permit(client):
    return create_permit(
        active=True,
        owner=client.auth_user,
        domain=client.enforcer.enforced_domain,
        external_id='eID-42',
    )


def generate_areas_data(client):
    user = client.auth_user
    domain = client.enforcer.enforced_domain
    areas = generate_areas(domain=domain, allowed_user=user, count=2)
    create_permit_area('X1', domain=domain, allowed_user=user)
    areas[0]['area'] = 'X1'
    return areas


@pytest.mark.django_db
def test_post_active_permit_by_external_id(enforcer_api_client, enforcer):
    permit_series = create_permit_series(owner=enforcer.user, active=True)
    data = {
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(
            domain=enforcer.enforced_domain, allowed_user=enforcer.user),
    }

    response = enforcer_api_client.post(list_url, data=data)

    returned_id = response.data.pop('id', None)
    assert response.data == dict(data, series=permit_series.id, properties=None)
    assert isinstance(returned_id, int)
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.django_db
def test_patch_active_permit_by_external_id(enforcer_api_client):
    active_permit = create_active_permit(enforcer_api_client)
    areas = generate_areas_data(enforcer_api_client)
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = enforcer_api_client.patch(active_permit_by_external_id_url, data={'areas': areas})

    assert response.status_code == HTTP_200_OK
    assert response.data['areas'] == areas


@pytest.mark.django_db
def test_put_active_permit_by_external_id(enforcer_api_client):
    active_permit = create_active_permit(enforcer_api_client)
    areas = generate_areas_data(enforcer_api_client)
    response = enforcer_api_client.get(list_url)
    put_data = response.data['results'][0]
    put_data.update(areas=areas)
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = enforcer_api_client.put(active_permit_by_external_id_url, data=put_data)

    assert response.status_code == HTTP_200_OK
    assert response.data['areas'] == areas


@pytest.mark.django_db
def test_post_active_permit_by_external_id_fails_if_no_active_series_exists(enforcer_api_client):
    data = {
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas_data(enforcer_api_client),
    }

    response = enforcer_api_client.post(list_url, data=data)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.data == {'detail': "Active permit series doesn't exist"}


def test_invalid_put_active_permit_by_external_id(enforcer_api_client):
    active_permit = create_active_permit(enforcer_api_client)
    areas = generate_areas_data(enforcer_api_client)
    del areas[0]['start_time']
    response = enforcer_api_client.get(list_url)
    put_data = response.data['results'][0]
    put_data.update(areas=areas)
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = enforcer_api_client.put(active_permit_by_external_id_url, data=put_data)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert set(response.data.keys()) == {'areas'}


def test_invalid_patch_active_permit_by_external_id(enforcer_api_client):
    active_permit = create_active_permit(enforcer_api_client)
    areas = generate_areas_data(enforcer_api_client)
    del areas[0]['start_time']
    active_permit_by_external_id_url = '{}{}/'.format(list_url, active_permit.external_id)

    response = enforcer_api_client.patch(active_permit_by_external_id_url, data={'areas': areas})

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert set(response.data.keys()) == {'areas'}


def test_get_active_permit_by_external_id(enforcer_api_client):
    active_permit = create_active_permit(enforcer_api_client)
    permit = create_permit(owner=enforcer_api_client.auth_user)
    response = enforcer_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['id'] != permit.id
    assert response.data['results'][0]['id'] == active_permit.id


def test_active_permit_visibility_is_limited_to_permitseries_owner(enforcer_api_client):
    active_permit = create_permit(
        domain=enforcer_api_client.enforcer.enforced_domain,
        active=True,
        external_id='E-123')
    assert active_permit.series.owner != enforcer_api_client.auth_user

    response = enforcer_api_client.get(list_url)

    assert response.data == {
        'count': 0, 'next': None, 'previous': None, 'results': []}
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_permit_is_created_to_correct_series(
        enforcer_api_client, enforcer, admin_user):
    """
    Test permit is created to a series owned by the request performer.

    If there are several active permit series, only those which are
    owned by the user who performs the request should be considered,
    when picking the latest active permit series.
    """
    permit_series = create_permit_series(owner=enforcer.user, active=True)
    other_series = create_permit_series(owner=admin_user, active=True)
    other_series.modified_at = permit_series.modified_at + timedelta(seconds=1)
    other_series.save(update_fields=['modified_at'])
    assert other_series.modified_at > permit_series.modified_at
    assert PermitSeries.objects.latest_active() == other_series
    data = {
        'external_id': 'Extern1234',
        'subjects': [],
        'areas': [],
    }

    response = enforcer_api_client.post(list_url, data=data)

    assert response.data.get('series') == permit_series.id
    assert response.status_code == HTTP_201_CREATED
