from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min
from django.utils import timezone

from parkings.models import ArchivedParking, Parking


class Command(BaseCommand):
    help = "Archive Parkings older than given number of months."

    verbosity = 1

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
        self._init_timezone()
        self.verbosity = verbosity

        all_parkings = Parking.objects.order_by("time_end", "pk")
        end_time = timezone.now() - relativedelta(months=keep_months)
        to_archive = all_parkings.ends_before(end_time)

        total_count = to_archive.count()
        count = limit if limit and total_count > limit else total_count

        if not count or limit == 0:
            self.stdout.write("Nothing to archive")
            return

        self._show_intention(to_archive, dry_run, count, total_count)

        self._show_stats()

        self.batch_num = 0
        self.batch_count = (count - 1) // batch_size + 1

        try:
            archived = to_archive.archive(
                batch_size=batch_size,
                limit=limit,
                pre_archive_callback=self._show_batch_info,
                post_archive_callback=self._show_batch_time,
                dry_run=dry_run,
            )
        except KeyboardInterrupt:
            self._info("\n  -> Interrupted!\n")
        else:
            self.stdout.write(
                ("Would have archived" if dry_run else "Archived")
                + " {} parkings".format(archived)
            )
        self._show_stats()

    def _init_timezone(self):
        admin_tz = getattr(settings, "ADMIN_TIME_ZONE", None)
        if admin_tz:
            timezone.activate(admin_tz)

    def _show_intention(self, to_archive, dry_run, count, total_count):
        if self.verbosity < 1:
            return

        limits = to_archive.aggregate(a=Min("time_end"), b=Max("time_end"))
        verb = "Would" if dry_run else "Will"
        self._info(
            "{} archive {}{} parkings (end times: {} -- {})...\n",
            verb,
            count,
            " (out of {})".format(total_count) if count != total_count else "",
            _format_ts(limits["a"]),
            _format_ts(limits["b"]),
        )

    def _show_stats(self, models=[ArchivedParking, Parking]):
        if self.verbosity < 1:
            return

        for model in models:
            name = model.__name__
            self.stdout.write("{:15} objects: ".format(name), ending="")
            stats = model.objects.aggregate(
                a=Min("time_end"),
                b=Max("time_end"),
                c=Count("*"),
            )
            self.stdout.write(
                "  Count: {:11,.0f}   End times: {} -- {}".format(
                    stats["c"], _format_ts(stats["a"]), _format_ts(stats["b"])
                )
            )

    def _show_batch_info(self, batch, archived):
        self.pre_batch_time = timezone.now()
        self.pre_batch_archived = archived
        self.batch_num += 1

        self._info(" Batch {:5d} / {:5d}", self.batch_num, self.batch_count),

        if self.verbosity < 2:
            return

        stats = batch.aggregate(a=Min("time_end"), b=Max("time_end"))
        end_ts_str = _format_ts(stats["b"])
        ts_diff_str = _format_ts_diff(stats["b"], stats["a"])
        self._info(" -> {} ({})", end_ts_str, ts_diff_str)

    def _show_batch_time(self, batch, archived):
        if self.verbosity < 1:
            self._info("\r")
            return

        batches_done = self.batch_num
        batch_size = archived - self.pre_batch_archived
        batch_end_time = timezone.now()
        if batches_done > 1:
            time_per_batch = batch_end_time - self.last_batch_end_time
        else:
            time_per_batch = batch_end_time - self.pre_batch_time
        self.last_batch_end_time = batch_end_time
        items_per_second = batch_size / time_per_batch.total_seconds()
        time_left = (self.batch_count - batches_done) * time_per_batch
        eta = _format_ts(timezone.now() + time_left)
        self._info(" {:11.1f} items/s ETA: {}", items_per_second, eta)
        self._info("\r" if time_left else "\n")

    def _info(self, message, *args):
        self.stdout.write(message.format(*args), ending="")
        self.stdout._out.flush()


def _format_ts(timestamp):
    if not timestamp:
        return "....-..-.. ..:..:.. ..:.."
    local_dt = timezone.localtime(timestamp)
    return local_dt.replace(microsecond=0).isoformat().replace("T", " ")


def _format_ts_diff(ts1, ts2):
    if not ts1 or not ts2:
        return "..d ..h ..m ..s"
    d = ts1 - ts2
    return "{} {:2d}h {:2d}m {:2d}s".format(
        "{:2d}d".format(d.days) if d.days else "   ",
        d.seconds // 3600,
        d.seconds // 60 % 60,
        d.seconds % 60,
    )
