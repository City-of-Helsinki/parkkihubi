from django.core.management.base import BaseCommand

from parkings.importers import PermitAreaImporter


class Command(BaseCommand):
    help = 'Uses the PermitAreaImporter to create permit areas'

    def handle(self, *args, **options):
        PermitAreaImporter().import_permit_areas()
