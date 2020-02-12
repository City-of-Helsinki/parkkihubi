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
