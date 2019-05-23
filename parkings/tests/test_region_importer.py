import os

import pytest

from parkings.importers.regions import ShapeFileToRegionImporter
from parkings.management.commands import import_regions
from parkings.models import Region

from .utils import call_mgmt_cmd_with_output

directory = os.path.abspath(os.path.dirname(__file__))

shp_path = os.path.join(directory, 'test-features.shp')


def test_get_layer_names():
    importer = ShapeFileToRegionImporter(shp_path)
    assert importer.get_layer_names() == ['test-features']


def test_get_layer_fields():
    importer = ShapeFileToRegionImporter(shp_path)
    assert importer.get_layer_fields('test-features') == [
        'Name', 'descriptio', 'timestamp', 'begin', 'end',
        'altitudeMo', 'tessellate', 'extrude', 'visibility',
        'drawOrder', 'icon', 'DisplayNam', 'year']


def test_get_layer_fields_invalid_layer_name():
    importer = ShapeFileToRegionImporter(shp_path)
    with pytest.raises(ValueError) as excinfo:
        importer.get_layer_fields('invalid-layer-name')
    assert str(excinfo.value) == "No such layer: 'invalid-layer-name'"


@pytest.mark.django_db
def test_import():
    assert Region.objects.count() == 0
    importer = ShapeFileToRegionImporter(shp_path)
    importer.set_field_mapping({'name': 'DisplayNam'})
    importer.import_from_layer('test-features')
    check_imported_regions()


@pytest.mark.django_db
def test_management_command():
    call_the_command(shp_path, 'test-features', name_field='DisplayNam')
    check_imported_regions()

    (stdout, stderr) = call_the_command(shp_path, 'LIST')
    assert stdout.splitlines() == [
        'test-features',
        ' - Name',
        ' - descriptio',
        ' - timestamp',
        ' - begin',
        ' - end',
        ' - altitudeMo',
        ' - tessellate',
        ' - extrude',
        ' - visibility',
        ' - drawOrder',
        ' - icon',
        ' - DisplayNam',
        ' - year']
    assert stdout.endswith('\n')
    assert stderr == ''


def call_the_command(*args, **kwargs):
    (result, stdout, stderr) = call_mgmt_cmd_with_output(
        import_regions.Command, *args, **kwargs)
    assert result is None
    return (stdout, stderr)


def check_imported_regions():
    assert Region.objects.count() == 2
    (reg1, reg2) = list(Region.objects.order_by('name'))
    assert reg1.name == 'Feature 1 - Center'
    assert reg2.name == 'Feature 2 - North'
    check_coords_equality(reg1.geom.coords, (((
        (25494876.99362251, 6677378.512999998),
        (25494929.966569535, 6677389.664999997),
        (25495159.757339746, 6677117.191999998),
        (25494819.72517978, 6677425.432),
        (25494876.99362251, 6677378.512999998),
    ),),), delta=0.0000001)
    check_coords_equality(reg2.geom.coords, (((
        (25494360.817638688, 6684192.751999998),
        (25494493.262506243, 6684249.482999996),
        (25494337.233162273, 6684151.803999996),
        (25494360.817638688, 6684192.751999998)
    ),),), delta=0.0000001)


def check_coords_equality(x1, x2, delta=0, pos=()):  # pragma: no cover
    at_pos = ' at position {}'.format(pos) if pos else ''
    if type(x1) != type(x2):
        raise ValueError('Type mismatch: {} vs {}{}'.format(
            type(x1), type(x2), at_pos))
    if isinstance(x1, (float, int)):
        diff = abs(x1 - x2)
        if diff > delta:
            raise ValueError(
                'Values differ too much {} vs {} (diff={}){}'.format(
                    x1, x2, diff, at_pos))
    elif len(x1) != len(x2):
        raise ValueError(
            'Length mismatch: {} vs {}{}'.format(
                len(x1), len(x2), at_pos))
    else:
        for (i, pair) in enumerate(zip(x1, x2)):
            (x1i, x2i) = pair
            check_coords_equality(x1i, x2i, delta, pos + (i,))
