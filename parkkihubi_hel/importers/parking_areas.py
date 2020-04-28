import logging
import time

from django.db import transaction

from parkings.models import EnforcementDomain, ParkingArea

from .wfs_importer import WfsImporter

logger = logging.getLogger(__name__)


class ParkingAreaImporter(WfsImporter):
    """
    Imports parking area data from kartta.hel.fi.

    It should be possible to parallelize this a lot, for instance the wfs in
    _download might be able to use maxfeatures and startindex, while parsing and
    saving can be multithreaded.
    (see getfeature method in
    https://github.com/geopython/OWSLib/blob/master/owslib/feature/wfs200.py)
    However this only takes a few seconds currently and will probably be ran
    at most daily so such optimization is probably premature at this point.
    """
    wfs_typename = 'avoindata:liikennemerkkipilotti_pysakointipaikat'

    def __init__(self, overwrite=False):
        self.overwrite = overwrite
        self.refusals = 0
        self.overwrites = 0
        self.created = 0

    def import_areas(self):
        start = time.time()

        area_dicts = self.download_and_parse()

        self._save_areas(area_dicts)

        if self.refusals:
            logger.warning(
                'Refused to overwrite data for %s areas because'
                ' --overwrite is not set.' % self.refusals
            )
        if self.overwrites:
            logger.info(
                'Overwrote data for %s parking areas.' % self.overwrites
            )
        if self.created:
            logger.info('Created %s new parking areas.' % self.created)
        if (self.created + self.refusals + self.overwrites) == 0:
            logger.info('Nothing to do.')

        logger.info(
            'Finished in %s seconds.' % round(time.time() - start, 2)
        )
        if self.refusals:
            return False
        else:
            return True

    @transaction.atomic
    def _save_areas(self, area_dicts):
        logger.info('Saving areas.')
        for index, area_dict in enumerate(area_dicts):
            """
            get_or_create could be used here, but due to not wanting to
            overwrite data as well as a None check needed this is split into
            two methods instead
            """
            try:
                parking_area = ParkingArea.objects.get(
                    origin_id=area_dict['origin_id'],
                )
                self._update_parking_area(area_dict, parking_area)
            except ParkingArea.DoesNotExist:
                parking_area = self._create_parking_area(area_dict)

            parking_area.save()

    def _create_parking_area(self, area_dict):
        parking_area = ParkingArea(
            domain=EnforcementDomain.get_default_domain(),
            origin_id=area_dict['origin_id'],
            geom=area_dict['geom'],
            capacity_estimate=area_dict['capacity_estimate'],
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

    def _parse_member(self, member):
        """
        Parses the fields from the wfs:member XML element that are currently
        used:
        alue_id > origin_id
        pyspaikkojen_lukumaara_arvio > capacity_estimate
        geom > geom
        and puts them in a dict.

        The field from 'avoindata:paivitetty_tietopalveluun' rougly translates
        to something like 'updated to the service' would be nice to have,
        however it seems to describe the entire system, not individual members
        and is thus nearly useless and is not used here. If at some point the
        dates start reflecting the individual members update time it would be a
        good way to see if a member needs updating or not.

        There is an example file tests/parking_area_importer_data.xml

        :param member: The member XML element.
        :returns: A dict containing the fields origin_id, capacity_estimate
        and geom.
        """
        data = member.find(
            'avoindata:liikennemerkkipilotti_pysakointipaikat',
            self.ns,
        )

        origin_id = data.find('avoindata:alue_id', self.ns).text
        try:
            capacity_estimate = int(
                data.find(
                    'avoindata:pyspaikkojen_lukumaara_arvio',
                    self.ns,
                ).text
            )
        except Exception:
            capacity_estimate = None
        geom = self.get_polygons(data.find('avoindata:geom', self.ns))

        return {
            'origin_id': origin_id,
            'capacity_estimate': capacity_estimate,
            'geom': geom,
        }
