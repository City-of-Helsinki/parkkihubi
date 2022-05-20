import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.status import (
    HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)

from parkings.factories.permit import create_permit, create_permits
from parkings.models import PermitLookupItem
from parkings.tests.api.enforcement.test_valid_parking import iso8601

from ..utils import (
    ALL_METHODS, check_cursor_list_endpoint_base_fields,
    check_method_status_codes, get)

list_url = reverse('enforcement:v1:valid_permit_item-list')


def list_url_for(reg_num=None, time=None):
    assert reg_num or time
    if not time:
        return '{url}?reg_num={reg_num}'.format(url=list_url, reg_num=reg_num)
    elif not reg_num:
        return '{url}?time={time}'.format(url=list_url, time=iso8601(time))
    else:
        return '{url}?reg_num={reg_num}&time={time}'.format(url=list_url, reg_num=reg_num, time=iso8601(time))


def get_url(kind, permit_item):
    if kind == 'list':
        return list_url_for(reg_num=permit_item.registration_number, time=timezone.now())
    elif kind == 'list_by_reg_num':
        return list_url_for(reg_num=permit_item.registration_number)
    elif kind == 'list_by_reg_num_and_time':
        return list_url_for(reg_num=permit_item.registration_number, time=timezone.now())
    else:
        assert kind == 'list_by_time'
        return list_url_for(time=timezone.now())


ALL_URL_KINDS = ['list', 'list_by_reg_num', 'list_by_reg_num_and_time', 'list_by_time']


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_permission_checks(api_client, operator_api_client, enforcer, url_kind):
    create_permit(active=True, owner=enforcer.user, domain=enforcer.enforced_domain)
    permit_item = PermitLookupItem.objects.first()
    url = get_url(url_kind, permit_item)
    check_method_status_codes(
        api_client, [url], ALL_METHODS, HTTP_401_UNAUTHORIZED)
    check_method_status_codes(
        operator_api_client, [url], ALL_METHODS, HTTP_403_FORBIDDEN,
        error_code='permission_denied')


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_disallowed_methods(enforcer_api_client, enforcer, url_kind):
    create_permit(active=True, owner=enforcer.user, domain=enforcer.enforced_domain)
    permit_item = PermitLookupItem.objects.first()
    url = get_url(url_kind, permit_item)
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    check_method_status_codes(
        enforcer_api_client, [url], disallowed_methods, 405)


def test_reg_num_and_time_are_optional(enforcer_api_client):
    response = enforcer_api_client.get(list_url)
    assert response.status_code == HTTP_200_OK
    assert response.data == {'next': None, 'previous': None, 'results': []}


def test_list_endpoint_base_fields(enforcer_api_client):
    permit_item_data = get(enforcer_api_client, list_url_for(reg_num='ABC-123'))
    check_cursor_list_endpoint_base_fields(permit_item_data)


def test_list_endpoint_data(enforcer_api_client, enforcer, operator_factory):
    operator_factory(user=enforcer.user)
    create_permit(active=True, owner=enforcer.user, domain=enforcer.enforced_domain, subject_count=1, area_count=1)
    assert PermitLookupItem.objects.count() == 1
    permit_item = PermitLookupItem.objects.first()

    data = get(enforcer_api_client, get_url('list_by_reg_num', permit_item))
    assert len(data['results']) == 1

    permit_item_data = data['results'][0]
    check_permit_item_data_keys(permit_item_data)
    check_permit_item_data_matches_permitlookuptem_object(data['results'][0], permit_item)


def check_permit_item_data_keys(permit_item_data):
    assert set(permit_item_data.keys()) == {
        'id',
        'permit_id',
        'area',
        'registration_number',
        'start_time',
        'end_time',
        'operator',
        'operator_name',
        'properties',
    }


def check_permit_item_data_matches_permitlookuptem_object(permit_item_data, permit_item):
    assert permit_item_data['id'] == permit_item.id
    assert permit_item_data['permit_id'] == permit_item.permit.id
    assert permit_item_data['area'] == permit_item.area.identifier
    assert permit_item_data['registration_number'] == permit_item.registration_number
    assert permit_item_data['start_time'] == iso8601(permit_item.start_time)
    assert permit_item_data['end_time'] == iso8601(permit_item.end_time)
    assert permit_item_data['operator'] == str(permit_item.permit.series.owner.operator.id)
    assert permit_item_data['operator_name'] == permit_item.permit.series.owner.operator.name


def test_registration_number_filter(enforcer_api_client, enforcer):
    create_permits(active=True, owner=enforcer.user, domain=enforcer.enforced_domain)
    for permit_item in PermitLookupItem.objects.all():
        results = get(enforcer_api_client, list_url_for(reg_num=permit_item.registration_number))['results']
        for result in results:
            assert result['registration_number'] == permit_item.registration_number


def test_time_filter(enforcer_api_client, enforcer):
    create_permit(active=True, owner=enforcer.user, domain=enforcer.enforced_domain, subject_count=2, area_count=1)
    permit_1 = PermitLookupItem.objects.all()[0]
    permit_2 = PermitLookupItem.objects.all()[1]

    response = get(enforcer_api_client, list_url_for(time=timezone.now()))
    assert len(response['results']) == 2

    permit_2.end_time = timezone.now() - datetime.timedelta(seconds=900)
    permit_2.save()

    response = get(enforcer_api_client, list_url_for(time=timezone.now()))
    assert len(response['results']) == 1
    assert response['results'][0]['registration_number'] == permit_1.registration_number


def test_registration_number_and_time_filter(enforcer_api_client, enforcer):
    create_permit(active=True, owner=enforcer.user, domain=enforcer.enforced_domain, subject_count=2, area_count=1)
    permit_1 = PermitLookupItem.objects.first()

    response = get(enforcer_api_client, list_url_for(reg_num=permit_1.registration_number, time=timezone.now()))

    assert len(response['results']) == 1
    assert response['results'][0]['registration_number'] == permit_1.registration_number


def test_enforcer_can_view_only_permit_items_from_domain_they_enforce(enforcer_api_client, enforcer):
    create_permits(active=True, owner=enforcer.user, domain=enforcer.enforced_domain, count=1)
    create_permits(active=True, count=1)

    enforcer_permits = PermitLookupItem.objects.filter(permit__domain=enforcer.enforced_domain)

    assert PermitLookupItem.objects.count() == 12
    assert enforcer_permits.count() == 6

    response = get(enforcer_api_client, list_url_for(time=timezone.now()))

    assert len(response['results']) == 6
    for results in response['results']:
        assert results['registration_number'] in enforcer_permits.values_list('registration_number', flat=True)
