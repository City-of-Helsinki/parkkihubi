import logging

from django.db import transaction

from parkings.models import EnforcementDomain, PaymentZone

from .wfs_importer import WfsImporter

logger = logging.getLogger(__name__)


class PaymentZoneImporter(WfsImporter):
    """
    Imports paymentzones data from kartta.hel.fi.
    """
    wfs_typename = 'Pysakoinnin_maksuvyohykkeet_alue'

    def import_payment_zones(self):
        payment_zone_dicts = self.download_and_parse()
        count = self._save_payment_zones(payment_zone_dicts)
        logger.info('Created or updated {} payment zones'.format(count))

    @transaction.atomic
    def _save_payment_zones(self, payment_zone_dicts):
        logger.info('Saving payment zones.')
        count = 0
        payment_zone_ids = []
        for payment_dict in payment_zone_dicts:
            payment_zone, _ = PaymentZone.objects.update_or_create(
                domain=EnforcementDomain.get_default_domain(),
                code=payment_dict['number'],
                number=payment_dict['number'],
                defaults=payment_dict)
            payment_zone_ids.append(payment_zone.pk)
            count += 1
        PaymentZone.objects.exclude(pk__in=payment_zone_ids).delete()
        return count

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
