import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)

from parkings.factories.permit import create_permit_series
from parkings.models import PermitSeries

url_list = reverse('operator:v1:permitseries-list')


def test_operator_can_view_only_own_permitseries(
    operator_api_client,
    admin_user
):
    permit_series = create_permit_series(owner=admin_user)

    response = operator_api_client.post(url_list, data={})
    assert response.status_code == HTTP_201_CREATED

    response = operator_api_client.get(url_list)

    assert response.status_code == HTTP_200_OK
    assert response.json()['count'] == 1
    assert PermitSeries.objects.count() == 2
    assert response.json()['results'][0]['id'] != permit_series.id


def test_operator_can_delete_own_permitseries(
    operator_api_client, operator, admin_user,
):
    permit_series = create_permit_series(owner=operator.user)
    admin_owned_permitseries = create_permit_series(owner=admin_user)

    url = reverse('operator:v1:permitseries-detail', kwargs={'pk': admin_owned_permitseries.pk})
    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert PermitSeries.objects.count() == 2

    url = reverse('operator:v1:permitseries-detail', kwargs={'pk': permit_series.pk})
    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_204_NO_CONTENT
    assert PermitSeries.objects.count() == 1
    assert PermitSeries.objects.first().id != permit_series.pk


def get_activate_url(permit_series):
    return '{}activate/'.format(get_detail_url(permit_series))


def get_detail_url(permit_series):
    pk = permit_series.pk
    return reverse('operator:v1:permitseries-detail', kwargs={'pk': pk})


def _create_permit_series(count=3, owner=None):
    for _ in range(count):
        PermitSeries.objects.create(active=True, owner=owner)


@pytest.mark.parametrize('deactivate_others', [True, False])
def test_activate_with_deactive_others(
    operator_api_client, operator, deactivate_others
):
    _create_permit_series(count=5, owner=operator.user)
    assert PermitSeries.objects.count() == 5

    series_to_activate = PermitSeries.objects.first()
    series_to_activate.active = False
    series_to_activate.save()

    response = operator_api_client.post(
        get_activate_url(series_to_activate),
        data={'deactivate_others': deactivate_others},
    )

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()
    assert series_to_activate.active
    assert response.json()['status'] == 'OK'

    if deactivate_others:
        assert PermitSeries.objects.filter(active=True).count() == 1
    else:
        assert PermitSeries.objects.filter(active=True).count() == 5


def test_activate_with_deactivate_series(
    operator_api_client, operator
):
    _create_permit_series(count=5, owner=operator.user)
    assert PermitSeries.objects.count() == 5

    series_to_activate = PermitSeries.objects.first()
    series_to_activate.active = False
    series_to_activate.save()

    series_to_deactivate = list(
        PermitSeries.objects.values_list('id', flat=True)[3:]
    )

    response = operator_api_client.post(
        get_activate_url(series_to_activate),
        data={'deactivate_series': series_to_deactivate},
    )

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()
    assert series_to_activate.active
    assert response.json()['status'] == 'OK'
    assert PermitSeries.objects.filter(active=False).count() == 2
    assert PermitSeries.objects.filter(active=True).count() == 3

    for series in PermitSeries.objects.filter(active=False):
        assert series.id in series_to_deactivate


@pytest.mark.parametrize('empty_data', [None, {}])
def test_activate_with_empty_payload(
    empty_data, operator_api_client, operator
):
    """
    Without params specified series is activated, nothing is deactivated.
    """
    _create_permit_series(count=3, owner=operator.user)
    series_to_activate = PermitSeries.objects.create(owner=operator.user, active=False)
    url = get_activate_url(series_to_activate)

    response = operator_api_client.post(url, data=empty_data)

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()

    assert series_to_activate.active
    assert PermitSeries.objects.filter(active=False).count() == 0


def test_activate_wont_deactivate_enforcer_series(
    operator_api_client, operator, staff_user
):
    _create_permit_series(count=5, owner=operator.user)
    _create_permit_series(count=5, owner=staff_user)

    series_to_activate = PermitSeries.objects.filter(owner=operator.user).first()
    series_to_activate.active = False
    series_to_activate.save()
    url = get_activate_url(series_to_activate)

    response = operator_api_client.post(url, data={'deactivate_others': True})

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()
    assert series_to_activate.active
    assert response.json()['status'] == 'OK'
    assert not PermitSeries.objects.filter(owner=staff_user, active=False).exists()
    assert PermitSeries.objects.filter(owner=staff_user, active=True).count() == 5


def test_activate_wont_deactivate_series_owned_by_others(
    operator_api_client, operator, staff_user
):
    _create_permit_series(count=5, owner=operator.user)
    _create_permit_series(count=5, owner=staff_user)

    series_to_activate = PermitSeries.objects.first()
    series_to_activate.active = False
    series_to_activate.save()

    staff_series_to_deactivate = list(
        PermitSeries.objects.filter(owner=staff_user).values_list('id', flat=True)[3:]
    )
    operator_series_to_deactivate = list(
        PermitSeries.objects.filter(owner=operator.user).values_list('id', flat=True)[3:]
    )
    series_to_deactivate = staff_series_to_deactivate + operator_series_to_deactivate

    response = operator_api_client.post(
        get_activate_url(series_to_activate),
        data={'deactivate_series': series_to_deactivate},
    )

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()
    assert series_to_activate.active
    assert response.json()['status'] == 'OK'
    assert PermitSeries.objects.filter(active=False).count() == 2
    assert PermitSeries.objects.filter(active=True).count() == 8

    for series in PermitSeries.objects.filter(active=False):
        assert series.id in operator_series_to_deactivate

    assert PermitSeries.objects.filter(owner=staff_user, active=True).count() == 5
