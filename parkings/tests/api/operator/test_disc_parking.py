import datetime

import pytest
from django.urls import reverse

from parkings.models import Parking

from ..utils import delete, patch, post

list_url = reverse('operator:v1:parking-list')


def get_detail_url(obj):
    return reverse('operator:v1:parking-detail', kwargs={'pk': obj.pk})


@pytest.fixture
def disc_parking_data():
    return {
        'registration_number': 'VSM-162',
        'time_start': '2016-12-12T20:34:38Z',
        'location': {'coordinates': [60.16899227603715, 24.9482582558314], 'type': 'Point'},
        'is_disc_parking': True
    }


expected_keys = {
        'id', 'zone', 'registration_number',
        'terminal_number',
        'time_start', 'time_end',
        'location', 'created_at', 'modified_at',
        'status', 'is_disc_parking', 'domain',
    }


def test_post_disc_parking(operator_api_client, operator, disc_parking_data):
    response_parking_data = post(operator_api_client, list_url, disc_parking_data)

    returned_data_keys = set(response_parking_data)
    posted_data_keys = set(disc_parking_data)
    assert returned_data_keys == expected_keys

    for key in returned_data_keys & posted_data_keys:
        assert response_parking_data[key] == disc_parking_data[key]


@pytest.mark.parametrize('kind', ['had time_end', 'didnt have time_end'])
def test_end_disc_parking_with_patch(
        kind, operator_api_client, operator, disc_parking):
    detail_url = get_detail_url(disc_parking)

    if kind == 'had time_end':
        disc_parking.time_end = (
            disc_parking.time_start + datetime.timedelta(hours=5))
    else:
        disc_parking.time_end = None
    disc_parking.save()

    new_time_end = disc_parking.time_start + datetime.timedelta(hours=2)
    time_end = new_time_end.strftime('%Y-%m-%dT%H:%M:%SZ')

    patch(operator_api_client, detail_url, data={'time_end': time_end})
    disc_parking.refresh_from_db()

    assert disc_parking.time_end.strftime('%Y-%m-%dT%H:%M:%SZ') == time_end


def test_delete_disc_parking(operator_api_client, disc_parking):
    detail_url = get_detail_url(disc_parking)
    delete(operator_api_client, detail_url)

    assert not Parking.objects.filter(id=disc_parking.id).exists()


def test_required_fields_for_disc_parking(operator_api_client, operator, disc_parking_data):
    disc_parking_data.pop('location')
    post(operator_api_client, list_url, disc_parking_data, status_code=400)
