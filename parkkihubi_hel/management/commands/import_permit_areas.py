from django.core.management.base import BaseCommand

from ...importers import PermitAreaImporter


class Command(BaseCommand):
    help = 'Uses the PermitAreaImporter to create permit areas'

    def add_arguments(self, parser):
        parser.add_argument('allowed_user', nargs='?', type=str, default=None)

    def handle(self, *args, allowed_user=None, **options):
        PermitAreaImporter().import_permit_areas(allowed_user)
