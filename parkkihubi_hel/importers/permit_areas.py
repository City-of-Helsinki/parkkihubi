import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from parkings.models import EnforcementDomain, PermitArea

from .wfs_importer import WfsImporter

logger = logging.getLogger(__name__)


class PermitAreaImporter(WfsImporter):
    """
    Imports permit area data from kartta.hel.fi.
    """
    wfs_typename = 'Asukas_ja_yrityspysakointivyohykkeet_alue'

    def import_permit_areas(self, allowed_user=None):
        permit_area_dicts = self.download_and_parse()
        count = self._save_permit_areas(permit_area_dicts, allowed_user)
        logger.info('Created or updated {} permit areas'.format(count))

    @transaction.atomic
    def _save_permit_areas(self, permit_areas_dict, allowed_user=None):
        logger.info('Saving permit areas.')
        count = 0
        permit_area_ids = []
        if allowed_user is not None:
            user = get_user_model().objects.filter(username=allowed_user).get()
        else:
            user = None
        for area_dict in permit_areas_dict:
            permit_area, _ = PermitArea.objects.update_or_create(
                domain=EnforcementDomain.get_default_domain(),
                identifier=area_dict['identifier'],
                defaults=area_dict)
            if user is not None:
                permit_area.allowed_users.add(user)
            permit_area_ids.append(permit_area.pk)
            count += 1
        PermitArea.objects.exclude(pk__in=permit_area_ids).delete()
        return count

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
