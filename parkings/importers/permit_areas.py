import logging

from django.db import transaction

from parkings.models import PermitArea

from .utils import BaseImporterMixin

logger = logging.getLogger(__name__)


class PermitAreaImporter(BaseImporterMixin):

    """
    Imports permit area data from kartta.hel.fi.
    """

    def __init__(self, overwrite=False):
        super().__init__(overwrite=overwrite)
        self.typename = 'Asukas_ja_yrityspysakointivyohykkeet_alue'

    def import_permit_areas(self):
        response = self._download(self.typename)
        permit_areas_dict = None

        if response is not None:
            permit_areas_dict = self._parse_data(response)
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

    def _parse_member(self, member):
        data = member.find(
            'avoindata:Asukas_ja_yrityspysakointivyohykkeet_alue',
            self.ns,
        )
        identifier = data.find('avoindata:asukaspysakointitunnus', self.ns).text
        name = data.find('avoindata:alueen_nimi', self.ns).text
        geom = self.get_polygons(data.find('avoindata:geom', self.ns))

        return {
            'name': name,
            'identifier': identifier,
            'geom': geom,
        }
