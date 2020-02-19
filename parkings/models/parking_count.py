from django.db import models
from django.utils.translation import ugettext_lazy as _

from .parking_area import ParkingArea
from .region import Region


class ParkingCount(models.Model):
    time = models.DateTimeField(verbose_name=_("time"), db_index=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="parking_counts",
        verbose_name=_("region"),
        null=True,
    )
    parking_area = models.ForeignKey(
        ParkingArea,
        on_delete=models.CASCADE,
        related_name="parking_counts",
        verbose_name=_("parking area"),
        null=True,
    )
    is_forecast = models.BooleanField(default=False, verbose_name=_("is forecast"))
    number = models.IntegerField(verbose_name=_("number"))

    class Meta:
        unique_together = ["time", "region", "parking_area", "is_forecast"]
