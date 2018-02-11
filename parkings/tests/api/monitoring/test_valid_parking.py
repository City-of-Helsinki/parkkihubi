import pytest
from django.core.urlresolvers import reverse
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_405_METHOD_NOT_ALLOWED)

from ..utils import ALL_METHODS, check_method_status_codes

list_url = reverse('monitoring:v1:valid_parking-list')


def detail_url(parking):
    return reverse('monitoring:v1:valid_parking-detail',
                   kwargs={'pk': parking.pk})


@pytest.mark.parametrize('kind', ['list', 'detail'])
def test_permission_checks(api_client, operator_api_client, parking, kind):
    url = list_url if kind == 'list' else detail_url(parking)
    check_method_status_codes(
        api_client, [url], ALL_METHODS, HTTP_401_UNAUTHORIZED)
    check_method_status_codes(
        operator_api_client, [url], ALL_METHODS, HTTP_403_FORBIDDEN,
        error_code='permission_denied')


@pytest.mark.parametrize('kind', ['list', 'detail'])
def test_disallowed_methods(monitoring_api_client, parking, kind):
    url = list_url if kind == 'list' else detail_url(parking)
    methods = [x for x in ALL_METHODS if x != 'get']
    check_method_status_codes(
        monitoring_api_client, [url], methods, HTTP_405_METHOD_NOT_ALLOWED)


def test_list_endpoint_data(monitoring_api_client, parking):
    result = monitoring_api_client.get(
        list_url, data={'time': parking.time_start.isoformat()})
    assert set(result.data.keys()) == {
        'type', 'count', 'next', 'previous', 'features'}
    assert result.data['type'] == 'FeatureCollection'
    assert result.data['next'] is None
    assert result.data['previous'] is None
    assert result.data['count'] == 1
    assert len(result.data['features']) == 1
    parking_feature = result.data['features'][0]
    check_parking_feature_shape(parking_feature)
    check_parking_feature_matches_parking_object(parking_feature, parking)


def check_parking_feature_shape(parking_feature):
    assert set(parking_feature.keys()) == {
        'id', 'type', 'geometry', 'properties'}
    assert parking_feature['type'] == 'Feature'
    assert set(parking_feature['geometry'].keys()) == {
        'type', 'coordinates'}
    assert parking_feature['geometry']['type'] == 'Point'
    assert len(parking_feature['geometry']['coordinates']) == 2
    assert set(parking_feature['properties'].keys()) == {
        'created_at', 'modified_at',
        'time_start', 'time_end',
        'registration_number',
        'terminal_number',
        'operator_name',
        'region', 'zone',
    }


def check_parking_feature_matches_parking_object(parking_feature, parking_obj):
    assert parking_feature['id'] == str(parking_obj.id)
    assert parking_feature['geometry']['coordinates'] == list(
        parking_obj.location.coords)
    props = parking_feature['properties']
    direct_fields = ['registration_number', 'terminal_number', 'zone']
    for field in direct_fields:
        assert props[field] == getattr(parking_obj, field)

    assert props['created_at'] == iso8601_us(parking_obj.created_at)
    assert props['modified_at'] == iso8601_us(parking_obj.modified_at)
    assert props['time_start'] == iso8601(parking_obj.time_start)
    assert props['time_end'] == iso8601(parking_obj.time_end)
    assert props['operator_name'] == parking_obj.operator.name
    assert props['region'] == getattr(parking_obj.region, 'pk', None)


def iso8601(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def iso8601_us(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
