import logging
import time

from django.db import transaction

from parkings.models import EnforcementDomain, ParkingArea

from .geojson_importer import GeoJsonImporter

LOG = logging.getLogger(__name__)


class ParkingAreaImporter(GeoJsonImporter):
    def __init__(self, file_path, overwrite=False):
        self.file_path = file_path
        self.overwrite = overwrite
        self.refusals = 0
        self.overwrites = 0
        self.created = 0
        self.srid = None

    def import_areas(self):
        start = time.time()

        area_dicts = self.read_and_parse(self.file_path)

        self._save_areas(area_dicts)

        if self.refusals:
            LOG.warning(
                'Refused to overwrite data for %s areas because'
                ' --overwrite is not set.', self.refusals)
        if self.overwrites:
            LOG.info('Overwrote data for %s parking areas.', self.overwrites)
        if self.created:
            LOG.info('Created %s new parking areas.', self.created)
        if (self.created + self.refusals + self.overwrites) == 0:
            LOG.info('Nothing to do.')

        LOG.info('Finished in %.2f seconds.', time.time() - start)

        if self.refusals:
            return False
        else:
            return True

    @transaction.atomic
    def _save_areas(self, area_dicts):
        LOG.info('Saving areas.')
        for area_dict in area_dicts:
            try:
                parking_area = ParkingArea.objects.get(
                    origin_id=area_dict["id"],
                )
                self._update_parking_area(area_dict, parking_area)
            except ParkingArea.DoesNotExist:
                parking_area = self._create_parking_area(area_dict)

            parking_area.save()

    def _create_parking_area(self, area_dict):
        domain = EnforcementDomain.objects.get(code=area_dict["domain"])

        parking_area = ParkingArea(
            origin_id=area_dict["id"],
            domain=domain,
            geom=area_dict["geom"],
            capacity_estimate=area_dict["capacity_estimate"],
            name=area_dict["name"]
        )

        self.created += 1

        return parking_area

    def _update_parking_area(self, area_dict, parking_area):
        new_area = area_dict['geom']
        new_capacity = area_dict['capacity_estimate']

        capacity_differs = parking_area.capacity_estimate != new_capacity
        area_differs = parking_area.geom.wkt != new_area.wkt

        if area_differs or capacity_differs:
            if self.overwrite:
                parking_area.geom = new_area
                parking_area.capacity_estimate = new_capacity
                self.overwrites += 1
            else:
                self.refusals += 1

        return parking_area
