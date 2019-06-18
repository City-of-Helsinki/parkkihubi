import os

from lxml import etree

from parkings.importers import PaymentZoneImporter

mydir = os.path.dirname(__file__)


def test_payment_zone_importer():
    filename = os.path.join(mydir, 'payment_zone_importer_data.xml')
    root = etree.fromstring(open(filename, 'r', encoding='utf8').read())
    importer = PaymentZoneImporter()
    members = importer._separate_members(root)
    payment_zone = importer._parse_member(members[0])

    assert payment_zone['name'] == 'Maksuvyöhyke 1'
    assert payment_zone['number'] == '1'
    assert payment_zone['geom'].wkt == (
        'MULTIPOLYGON (((6673221.131005 25497165.701059, 6673221.211415 '
        '25497167.810273, 6673233.337525 25497167.006736, 6673233.1924 '
        '25497165.052488, 6673221.131005 25497165.701059)))'
    )
