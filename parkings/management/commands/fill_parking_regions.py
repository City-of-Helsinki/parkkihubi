#!/usr/bin/env python
"""
Fill regions to Parking objects.
"""
import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Parking, Region


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def add_arguments(self, parser):
        parser.add_argument(
            'block_size_target', type=int, nargs='?', default=20000,
            help=(
                "Block size target, "
                "i.e. the number of parkings to process at time"))

    def handle(self, block_size_target, *args, **options):
        verbosity = int(options['verbosity'])
        silent = (verbosity == 0)
        show_info = (self._print_and_flush if not silent else self._null_print)

        regions = Region.objects.all()
        parkings = (
            Parking.objects
            .exclude(location=None)
            .filter(region=None)
            .order_by('created_at'))
        count = parkings.count()

        if not count:
            show_info("Nothing to do")
            return

        block_count = int(max(count / block_size_target, 1))
        start = parkings.first().created_at.replace(microsecond=0, second=0)
        end = parkings.last().created_at
        block_seconds = int((end - start).total_seconds() / block_count) + 1
        block_span = datetime.timedelta(seconds=block_seconds)

        for block_num in range(block_count):
            block_start = start + (block_num * block_span)
            block_end = start + ((block_num + 1) * block_span)
            block = parkings.filter(
                created_at__gte=block_start,
                created_at__lt=block_end)
            block_size = block.count()

            show_info(
                "Processing block {:5d}/{:5d}, size {:6d}, {}--{}".format(
                    block_num + 1, block_count, block_size,
                    block_start, block_end), ending='')

            with transaction.atomic():
                for (n, region) in enumerate(regions):
                    if n % 10 == 0:
                        show_info('.', ending='')
                    in_region = block.filter(location__intersects=region.geom)
                    in_region.update(region=region)
                show_info('', ending='\n')  # Print end of line

    def _print_and_flush(self, *args, ending='\n'):
        self.stdout.write(*args, ending=ending)

    def _null_print(self, *args, ending='\n'):
        pass
