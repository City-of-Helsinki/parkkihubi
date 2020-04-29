from django.core.management.base import BaseCommand

from parkings.importers import PaymentZoneImporter


class Command(BaseCommand):
    help = 'Uses the PaymentZoneImporter to import payment zones.'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file_path')
        parser.add_argument('--srid', '-s', type=int, default=None)
        parser.add_argument('--domain', '-d', type=str, default=None)

    def handle(self, *, geojson_file_path,
               srid=None, domain=None, **kwargs):
        importer = PaymentZoneImporter(srid=srid, default_domain_code=domain)
        importer.import_payment_zones(geojson_file_path)
