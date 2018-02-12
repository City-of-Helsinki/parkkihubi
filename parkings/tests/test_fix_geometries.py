import os

import pytest
from django.core import management

from parkings.management.commands import fix_geometries

from ..models import ParkingArea
from .utils import call_mgmt_cmd_with_output

directory = os.path.abspath(os.path.dirname(__file__))

parking_areas_yaml = os.path.join(directory, 'invalid_geom_parking_areas.yaml')


def test_non_compatible_model():
    with pytest.raises(SystemExit) as excinfo:
        call_the_command('Operator')
    assert str(excinfo.value) == (
        'Model should have exactly one MultiPolygon field')


@pytest.mark.django_db
@pytest.mark.parametrize('verbosity', [0, 1, 2])
@pytest.mark.parametrize('dry_run', [False, True])
def test_fixing(verbosity, dry_run):
    # Load the test data and collect its timestamps and area sizes
    management.call_command('loaddata', parking_areas_yaml)
    timestamps_before = sorted(
        ParkingArea.objects.values_list('modified_at', flat=True))
    areas_before = get_areas(ParkingArea.objects.all())

    # Call the command
    (stdout, stderr) = call_the_command(
        'ParkingArea', verbosity=verbosity, dry_run=dry_run)

    # Check the output
    assert stdout == get_expected_output(verbosity, dry_run)
    assert stderr == ''

    # Check that it did changes as expected
    timestamps_after = sorted(
        ParkingArea.objects.values_list('modified_at', flat=True))
    if dry_run:
        assert timestamps_after == timestamps_before
    else:
        assert timestamps_after != timestamps_before

    areas_after = get_areas(ParkingArea.objects.all())
    assert areas_after == areas_before, "Areas sizes (m^2) shouldn't change"

    # Make sure that after the command is run, there is no more invalid
    # geometries
    if not dry_run:
        assert call_the_command('ParkingArea', dry_run=True)[0] == (
            'All good. Nothing to fix.\n')


def get_areas(objects):
    """
    Get rounded area sizes (in m^2) of the geometries in given objects.

    The results are rounded to two digits (dm^2 if the unit is metre)
    and converted to string to allow easy comparison with equals.
    """
    return {str(obj): '{:.2f}'.format(obj.geom.area) for obj in objects}


def get_expected_output(verbosity, dry_run):
    lines = [
        ('Doing geom of ParkingArea:a0000000-d493-4670-a1de-f752fd694ed4 '
         '/ Parking Area 2833', 1),
        ('  original geometry: SRID=3879;MULTIPOLYGON (((...)), ((...)))', 2),
        ('  after MakeValid:   SRID=3879;MULTIPOLYGON (((...)), ((...)))', 2),
        ('  after conversion:  SRID=3879;MULTIPOLYGON (((...)), ((...)))', 2),
        ('  Fixed.', 1),

        ('Doing geom of ParkingArea:b0000000-0a2f-4acf-a89d-0c89eb3a0d1b '
         '/ Parking Area 3066', 1),
        ('  original geometry: SRID=3879;MULTIPOLYGON '
         '(((...)), ((...)), ((...)), ((...)), ((...)))', 2),
        ('  after MakeValid:   SRID=3879;GEOMETRYCOLLECTION '
         '(MULTIPOLYGON (((...)), ((...)), ((...))),'
         ' MULTILINESTRING ((...), (...)))', 2),
        ('  after conversion:  SRID=3879;MULTIPOLYGON '
         '(((...)), ((...)), ((...)))', 2),
        ('  Fixed.', 1),

        ('Doing geom of ParkingArea:c0000000-7713-48d5-82f5-920dfe2a61d7 '
         '/ Parking Area 3331', 1),
        ('  original geometry: SRID=3879;MULTIPOLYGON '
         '(((...)), ((...)), ((...)))', 2),
        ('  after MakeValid:   SRID=3879;GEOMETRYCOLLECTION '
         '(MULTIPOLYGON (((...)), ((...))), LINESTRING (...))', 2),
        ('  after conversion:  SRID=3879;MULTIPOLYGON (((...)), ((...)))', 2),
        ('  Fixed.', 1),

        ('Doing geom of ParkingArea:d0000000-a225-4542-a7d4-58196cd82d19 '
         '/ Parking Area 3652', 1),
        ('  original geometry: SRID=3879;MULTIPOLYGON (((...)), ((...)))', 2),
        ('  after MakeValid:   SRID=3879;GEOMETRYCOLLECTION '
         '(POLYGON ((...)), MULTILINESTRING ((...), (...)))', 2),
        ('  after conversion:  SRID=3879;MULTIPOLYGON (((...)))', 2),
        ('  Fixed.', 1),

        ('Doing geom of ParkingArea:e0000000-c039-462b-9680-798e4fe9d7e4 '
         '/ Parking Area 4396', 1),
        ('  original geometry: SRID=3879;MULTIPOLYGON (((...)), ((...)))', 2),
        ('  after MakeValid:   SRID=3879;GEOMETRYCOLLECTION '
         '(POLYGON ((...)), LINESTRING (...))', 2),
        ('  after conversion:  SRID=3879;MULTIPOLYGON (((...)))', 2),
        ('  Fixed.', 1),

        ('Doing geom of ParkingArea:f0000000-28b8-4710-a203-8dd3c597b936 '
         '/ Parking Area 4542', 1),
        ('  original geometry: SRID=3879;MULTIPOLYGON '
         '(((...)), ((...)), ((...)), ((...)), ((...)))', 2),
        ('  after MakeValid:   SRID=3879;GEOMETRYCOLLECTION '
         '(MULTIPOLYGON (((...)), ((...)), ((...)), ((...))), '
         'LINESTRING (...))', 2),
        ('  after conversion:  SRID=3879;MULTIPOLYGON '
         '(((...)), ((...)), ((...)), ((...)))', 2),
        ('  Fixed.', 1),
    ]
    text = ''.join(line + '\n' for (line, lvl) in lines if lvl <= verbosity)
    if dry_run:
        return text.replace('Fixed.', 'Not saved, since doing dry-run.')
    return text


@pytest.mark.django_db
def test_nothing_to_fix(parking_area):
    (stdout, stderr) = call_the_command('ParkingArea')
    assert stdout == 'All good. Nothing to fix.\n'
    assert stderr == ''


def call_the_command(*args, **kwargs):
    (result, stdout, stderr) = call_mgmt_cmd_with_output(
        fix_geometries.Command, *args, **kwargs)
    assert result is None
    return (stdout, stderr)
