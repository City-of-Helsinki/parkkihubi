import os

from parkings.importers import PermitAreaImporter

mydir = os.path.dirname(__file__)


def test_permit_area_importer():
    filename = os.path.join(mydir, 'geojson_permit_areas_importer_data.geojson')
    importer = PermitAreaImporter()
    data = importer.read_and_parse(filename)
    permit_area = next(iter(data))

    assert permit_area['name'] == 'Asukaspysäköintialue A'
    assert permit_area['identifier'] == 1
    assert permit_area['geom'].wkt == (
        'MULTIPOLYGON (('
        '(102 2, 103 2, 103 3, 102 3, 102 2)),'
        ' ((100 0, 101 0, 101 1, 100 1, 100 0),'
        ' (100.2 0.2, 100.8 0.2, 100.8 0.8, 100.2 0.8, 100.2 0.2)))'
    )
