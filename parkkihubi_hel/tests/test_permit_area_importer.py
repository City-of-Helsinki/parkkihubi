import os

from ..importers import PermitAreaImporter

mydir = os.path.dirname(__file__)


def test_permit_area_importer():
    filename = os.path.join(mydir, 'permit_area_importer_data.xml')
    importer = PermitAreaImporter()
    with open(filename, 'rb') as fp:
        data = importer._parse_response(fp.read())
    permit_area = next(iter(data))

    assert permit_area['name'] == 'Kamppi'
    assert permit_area['identifier'] == 'A'
    assert permit_area['geom'].wkt == (
        'MULTIPOLYGON (((6673221.131005 25497165.701059, 6673221.211415 '
        '25497167.810273, 6673233.337525 25497167.006736, 6673233.1924 '
        '25497165.052488, 6673221.131005 25497165.701059)))'
    )
