from django.core.management.base import BaseCommand

from parkings.importers import ParkingAreaImporter


class Command(BaseCommand):
    help = 'Uses the geojson ParkingAreaImporter to create parking areas'

    def add_arguments(self, parser):
        parser.add_argument('file path', nargs='+', type=str)
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help=('Overwrite existing data. You may want to manually '
                  'inspect the data before doing this. Use with care!'),
        )

    def handle(self, *args, **options):
        file_path = options["file path"][0]
        overwrite = options["overwrite"]

        ParkingAreaImporter(
            file_path=file_path,
            overwrite=overwrite
        ).import_areas()
