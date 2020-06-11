from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from parkings.models import ArchivedParking
from parkings.utils.sanitizing import reset_sanitizing_session


class Command(BaseCommand):
    help = "Sanitize all archived parkings or those that are older than given number of months."

    def add_arguments(self, parser):
        parser.add_argument("months", type=int, nargs='?')
        parser.add_argument('--confirm', action='store_true',)

    def handle(self, *args, **options):
        months = options["months"]
        confirm = options["confirm"]

        parkings_to_sanitize = ArchivedParking.objects.filter(sanitized_at__isnull=True)

        if months:
            end_time = timezone.now() - relativedelta(months=months)
            parkings_to_sanitize = parkings_to_sanitize.ends_before(end_time)

        if confirm:
            choice = input("Do you want to sanitize %s parkings? [Yes/no] " % parkings_to_sanitize.count()).lower()
            if choice != "yes":
                return

        reset_sanitizing_session()  # Make sure the secret is new when starting the sanitizing

        for parking in parkings_to_sanitize:
            parking.sanitize()

        self.stdout.write("Sanitized %s parkings." % parkings_to_sanitize.count())
