import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)

from parkings.models import PermitSeries

url_list = reverse('operator:v1:permitseries-list')


def test_operator_can_view_only_permitseries_owned_by_herself(
    operator_api_client,
    permit_series,
    admin_user
):
    permit_series.owner = admin_user
    permit_series.save()

    response = operator_api_client.post(url_list, data={})
    assert response.status_code == HTTP_201_CREATED

    response = operator_api_client.get(url_list)

    assert response.status_code == HTTP_200_OK
    assert response.json()['count'] == 1
    assert PermitSeries.objects.count() == 2
    assert response.json()['results'][0]['id'] != permit_series.id


def test_operator_can_delete_permitseries_owned_by_herself(
    operator_api_client,
    permit_series,
    admin_user,
    permit_series_factory
):
    admin_owned_permitseries = permit_series_factory(owner=admin_user)

    url = reverse('operator:v1:permitseries-detail', kwargs={'pk': admin_owned_permitseries.pk})
    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_404_NOT_FOUND
    assert PermitSeries.objects.count() == 2

    url = reverse('operator:v1:permitseries-detail', kwargs={'pk': permit_series.pk})
    response = operator_api_client.delete(url)

    assert response.status_code == HTTP_204_NO_CONTENT
    assert PermitSeries.objects.count() == 1
    assert PermitSeries.objects.first().id != permit_series.pk


def get_permitseries_detail_url(obj):
    return reverse('operator:v1:permitseries-detail', kwargs={'pk': obj.pk})


def _create_permit_series(count=3, owner=None, active=False):
    for _ in range(count):
        PermitSeries.objects.create(active=active, owner=owner)


@pytest.mark.parametrize('deactivate_others', [True, False])
def test_operator_can_deactivate_all_other_series_activating_main(
    operator_api_client, operator, deactivate_others
):
    _create_permit_series(count=5, owner=operator.user, active=True)
    assert PermitSeries.objects.count() == 5

    series_to_activate = PermitSeries.objects.first()
    series_to_activate.active = False
    series_to_activate.save()

    response = operator_api_client.post(
        '{}activate/'.format(get_permitseries_detail_url(series_to_activate)),
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


def test_operator_can_deactivate_specified_series_activating_main(
    operator_api_client, operator
):
    _create_permit_series(count=5, owner=operator.user, active=True)
    assert PermitSeries.objects.count() == 5

    series_to_activate = PermitSeries.objects.first()
    series_to_activate.active = False
    series_to_activate.save()

    series_to_deactivate = list(
        PermitSeries.objects.values_list('id', flat=True)[3:]
    )

    response = operator_api_client.post(
        '{}activate/'.format(get_permitseries_detail_url(series_to_activate)),
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


def test_operator_activates_specified_series_and_deactivates_no_other_series_on_empty_payload(
    operator_api_client, operator
):
    _create_permit_series(count=3, owner=operator.user, active=True)
    series_to_activate = PermitSeries.objects.create(owner=operator.user, active=False)

    response = operator_api_client.post(
        '{}activate/'.format(get_permitseries_detail_url(series_to_activate), data={}),
    )

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()

    assert series_to_activate.active
    assert PermitSeries.objects.filter(active=False).count() == 0


def test_operator_activate_series_doesnot_deactivate_enforcer_owned_series(
    operator_api_client, operator, staff_user
):
    _create_permit_series(count=5, owner=operator.user, active=True)
    _create_permit_series(count=5, owner=staff_user, active=True)

    series_to_activate = PermitSeries.objects.filter(owner=operator.user).first()
    series_to_activate.active = False
    series_to_activate.save()

    response = operator_api_client.post(
        '{}activate/'.format(get_permitseries_detail_url(series_to_activate)),
        data={'deactivate_others': True},
    )

    assert response.status_code == HTTP_200_OK
    series_to_activate.refresh_from_db()
    assert series_to_activate.active
    assert response.json()['status'] == 'OK'
    assert not PermitSeries.objects.filter(owner=staff_user, active=False).exists()


def test_operator_cannot_deactivate_series_owned_by_others_even_when_explicitly_specified(
    operator_api_client, operator, staff_user
):
    _create_permit_series(count=5, owner=operator.user, active=True)
    _create_permit_series(count=5, owner=staff_user, active=True)

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
        '{}activate/'.format(get_permitseries_detail_url(series_to_activate)),
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
