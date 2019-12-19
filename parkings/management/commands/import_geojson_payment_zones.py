from django.core.management.base import BaseCommand

from parkings.importers import PaymentZoneImporter


class Command(BaseCommand):
    help = 'Uses the PaymentZoneImporter to import payment zones.'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file_path')

    def handle(self, *args, **options):
        file_path = options.get('geojson_file_path', None)
        PaymentZoneImporter().import_payment_zones(file_path)
