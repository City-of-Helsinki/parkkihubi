import pytest
from django.core.management import call_command

from parkings.management.commands import (
    import_parking_areas, import_payment_zones, import_permit_areas)
from parkings.models import ParkingArea, PaymentZone, PermitArea

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

        call_command(import_permit_areas.Command())

    assert PermitArea.objects.count() == 1
