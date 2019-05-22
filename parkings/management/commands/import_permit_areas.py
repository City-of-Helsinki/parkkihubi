import json
import logging

import requests
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from ...models import PermitArea

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _("Import the parking permit areas.")
    tile_combinations = ((20, 118), (20, 119), (21, 118), (21, 119))
    created = 0

    def handle(self, *args, **options):
        PermitArea.objects.all().delete()

        for x, y in self.tile_combinations:
            url = '''
                https://kartta.hel.fi/maps/featureloader.ashx?request=tile&x={}&y={}&z=0&options=%5B%7B%22id%22%3A%22MAKA_Asukaspysakointivyohykkeet%22%2C%22params%22%3A%22%7B%7D%22%2C%22where%22%3A%22%22%2C%22showNames%22%3Afalse%2C%22maxFeatures%22%3A50000%2C%22simplify%22%3Atrue%7D%5D&capfeatures=true
            '''.format(x, y)
            response = requests.get(url)
            assert response.status_code == 200
            json_resp = json.loads(response.content)

            for item in json_resp[0]['features']:
                name = item['properties']['alueen_nimi']
                identifier = item['properties']['asukaspysakointitunnus']
                points = []

                for coordinate in item['geometry']['coordinates'][0]:
                    lat, lng = coordinate
                    points.append(Point(float(lat), float(lng)))
                polygons = Polygon(points)
                permit_area_data = {
                    'name': name,
                    'identifier': identifier,
                    'geom': MultiPolygon(polygons)
                }
                self._create_parking_zone(permit_area_data)

        logger.info('Created %s parking zones' % self.created)

    @transaction.atomic
    def _create_parking_zone(self, permit_area_data):
        if not PermitArea.objects.filter(
            name=permit_area_data['name'],
            identifier=permit_area_data['identifier']
        ).exists():
            PermitArea.objects.create(**permit_area_data)
            self.created += 1
