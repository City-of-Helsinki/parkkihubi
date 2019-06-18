import logging

from django.db import transaction

from parkings.models import PaymentZone

from .utils import BaseImporterMixin

logger = logging.getLogger(__name__)


class PaymentZoneImporter(BaseImporterMixin):

    """
    Imports paymentzones data from kartta.hel.fi.
    """

    def __init__(self, overwrite=False):
        super().__init__(overwrite=overwrite)
        self.typename = 'Pysakoinnin_maksuvyohykkeet_alue'

    def import_payment_zones(self):
        response = self._download(self.typename)
        payment_zones_dict = None

        if response is not None:
            payment_zones_dict = self._parse_data(response)
        else:
            logger.error("Download failed.")
            return False

        if payment_zones_dict is not None:
            self._save_payment_zones(payment_zones_dict)

        if self.created:
            logger.info('Created %s new payment zone.' % self.created)

    @transaction.atomic
    def _save_payment_zones(self, payment_zones_dict):
        logger.info('Saving payment zones.')

        payment_zone_ids = []
        for payment_dict in payment_zones_dict:
            payment_zone, _ = PaymentZone.objects.update_or_create(
                number=payment_dict['number'],
                defaults=payment_dict)
            payment_zone_ids.append(payment_zone.pk)
            self.created += 1
        PaymentZone.objects.exclude(pk__in=payment_zone_ids).delete()

    def _parse_member(self, member):
        data = member.find(
            'avoindata:Pysakoinnin_maksuvyohykkeet_alue',
            self.ns,
        )
        number = data.find('avoindata:vyohykkeen_nro', self.ns).text
        name = data.find('avoindata:nimi', self.ns).text
        geom = self.get_polygons(data.find('avoindata:geom', self.ns))

        return {
            'name': name,
            'number': number,
            'geom': geom,
        }
