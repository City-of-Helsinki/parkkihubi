from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from parkings.models import Parking


class Command(BaseCommand):
    help = "Archive Parkings older than given number of months."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            "-l",
            type=int,
            metavar="N",
            help=(
                "Number of parkings to archive. This will archive "
                "at most N oldest parkings."
            ),
        )
        parser.add_argument(
            "--keep-months",
            "-m",
            type=int,
            required=True,
            metavar="N",
            help=(
                "Number of months to keep untouched. This will archive "
                "all parkings that are older than N months."
            ),
        )
        parser.add_argument(
            "--dry-run",
            "-n",
            action="store_true",
            help="Do a dry-run, i.e. nothing is actually archived.",
        )
        parser.add_argument(
            "--batch-size",
            "-b",
            type=int,
            default=10000,
            help="Batch size: How many parkings to process at a time",
        )

    def handle(
        self,
        limit=None,
        keep_months=None,
        batch_size=50000,
        dry_run=False,
        verbosity=1,
        **kwargs
    ):
        all_parkings = Parking.objects.order_by("time_end", "pk")
        end_time = timezone.now() - relativedelta(months=keep_months)
        to_archive = all_parkings.ends_before(end_time)

        total_count = to_archive.count()
        count = limit if limit and total_count > limit else total_count

        if not count or limit == 0:
            self.stdout.write("Nothing to archive")
            return
        else:
            self.stdout.write("Parkings to archive: {}".format(count))

        archived = to_archive.archive(
            batch_size=batch_size,
            limit=limit,
            dry_run=dry_run,
        )
        self.stdout.write(
            ("Would have archived" if dry_run else "Archived")
            + " {} parkings".format(archived)
        )
