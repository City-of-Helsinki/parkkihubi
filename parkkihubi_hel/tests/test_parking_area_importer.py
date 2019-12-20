import os

from ..importers import ParkingAreaImporter

mydir = os.path.dirname(__file__)
sample_xml_file = os.path.join(mydir, 'parking_area_importer_data.xml')


def test_parse_response():
    importer = ParkingAreaImporter()
    with open(sample_xml_file, 'rb') as fp:
        data = importer._parse_response(fp.read())
    area = next(iter(data))

    assert area['origin_id'] == '3508'
    assert area['capacity_estimate'] == 2
    assert area['geom'].wkt == (
        'MULTIPOLYGON (((6673221.131005 25497165.701059, 6673221.211415 '
        '25497167.810273, 6673233.337525 25497167.006736, 6673233.1924 '
        '25497165.052488, 6673221.131005 25497165.701059)))'
    )
