import json
import logging

import requests
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from ...models import PaymentZone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _("Import the parking payment zones.")
    created = 0
    URL = '''
        https://kartta.hel.fi/maps/featureloader.ashx?request=tile&x=41&y=237&z=1&options=%5B%7B%22id%22%3A%22PostGIS_MAKA_pysakoinnin_maksuvyohykkeet%22%2C%22params%22%3A%22%7B%7D%22%2C%22where%22%3A%22%22%2C%22showNames%22%3Afalse%2C%22maxFeatures%22%3A50000%2C%22simplify%22%3Atrue%7D%5D&capfeatures=true
    '''

    def handle(self, *args, **options):
        PaymentZone.objects.all().delete()
        resp = requests.get(self.URL)
        assert resp.status_code == 200
        json_resp = json.loads(resp.content)

        for payment_zone in json_resp[0]['features']:
            number = payment_zone['properties']['vyohykkeen_nro']
            name = payment_zone['properties']['nimi']
            points = []

            for coordinate in payment_zone['geometry']['coordinates'][0]:
                lat, lng = coordinate
                points.append(Point(float(lat), float(lng)))

            polygons = Polygon(points)
            payment_zone_data = {
                'name': name,
                'number': number,
                'geom': MultiPolygon(polygons)
            }
            self._create_payment_zone(payment_zone_data)

        logger.info('Created %s payment zones' % self.created)

    @transaction.atomic
    def _create_payment_zone(self, payment_zone_data):
        if not PaymentZone.objects.filter(
            name=payment_zone_data['name'],
            number=payment_zone_data['number']
        ).exists():
            PaymentZone.objects.create(**payment_zone_data)
            self.created += 1
