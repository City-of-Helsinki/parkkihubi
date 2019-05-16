import io

import pytz
from django.core import management

from parkings.factories import ParkingFactory, RegionFactory
from parkings.factories.faker import fake


def call_mgmt_cmd_with_output(command_cls, *args, **kwargs):
    assert issubclass(command_cls, management.BaseCommand)
    stdout = io.StringIO()
    stderr = io.StringIO()
    cmd = command_cls(stdout=stdout, stderr=stderr)
    assert isinstance(cmd, management.BaseCommand)
    result = management.call_command(cmd, *args, **kwargs)
    return (result, stdout.getvalue(), stderr.getvalue())


def create_parkings_and_regions(parking_count=100, region_count=20):
    regions = RegionFactory.create_batch(region_count)
    parkings = ParkingFactory.create_batch(parking_count)

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


CAPITAL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'


def generate_registration_number():
    letters = ''.join(fake.random.choice(CAPITAL_LETTERS) for _ in range(3))
    numbers = ''.join(fake.random.choice('0123456789') for _ in range(3))
    return '%s-%s' % (letters, numbers)


def generate_subjects(count=1):
    subjects = []
    for c in range(count):
        subjects.append({
            'registration_number': generate_registration_number(),
            'start_time': str(fake.date_time_between(start_date='-2h', end_date='-1h', tzinfo=pytz.utc)),
            'end_time': str(fake.date_time_between(start_date='+1h', end_date='+2h', tzinfo=pytz.utc)),
        })
    return subjects


def generate_areas(count=1):
    areas = []
    for c in range(count):
        areas.append({
            'start_time': str(fake.date_time_between(start_date='-2h', end_date='-1h', tzinfo=pytz.utc)),
            'end_time': str(fake.date_time_between(start_date='+1h', end_date='+2h', tzinfo=pytz.utc)),
            'area': fake.random.choice(CAPITAL_LETTERS),
        })
    return areas


def generate_external_ids(id_length=11):
    external_id = ''.join(fake.random.choice('0123456789') for _ in range(id_length))
    return external_id


def generate_subjects_with_startdate_gt_endate(count=1):
    subjects = []
    for c in range(count):
        subjects.append({
            'registration_number': generate_registration_number(),
            'start_time': str(fake.date_time_between(start_date='+1h', end_date='+2h', tzinfo=pytz.utc)),
            'end_time': str(fake.date_time_between(start_date='-2h', end_date='-1h', tzinfo=pytz.utc)),
        })
    return subjects


def generate_areas_with_startdate_gt_endate(count=1):
    areas = []
    for c in range(count):
        areas.append({
            'start_time': str(fake.date_time_between(start_date='+1h', end_date='+2h', tzinfo=pytz.utc)),
            'end_time': str(fake.date_time_between(start_date='-2h', end_date='-1h', tzinfo=pytz.utc)),
            'area': fake.random.choice(CAPITAL_LETTERS),
        })
    return areas
