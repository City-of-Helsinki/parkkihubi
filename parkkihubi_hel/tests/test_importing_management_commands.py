import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from parkings.models import ParkingArea, PaymentZone, PermitArea

from ..management.commands import (
    import_parking_areas, import_payment_zones, import_permit_areas)
from .request_mocking import mocked_requests


@pytest.mark.django_db
def test_import_parking_areas():
    with mocked_requests():

        call_command(import_parking_areas.Command())

    assert ParkingArea.objects.count() == 1


@pytest.mark.django_db
def test_import_payment_zones():
    with mocked_requests():

        call_command(import_payment_zones.Command())

    assert PaymentZone.objects.count() == 1


@pytest.mark.django_db
def test_permit_area_importer():
    with mocked_requests():
        test_user = get_user_model().objects.create(username='TEST_USER', is_staff=True)
        call_command(import_permit_areas.Command(), test_user.username)

    assert PermitArea.objects.count() == 1
