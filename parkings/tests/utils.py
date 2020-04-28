import io
from decimal import Decimal
from uuid import UUID

import pytest
from django.core import management

from parkings.factories import ParkingFactory, RegionFactory
from parkings.models import EnforcementDomain


def approx(x, **kwargs):
    if isinstance(x, float):
        return pytest.approx(x, **kwargs)
    elif x is None or isinstance(x, (str, bytes, UUID, int, Decimal)):
        return x
    elif callable(getattr(x, 'items', None)):
        return type(x)(
            (key, approx(value, **kwargs))
            for (key, value) in x.items())
    else:
        return type(x)(approx(item, **kwargs) for item in x)


def call_mgmt_cmd_with_output(command_cls, *args, **kwargs):
    assert issubclass(command_cls, management.BaseCommand)
    stdout = io.StringIO()
    stderr = io.StringIO()
    cmd = command_cls(stdout=stdout, stderr=stderr)
    assert isinstance(cmd, management.BaseCommand)
    result = management.call_command(cmd, *args, **kwargs)
    return (result, stdout.getvalue(), stderr.getvalue())


def create_parkings_and_regions(parking_count=100, region_count=20):
    domain = EnforcementDomain.get_default_domain()
    regions = RegionFactory.create_batch(region_count, domain=domain)
    parkings = ParkingFactory.create_batch(parking_count, domain=domain)

    centroids = [region.geom.centroid for region in regions]
    touching_points = [p for p in centroids if intersects_with_any(p, regions)]

    # Make sure that some of the parkings are inside the regions
    for (point, parking) in zip(touching_points, parkings):
        parking.location = point
        parking.save()

    for parking in parkings:  # pragma: no cover
        if intersects_with_any(parking.location, regions):
            assert parking.region
            assert intersects(parking.location, parking.region)
        else:
            assert parking.region is None

    return (parkings, regions)


def intersects_with_any(point, regions):
    assert regions
    p = point.transform(regions[0].geom.srid, clone=True)
    assert all(x.geom.srid == p.srid for x in regions)
    return any(p.intersects(x.geom) for x in regions)


def intersects(point, region):
    geom = region.geom
    return point.transform(geom.srid, clone=True).intersects(geom)
