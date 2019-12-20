from django.core.management.base import BaseCommand

from ...importers import ParkingAreaImporter


class Command(BaseCommand):
    help = 'Uses the parking area importer to create and update parking areas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help=('Overwrite existing data. You may want to manually '
                  'inspect the data before doing this. Use with care!'),
        )

    def handle(self, *args, **options):
        ParkingAreaImporter(
            overwrite=options['overwrite'],
        ).import_areas()
