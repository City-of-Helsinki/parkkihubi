from django.contrib.gis.geos import MultiPolygon, Polygon
from django.urls import reverse

from ..utils import check_method_status_codes, get, get_ids_from_results

list_url = reverse('public:v1:parkingarea-list')


def get_detail_url(obj):
    return reverse('public:v1:parkingarea-detail', kwargs={'pk': obj.pk})


def test_disallowed_methods(api_client, parking_area):
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    urls = (list_url, get_detail_url(parking_area))
    check_method_status_codes(api_client, urls, disallowed_methods, 405)


def test_get_list_check_data(api_client, parking_area):
    data = get(api_client, list_url)
    assert data.keys() == {'type', 'count', 'next', 'previous', 'features'}
    assert data['type'] == 'FeatureCollection'
    assert data['count'] == 1

    feature_data = data['features'][0]
    assert feature_data.keys() == {'id', 'type', 'geometry', 'properties'}
    assert feature_data['type'] == 'Feature'
    assert feature_data['id'] == str(parking_area.id)

    geometry_data = feature_data['geometry']
    assert geometry_data.keys() == {'type', 'coordinates'}
    assert geometry_data['type'] == 'MultiPolygon'
    assert len(geometry_data['coordinates']) > 0

    properties_data = feature_data['properties']
    assert properties_data.keys() == {'capacity_estimate'}
    assert properties_data['capacity_estimate'] == parking_area.capacity_estimate


def test_get_detail_check_data(api_client, parking_area):
    feature_data = get(api_client, get_detail_url(parking_area))
    assert feature_data.keys() == {'id', 'type', 'geometry', 'properties'}
    assert feature_data['type'] == 'Feature'
    assert feature_data['id'] == str(parking_area.id)

    geometry_data = feature_data['geometry']
    assert geometry_data.keys() == {'type', 'coordinates'}
    assert geometry_data['type'] == 'MultiPolygon'
    assert len(geometry_data['coordinates']) > 0

    properties_data = feature_data['properties']
    assert properties_data.keys() == {'capacity_estimate'}
    assert properties_data['capacity_estimate'] == parking_area.capacity_estimate


def test_bounding_box_filter(api_client, parking_area_factory):
    polygon_1 = Polygon([[10, 40], [20, 40], [20, 50], [10, 50], [10, 40]], srid=4326).transform(3879, clone=True)
    polygon_2 = Polygon([[30, 50], [40, 50], [40, 60], [30, 60], [30, 50]], srid=4326).transform(3879, clone=True)

    area_1 = parking_area_factory(geom=MultiPolygon(polygon_1))
    area_2 = parking_area_factory(geom=MultiPolygon(polygon_2))

    data = get(api_client, list_url)
    assert data['count'] == 2
    assert get_ids_from_results(data['features']) == {area_1.id, area_2.id}

    data = get(api_client, list_url + '?in_bbox=5,5,85,85')
    assert data['count'] == 2
    assert get_ids_from_results(data['features']) == {area_1.id, area_2.id}

    data = get(api_client, list_url + '?in_bbox=5,35,25,55')
    assert data['count'] == 1
    assert get_ids_from_results(data['features']) == {area_1.id}

    data = get(api_client, list_url + '?in_bbox=80,80,85,85')
    assert data['count'] == 0
