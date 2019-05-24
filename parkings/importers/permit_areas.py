import logging

from django.db import transaction
from lxml import etree
from owslib.wfs import WebFeatureService

from parkings.models import PermitArea

from .utils import get_polygons

logger = logging.getLogger(__name__)


class PermitAreaImporter(object):

    """
    Imports permit area data from kartta.hel.fi.
    """

    def __init__(self, overwrite=False):
        self.ns = {
            'wfs': 'http://www.opengis.net/wfs/2.0',
            'avoindata': 'https://www.hel.fi/avoindata',
            'gml': 'http://www.opengis.net/gml/3.2',
        }
        self.created = 0

    def import_permit_areas(self):
        response = self._download()
        permit_areas_dict = None

        if response is not None:
            permit_areas_dict = self._parse_permit_areas(response)
        else:
            logger.error("Download failed.")
            return False

        if permit_areas_dict is not None:
            self._save_permit_areas(permit_areas_dict)

        if self.created:
            logger.info('Created %s new permit areas.' % self.created)

    @transaction.atomic
    def _save_permit_areas(self, permit_areas_dict):
        logger.info('Saving permit areas.')

        permit_area_ids = []
        for area_dict in permit_areas_dict:
            permit_area, _ = PermitArea.objects.update_or_create(
                identifier=area_dict['identifier'],
                defaults=area_dict)
            permit_area_ids.append(permit_area.pk)
            self.created += 1
        PermitArea.objects.exclude(pk__in=permit_area_ids).delete()

    def _parse_permit_areas(self, root):
        members = self._separate_members(root)
        logger.info('Parsing permit areas.')
        parsed_members = []

        for index, member in enumerate(members):
            parsed_members.append(self._parse_member(member))

        return parsed_members

    def _download(self):
        logger.info('Getting data from the server.')

        try:
            wfs = WebFeatureService(
                url='https://kartta.hel.fi/ws/geoserver/avoindata/wfs',
                version='2.0.0',
            )
            response = wfs.getfeature(
                typename='Asukas_ja_yrityspysakointivyohykkeet_alue',
            )
            return etree.fromstring(bytes(response.getvalue(), 'UTF-8'))
        except Exception:
            logger.error('Unable to get data from the server.', exc_info=True)

    def _parse_member(self, member):
        data = member.find(
            'avoindata:Asukas_ja_yrityspysakointivyohykkeet_alue',
            self.ns,
        )
        identifier = data.find('avoindata:asukaspysakointitunnus', self.ns).text
        name = data.find('avoindata:alueen_nimi', self.ns).text
        geom = get_polygons(data.find('avoindata:geom', self.ns))

        return {
            'name': name,
            'identifier': identifier,
            'geom': geom,
        }

    def _separate_members(self, xml_tree):
        members = xml_tree.findall('wfs:member', self.ns)
        return members
