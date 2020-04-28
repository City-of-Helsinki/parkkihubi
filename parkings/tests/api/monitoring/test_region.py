import json

from django.urls import reverse
from rest_framework import status

from ...utils import approx

WGS84_SRID = 4326


list_url = reverse('monitoring:v1:region-list')


def test_get_regions_empty(monitoring_api_client):
    result = monitoring_api_client.get(list_url)
    assert result.data == {
        'type': 'FeatureCollection',
        'features': [],
        'count': 0,
        'next': None,
        'previous': None,
    }
    assert result.status_code == status.HTTP_200_OK


def test_get_regions_with_data(monitoring_api_client, region, parking_area):
    parking_area.geom = region.geom
    parking_area.save()
    region.domain = monitoring_api_client.monitor.domain
    region.save()  # Update capacity_estimate

    result = monitoring_api_client.get(list_url)
    features = result.data.pop('features', None)
    assert result.data == {
        'type': 'FeatureCollection',
        'count': 1,
        'next': None,
        'previous': None,
    }
    assert result.status_code == status.HTTP_200_OK
    assert isinstance(features, list)
    assert len(features) == 1
    geometry = features[0].pop('geometry', None)
    properties = features[0].pop('properties', None)
    assert features[0] == {'id': str(region.id), 'type': 'Feature'}
    km2 = region.geom.area / 1000000.0
    assert properties == approx({
        'name': region.name,
        'capacity_estimate': region.capacity_estimate,
        'area_km2': km2,
        'spots_per_km2': region.capacity_estimate / km2,
        'parking_areas': [parking_area.id],
    })
    coordinates = geometry.pop('coordinates', None)
    assert geometry == {'type': 'MultiPolygon'}
    wgs84_geom = region.geom.transform(WGS84_SRID, clone=True)
    assert coordinates == tuples_to_lists(wgs84_geom.coords)


def tuples_to_lists(tuples_of_tuples):
    return json.loads(json.dumps(tuples_of_tuples))


def test_monitor_can_view_only_regions_in_their_domain(monitoring_api_client, region_factory, parking_area):
    non_visible_region = region_factory()
    parking_area.geom = non_visible_region.geom
    parking_area.save()
    non_visible_region.save()
    result = monitoring_api_client.get(list_url)
    assert result.data['count'] == 0

    visible_region = region_factory(domain=monitoring_api_client.monitor.domain)
    parking_area.geom = visible_region.geom
    parking_area.save()
    visible_region.save()
    result = monitoring_api_client.get(list_url)
    assert result.data['count'] == 1
