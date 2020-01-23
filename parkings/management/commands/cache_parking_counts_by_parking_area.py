"""
Cache parking counts by parking area in its own model.

Precalculating the parking counts enhances the dashboard experience
and makes calculating forecasts of parking occupancies much faster.
"""
from django.core.management.base import BaseCommand

from parkings.forecasts.cache_parking_counts import (
    cache_parking_counts_by_parking_area)


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def handle(self, *args, **options):
        cache_parking_counts_by_parking_area()
