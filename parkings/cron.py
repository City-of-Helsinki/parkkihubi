from django.conf import settings
from django_cron import CronJobBase, Schedule

from parkings.forecasts.cache_parking_counts import (
    cache_parking_counts_by_region)
from parkings.forecasts.forecast_parking_counts import (
    forecast_region_parking_counts)


class CacheRegionParkingCountsCronJob(CronJobBase):
    RUN_AT_TIMES = ["0:00"]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = "parkings.CacheRegionParkingCountsCronJob"

    def do(self):
        if settings.ENABLE_FORECAST_CRON_JOB:
            cache_parking_counts_by_region()


class ForecastRegionParkingsCronJob(CronJobBase):
    RUN_AT_TIMES = ["3:00"]

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = "parkings.ForecastRegionParkingsCronJob"

    def do(self):
        if settings.ENABLE_FORECAST_CRON_JOB:
            forecast_region_parking_counts()
