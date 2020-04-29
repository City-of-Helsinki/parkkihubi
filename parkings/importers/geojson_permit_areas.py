import logging
import os

from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import PermitArea
from .geojson_importer import GeoJsonImporter

logger = logging.getLogger(__name__)
mydir = os.path.dirname(__file__)


class PermitAreaImporter(GeoJsonImporter):
    """
    Imports permit area data
    """

    def import_permit_areas(self, geojson_file_path, permitted_user):
        permit_area_dicts = self.read_and_parse(geojson_file_path)
        count = self._save_permit_areas(permit_area_dicts, permitted_user)
        logger.info('Created or updated {} permit areas'.format(count))

    @transaction.atomic
    def _save_permit_areas(self, permit_areas_dict, permitted_user):
        logger.info('Saving permit areas.')
        user = get_user_model().objects.filter(username=permitted_user).get()
        default_domain = self.get_default_domain()
        count = 0
        permit_area_ids = []
        for area_dict in permit_areas_dict:
            domain = area_dict.pop('domain', default_domain)
            area_dict.setdefault('permitted_user', user)
            permit_area, _ = PermitArea.objects.update_or_create(
                identifier=area_dict['identifier'],
                domain=domain,
                defaults=area_dict)
            permit_area_ids.append(permit_area.pk)
            count += 1
        return count
