import pytest
from django.urls import reverse
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from parkings.models import Operator

from ..utils import (
    ALL_METHODS, check_list_endpoint_base_fields, check_method_status_codes,
    get)

list_url = reverse('enforcement:v1:operator-list')


def get_url(kind, operator):
    if kind == 'list':
        return list_url
    else:
        assert kind == 'detail'
        return reverse('enforcement:v1:operator-detail',
                       kwargs={'pk': operator.pk})


ALL_URL_KINDS = ['list', 'detail']


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_permission_checks(api_client, operator_api_client, operator, url_kind):
    url = get_url(url_kind, operator)
    check_method_status_codes(
        api_client, [url], ALL_METHODS, HTTP_401_UNAUTHORIZED)
    check_method_status_codes(
        operator_api_client, [url], ALL_METHODS, HTTP_403_FORBIDDEN,
        error_code='permission_denied')


@pytest.mark.parametrize('url_kind', ALL_URL_KINDS)
def test_disallowed_methods(enforcer_api_client, operator, url_kind):
    url = get_url(url_kind, operator)
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    check_method_status_codes(
        enforcer_api_client, [url], disallowed_methods, 405)


def test_list_endpoint_base_fields(enforcer_api_client):
    operator_data = get(enforcer_api_client, list_url)
    check_list_endpoint_base_fields(operator_data)


def test_list_endpoint_data(enforcer_api_client, operator):
    assert Operator.objects.count() == 1
    data = get(enforcer_api_client, list_url)
    assert len(data['results']) == 1
    operator_data = data['results'][0]
    check_operator_data_keys(operator_data)
    check_operator_data_matches_operator_object(data['results'][0], operator)


def check_operator_data_keys(operator_data):
    assert set(operator_data.keys()) == {
        'id', 'created_at', 'modified_at', 'name'}


def check_operator_data_matches_operator_object(operator_data, operator_obj):
    """
    Check that a operator data dict and an actual Operator object match.
    """
    assert operator_data['id'] == str(operator_obj.id)  # UUID -> str
    assert operator_data['created_at'] == iso8601_us(operator_obj.created_at)
    assert operator_data['modified_at'] == iso8601_us(operator_obj.modified_at)
    assert operator_data['name'] == operator_obj.name


def iso8601_us(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
