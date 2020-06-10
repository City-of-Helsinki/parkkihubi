from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from parkings.models import Parking


class Command(BaseCommand):
    help = "Archive Parkings older than given number of months."

    def add_arguments(self, parser):
        parser.add_argument("months", type=int)
        parser.add_argument('--confirm', action='store_true',)

    def handle(self, *args, **options):
        months = options["months"]
        confirm = options["confirm"]
        end_time = timezone.now() - relativedelta(months=months)
        parkings_to_archive = Parking.objects.ends_before(end_time)

        if confirm:
            choice = input("Do you want to archive %s parkings? [Yes/no] " % parkings_to_archive.count()).lower()
            if choice != "yes":
                return

        parkings_to_archive.archive()
        self.stdout.write("Archived %s parkings." % parkings_to_archive.count())
