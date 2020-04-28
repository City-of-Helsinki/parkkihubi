from collections import OrderedDict

import pytz
from django.urls import reverse
from rest_framework import status

from parkings.factories.faker import fake

from ...utils import create_parkings_and_regions, intersects

list_url = reverse('monitoring:v1:regionstatistics-list')


def test_empty(monitoring_api_client):
    result = monitoring_api_client.get(list_url)
    assert result.data == {
        'count': 0,
        'next': None,
        'previous': None,
        'results': [],
    }
    assert result.status_code == status.HTTP_200_OK


def test_with_single_parking(monitoring_api_client, region, parking):
    region.domain = monitoring_api_client.monitor.domain
    region.save()

    point_in_region = region.geom.centroid
    parking.location = point_in_region
    parking.domain = region.domain
    parking.save()
    assert intersects(point_in_region, region)

    result = monitoring_api_client.get(list_url)
    assert result.data == {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [
            OrderedDict([
                ('id', str(region.id)),
                ('parking_count', 1)]),
        ]
    }
    assert result.status_code == status.HTTP_200_OK


def test_with_many_parkings_and_specified_time(monitoring_api_client):
    (parkings, regions) = create_parkings_and_regions(
        parking_count=20, region_count=5)

    monitoring_api_client.monitor.domain = parkings[0].domain
    monitoring_api_client.monitor.save()

    # Select a parking with a region and is not ending first
    earliest_end_time = min(x.time_end for x in parkings if x.region)
    parking = [
        parking for parking in parkings
        if parking.region and parking.time_end > earliest_end_time][0]

    # Pick a point in time when at least the selected parking is valid
    time = fake.date_time_between(parking.time_start, parking.time_end,
                                  tzinfo=pytz.utc)

    # Calculate some lookup containers
    valid_parkings_at_time = [
        parking for parking in parkings
        if parking.time_start <= time and (parking.time_end is None
                                           or parking.time_end >= time)]
    regions_with_valid_parkings = {
        parking.region for parking in valid_parkings_at_time
        if parking.region
    }
    regions_by_id = {str(region.id): region for region in regions}

    # Do the API call
    api_result = monitoring_api_client.get(list_url, {'time': str(time)})

    # Check the results
    results = api_result.data.pop('results', None)
    assert api_result.data == {
        'count': len(regions_with_valid_parkings),
        'next': None,  # No paging, since parking count < page size
        'previous': None,
    }
    assert len(results) == len(regions_with_valid_parkings)
    for result in results:
        assert isinstance(result, OrderedDict)
        assert set(result.keys()) == {'id', 'parking_count'}
        assert result['id'] in regions_by_id
        region = regions_by_id[result['id']]
        expected_count = sum(
            1 for parking in valid_parkings_at_time
            if parking.region == region)
        assert result['parking_count'] == expected_count
    assert api_result.status_code == status.HTTP_200_OK


def test_monitor_can_view_data_only_from_their_domain(monitoring_api_client, region, parking):
    region.domain = monitoring_api_client.monitor.domain
    region.save()

    point_in_region = region.geom.centroid
    parking.location = point_in_region
    assert parking.domain != region.domain
    result = monitoring_api_client.get(list_url)
    assert result.data['count'] == 0

    parking.domain = region.domain
    parking.save()
    result = monitoring_api_client.get(list_url)
    assert result.data['count'] == 1
    assert result.data['results'][0]['id'] == str(region.id)
