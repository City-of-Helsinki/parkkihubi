import logging

from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from lxml import etree
from owslib.wfs import WebFeatureService

logger = logging.getLogger(__name__)


class BaseImporterMixin(object):
    def __init__(self, overwrite=False):
        self.ns = {
            'wfs': 'http://www.opengis.net/wfs/2.0',
            'avoindata': 'https://www.hel.fi/avoindata',
            'gml': 'http://www.opengis.net/gml/3.2',
        }
        self.created = 0
        self.overwrite = overwrite

    def _download(self, typename):
        logger.info('Getting data from the server.')

        try:
            wfs = WebFeatureService(
                url='https://kartta.hel.fi/ws/geoserver/avoindata/wfs',
                version='2.0.0',
            )
            response = wfs.getfeature(
                typename=typename,
            )
            return etree.fromstring(bytes(response.getvalue(), 'UTF-8'))
        except Exception:
            logger.error('Unable to get data from the server.', exc_info=True)

    def get_polygons(self, geom):
        """
        Turns the XML containing coordinates into a multipolygon
        """
        polygons = []

        for pos in geom.iter('*'):
            # get leaf nodes. Treat LinearRing and MultiSurface the same way
            if len(pos) == 0:
                positions = list(filter(None, pos.text.split(' ')))
                points = []
                points_as_pairs = zip(positions[1::2], positions[::2])
                for latitude, longitude in points_as_pairs:
                    points.append(Point(float(latitude), float(longitude)))
                polygons.append(Polygon(points))

        return MultiPolygon(polygons)

    def _parse_data(self, root):
        members = self._separate_members(root)
        logger.info('Parsing Data.')
        parsed_members = map(self._parse_member, members)

        return parsed_members

    def _separate_members(self, xml_tree):
        members = xml_tree.findall('wfs:member', self.ns)
        return members
