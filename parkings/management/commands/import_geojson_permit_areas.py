from django.core.management.base import BaseCommand

from parkings.importers import PermitAreaImporter


class Command(BaseCommand):
    help = 'Uses the PermitAreaImporter to create permit areas'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file_path')
        parser.add_argument('permitted-user')

    def handle(self, *args, **options):
        file_path = options.get('geojson_file_path', None)
        permitted_user = options.get('permitted-user', None)
        PermitAreaImporter().import_permit_areas(file_path, permitted_user)
