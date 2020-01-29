from django.core.management.base import BaseCommand

from ...importers import PermitAreaImporter


class Command(BaseCommand):
    help = 'Uses the PermitAreaImporter to create permit areas'

    def add_arguments(self, parser):
        parser.add_argument('permitted-user')

    def handle(self, *args, **options):
        permitted_user = options.get('permitted-user', None)
        PermitAreaImporter().import_permit_areas(permitted_user)
