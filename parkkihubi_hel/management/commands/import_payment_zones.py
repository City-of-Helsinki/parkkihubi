from django.core.management.base import BaseCommand

from ...importers import PaymentZoneImporter


class Command(BaseCommand):
    help = 'Uses the PaymentZoneImporter to import payment zones.'

    def handle(self, *args, **options):
        PaymentZoneImporter().import_payment_zones()
