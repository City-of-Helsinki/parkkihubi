"""
Train region model with cached parking data.
"""
from django.core.management.base import BaseCommand

from parkings.forecasts.forecast_parking_counts import (
    forecast_region_parking_counts)


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def handle(self, *args, **options):
        forecast_region_parking_counts()
