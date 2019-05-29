import pytest
from django.core.urlresolvers import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN)

from ....factories.permit import (
    generate_areas, generate_external_ids, generate_subjects)
from ....models import PermitCacheItem

list_url = reverse('enforcement:v1:permit-list')


@pytest.mark.django_db
def test_unauthorized_user_cannot_create_permit(user_api_client, permit_series):
    permit_data = {
        'series': permit_series.id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(),
    }

    response = user_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permit_is_created_with_valid_post_data(staff_api_client, permit_series):
    permit_data = {
        'series': permit_series.id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(),
    }

    response = staff_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED


@pytest.mark.django_db
def test_permit_is_not_created_with_invalid_post_data(staff_api_client, permit_series):
    valid_subject = generate_subjects()
    del valid_subject[0]['start_time']
    invalid_permit_data = {
        'series': permit_series.id,
        'external_id': generate_external_ids(),
        'subjects': valid_subject,
        'areas': generate_areas()
    }

    response = staff_api_client.post(list_url, data=invalid_permit_data)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data['subjects'] == ['Subjects is not valid']


@pytest.mark.django_db
def test_cache_item_is_created_for_permit(staff_api_client, permit_series):
    permit_data = {
        'series': permit_series.id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(),
    }
    assert PermitCacheItem.objects.count() == 0
    response = staff_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED
    assert PermitCacheItem.objects.count() == 1


def test_api_endpoint_returns_correct_data(staff_api_client, permit):
    response = staff_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    check_permit_object_keys(response.data['results'][0])
    check_permit_subject_keys(response.data['results'][0]['subjects'][0])
    check_permit_areas_keys(response.data['results'][0]['areas'][0])


def check_permit_object_keys(data):
    assert set(data.keys()) == {'id', 'series', 'subjects', 'areas', 'external_id'}


def check_permit_subject_keys(data):
    assert set(data.keys()) == {'start_time', 'end_time', 'registration_number'}


def check_permit_areas_keys(data):
    assert set(data.keys()) == {'start_time', 'end_time', 'area'}


def test_permit_data_matches_permit_object(staff_api_client, permit):
    permit_detail_url = '{}{}/'.format(list_url, permit.id)

    response = staff_api_client.get(permit_detail_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['id'] == permit.id
    assert response.data['series'] == permit.series.id
    assert response.data['subjects'] == permit.subjects
    assert response.data['areas'] == permit.areas
    check_permit_object_keys(response.data)
    check_permit_subject_keys(response.data['subjects'][0])
    check_permit_areas_keys(response.data['areas'][0])
