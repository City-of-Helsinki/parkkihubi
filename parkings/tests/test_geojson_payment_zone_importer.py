import os

from parkings.importers import PaymentZoneImporter

mydir = os.path.dirname(__file__)


def test_payment_zone_importer():
    filename = os.path.join(mydir, 'geojson_payment_zones_importer_data.geojson')
    importer = PaymentZoneImporter()
    data = importer.read_and_parse(filename)
    payment_zone = next(iter(data))

    assert payment_zone['name'] == "Zone 1"
    assert payment_zone['number'] == 0
    assert payment_zone['geom'].wkt == (
        'MULTIPOLYGON (('
        '(-47.900390625 -14.94478487508837, -51.591796875 -19.91138351415555, -41.11083984375'
        ' -21.30984614108719, -43.39599609375 -15.3901357153052, -47.900390625 -14.94478487508837), '
        '(-46.6259765625 -17.14079039331664, -47.548828125 -16.80454107638345, -46.23046874999999'
        ' -16.69934023459454, -45.3515625 -19.31114335506464, -46.6259765625 -17.14079039331664), '
        '(-44.40673828125 -18.37537909403182, -44.4287109375 -20.09720622708389, -42.9345703125'
        ' -18.97902595325527, -43.52783203125 -17.60213912335084, -44.40673828125 -18.37537909403182)))'
    )
