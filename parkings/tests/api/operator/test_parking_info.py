import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse

from parkings.models import ParkingTerminal, PaymentZone
from parkings.tests.api.enforcement.test_check_parking import create_area_geom
from parkings.tests.api.utils import post

PARKING_INFO_POST_URL = reverse('operator:v1:parking_info_query')
POINT_Y = 60.200
POINT_X = 24.900


def test_parking_info_with_terminal_number(operator_api_client):
    setup_terminal()

    post_data = {
        'terminal_number': 4567
    }

    response = post(
        api_client=operator_api_client,
        url=PARKING_INFO_POST_URL,
        data=post_data,
        status_code=200)

    assert response == get_expected_response()


@pytest.mark.parametrize('coordinates, terminal_found', [
    ([24.8998, 60.1999], True),   # 15.68 metres from terminal.
    ([24.8999, 60.1992], True),   # 89.13 metres from terminal.
    ([24.8999, 60.1991], False),  # 100.23 metres from terminal.
    ([24.8999, 60.1990], False),  # 111.33 metres from terminal.
])
def test_parking_info_with_location(operator_api_client, coordinates, terminal_found):
    """
    Closest terminal within 100m should be returned from location coordinates provided.
    """
    setup_terminal()

    post_data = {
        'location': {
            'type': 'Point',
            'coordinates': coordinates,
        }
    }

    response = post(
        api_client=operator_api_client,
        url=PARKING_INFO_POST_URL,
        data=post_data,
        status_code=200 if terminal_found else 404)

    if terminal_found:
        assert response == get_expected_response()
    else:
        assert response == {'detail': 'No terminal was found.'}


def test_parking_info_with_terminal_num_and_location(operator_api_client):
    """
    Test posting with both location and terminal number. Terminal number should have
    precedence over location.
    """
    setup_terminal()

    post_data = {
        'terminal_number': 4567,
        'location': {
            'type': 'Point',
            'coordinates': [24.8999, 60.1991],  # Coordinates would in this case return not found.
        }
    }

    response = post(
        api_client=operator_api_client,
        url=PARKING_INFO_POST_URL,
        data=post_data,
        status_code=200)

    assert response == get_expected_response()


def test_parking_info_empty_post_data(operator_api_client):
    setup_terminal()

    post_data = {}

    response = post(
        api_client=operator_api_client,
        url=PARKING_INFO_POST_URL,
        data=post_data,
        status_code=400)

    assert response == {'detail': 'No search parameters entered.'}


def get_or_create_terminal(point_x=POINT_X, point_y=POINT_Y):
    return ParkingTerminal.objects.get_or_create(
        number=4567,
        defaults={
            'location': Point(point_x, point_y),
            'name': "Test terminal"
        })[0]


def get_or_create_payment_zone(area):
    return PaymentZone.objects.get_or_create(
        number=1,
        name="Maksuvyöhyke 1",
        geom=area)[0]


def get_expected_response():
    return {
        'location': {
            'latitude': POINT_Y,
            'longitude': POINT_X,
        },
        'zone': 1,
        'terminal_number': '4567',
        'rules': [
            {
                'after': '1970-01-01T00:00:00Z',
                'policy': 'unknown',
                'maximum_duration': 60,
            }
        ]
    }


def setup_terminal():
    area = create_area_geom()
    get_or_create_payment_zone(area)
    get_or_create_terminal()
