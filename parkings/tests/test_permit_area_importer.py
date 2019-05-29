import os

from lxml import etree

from parkings.importers import PermitAreaImporter

mydir = os.path.dirname(__file__)


def test_permit_area_importer():
    filename = os.path.join(mydir, 'permit_area_importer_data.xml')
    root = etree.fromstring(open(filename, 'r', encoding='utf8').read())
    importer = PermitAreaImporter()
    members = importer._separate_members(root)
    permit_area = importer._parse_member(members[0])

    assert permit_area['name'] == 'Kamppi'
    assert permit_area['identifier'] == 'A'
    assert permit_area['geom'].wkt == (
        'MULTIPOLYGON (((6673221.131005 25497165.701059, 6673221.211415 '
        '25497167.810273, 6673233.337525 25497167.006736, 6673233.1924 '
        '25497165.052488, 6673221.131005 25497165.701059)))'
    )
