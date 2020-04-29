from django.core.management.base import BaseCommand

from parkings.importers import PermitAreaImporter


class Command(BaseCommand):
    help = 'Uses the PermitAreaImporter to create permit areas'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file_path')
        parser.add_argument('permitted_user')
        parser.add_argument('--srid', '-s', type=int, default=None)
        parser.add_argument('--domain', '-d', type=str, default=None)

    def handle(self, *, geojson_file_path, permitted_user,
               srid=None, domain=None, **kwargs):
        importer = PermitAreaImporter(srid=srid, default_domain_code=domain)
        importer.import_permit_areas(geojson_file_path, permitted_user)
