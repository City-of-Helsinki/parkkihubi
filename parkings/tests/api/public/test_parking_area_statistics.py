from unittest.mock import patch

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.urls import reverse

from parkings.models import Parking

from ..utils import (
    check_list_endpoint_base_fields, check_method_status_codes, get,
    get_ids_from_results)

list_url = reverse('public:v1:parkingareastatistics-list')


def get_detail_url(obj):
    return reverse('public:v1:parkingareastatistics-detail', kwargs={'pk': obj.pk})


def test_disallowed_methods(api_client, parking_area):
    disallowed_methods = ('post', 'put', 'patch', 'delete')
    urls = (list_url, get_detail_url(parking_area))
    check_method_status_codes(api_client, urls, disallowed_methods, 405)


def test_list_endpoint_base_fields(api_client):
    stats_data = get(api_client, list_url)
    check_list_endpoint_base_fields(stats_data)


def test_get_list_check_data(api_client, parking_factory, parking_area_factory, history_parking_factory):
    parking_area_1, parking_area_2, parking_area_3, parking_area_4 = parking_area_factory.create_batch(4)

    with patch.object(Parking, 'get_closest_area', return_value=parking_area_1):
        parking_factory.create_batch(4)

    with patch.object(Parking, 'get_closest_area', return_value=parking_area_2):
        parking_factory.create_batch(3)

    with patch.object(Parking, 'get_closest_area', return_value=parking_area_3):
        history_parking_factory.create_batch(5)

    with patch.object(Parking, 'get_closest_area', return_value=parking_area_4):
        history_parking_factory.create_batch(5, time_end=None)

    results = get(api_client, list_url)['results']
    assert len(results) == 4

    def find_by_obj_id(obj, iterable):
        return [x for x in iterable if x['id'] == str(obj.id)][0]

    stats_data_1 = find_by_obj_id(parking_area_1, results)
    stats_data_2 = find_by_obj_id(parking_area_2, results)
    stats_data_3 = find_by_obj_id(parking_area_3, results)
    stats_data_4 = find_by_obj_id(parking_area_4, results)

    assert stats_data_1.keys() == {'id', 'current_parking_count'}
    assert stats_data_1['current_parking_count'] == 4
    assert stats_data_2['current_parking_count'] == 0  # under 4
    assert stats_data_3['current_parking_count'] == 0  # not valid parkings currently
    assert stats_data_4['current_parking_count'] == 5  # no end time so valid


def test_get_detail_check_data(api_client, parking_factory, parking_area):
    with patch.object(Parking, 'get_closest_area', return_value=parking_area):
        parking_factory.create_batch(3)

    stats_data = get(api_client, get_detail_url(parking_area))
    assert stats_data.keys() == {'id', 'current_parking_count'}
    assert stats_data['current_parking_count'] == 0

    with patch.object(Parking, 'get_closest_area', return_value=parking_area):
        parking_factory()

    stats_data = get(api_client, get_detail_url(parking_area))
    assert stats_data['current_parking_count'] == 4


def test_bounding_box_filter(api_client, parking_area_factory):
    polygon_1 = Polygon([[10, 40], [20, 40], [20, 50], [10, 50], [10, 40]], srid=4326).transform(3879, clone=True)
    polygon_2 = Polygon([[30, 50], [40, 50], [40, 60], [30, 60], [30, 50]], srid=4326).transform(3879, clone=True)

    area_1 = parking_area_factory(geom=MultiPolygon(polygon_1))
    area_2 = parking_area_factory(geom=MultiPolygon(polygon_2))

    data = get(api_client, list_url)
    assert len(data['results']) == 2
    assert get_ids_from_results(data['results']) == {area_1.id, area_2.id}

    data = get(api_client, list_url + '?in_bbox=5,5,85,85')
    assert len(data['results']) == 2

    data = get(api_client, list_url + '?in_bbox=5,35,25,55')
    assert len(data['results']) == 1
    assert get_ids_from_results(data['results']) == {area_1.id}

    data = get(api_client, list_url + '?in_bbox=80,80,85,85')
    assert len(data['results']) == 0
