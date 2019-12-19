import os

import pytest
from django.core.management import call_command

from parkings.models import PaymentZone, PermitArea

from ..management.commands import (
    import_geojson_payment_zones, import_geojson_permit_areas)

mydir = os.path.dirname(__file__)
permit_areas = os.path.join(mydir, 'geojson_permit_areas_importer_data.geojson')
payment_zones = os.path.join(mydir, 'geojson_payment_zones_importer_data.geojson')


@pytest.mark.django_db
def test_import_payment_zones():
    call_command(import_geojson_payment_zones.Command(), payment_zones)

    assert PaymentZone.objects.count() == 1


@pytest.mark.django_db
def test_permit_area_importer():
    call_command(import_geojson_permit_areas.Command(), permit_areas)

    assert PermitArea.objects.count() == 1
