from django.core.management.base import BaseCommand

from parkings.importers import PermitAreaImporter


class Command(BaseCommand):
    help = 'Uses the PermitAreaImporter to create permit areas'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file_path')
        parser.add_argument('allowed_user', nargs='?', type=str, default=None)
        parser.add_argument('--srid', '-s', type=int, default=None)
        parser.add_argument('--domain', '-d', type=str, default=None)

    def handle(self, *, geojson_file_path, allowed_user=None,
               srid=None, domain=None, **kwargs):
        importer = PermitAreaImporter(srid=srid, default_domain_code=domain)
        importer.import_permit_areas(geojson_file_path, allowed_user)
