#!/usr/bin/env python
"""
Anonymize the registration numbers from old objects of all models.

What is considered old is defined as something that has ended before a
cutoff date, which is the current time minus the value in the setting
PARKKIHUBI_REGISTRATION_NUMBERS_REMOVABLE_AFTER. Default is 24 hours.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from parkings.anonymization import anonymize_all


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            "-n",
            action="store_true",
            help="Do a dry-run, i.e. nothing is actually anonymized.",
        )
        parser.add_argument(
            "--cutoff-in-hours",
            "-c",
            type=int,
            required=False,
            metavar="N",
            help=(
                "Number of hours to use as the cutoff time. "
                "All items that have ended before this many hours "
                "will be anonymized."
            ),
        )

    def handle(self, dry_run, cutoff_in_hours, *args, **options):
        if cutoff_in_hours is not None:
            cutoff = timezone.now() - timedelta(hours=cutoff_in_hours)
        else:
            cutoff = None

        anonymize_all(cutoff=cutoff, dry_run=dry_run)
