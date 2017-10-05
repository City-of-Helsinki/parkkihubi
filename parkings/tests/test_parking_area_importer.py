import os

from lxml import etree

from parkings.importers import ParkingAreaImporter

mydir = os.path.dirname(__file__)


def test_parking_area_importer():
    filename = os.path.join(mydir, 'parking_area_importer_data.xml')
    root = etree.fromstring(open(filename, 'r', encoding='utf8').read())
    importer = ParkingAreaImporter()
    members = importer._separate_members(root)
    area = importer._parse_member(members[0])

    assert area['origin_id'] == '3508'
    assert area['capacity_estimate'] == 2
    assert area['geom'].wkt == (
        'MULTIPOLYGON (((6673221.131005 25497165.701059, 6673221.211415 '
        '25497167.810273, 6673233.337525 25497167.006736, 6673233.1924 '
        '25497165.052488, 6673221.131005 25497165.701059)))'
    )
