from django.contrib.gis.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from parkings.models.address import Address
from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from parkings.models.operator import Operator


class Parking(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, verbose_name=_("address"), related_name="parkings", null=True, blank=True
    )
    device_identifier = models.CharField(
        max_length=128, verbose_name=_("device identifier"), db_index=True
    )
    location = models.PointField(verbose_name=_("location"))
    operator = models.ForeignKey(
        Operator, on_delete=models.PROTECT, verbose_name=_("operator"), related_name="parkings"
    )
    registration_number = models.CharField(
        max_length=10, db_index=True, verbose_name=_("registration number"),
        validators=[RegexValidator(r"^[A-Z0-9-]+$")]
    )
    resident_code = models.CharField(
        max_length=1, verbose_name=_("resident parking code"), validators=[RegexValidator(r"^[A-Z]{1}$")], blank=True
    )
    special_code = models.CharField(
        max_length=10, verbose_name=_("special parking code"), blank=True,
    )
    time_end = models.DateTimeField(
        verbose_name=_("parking end time"), db_index=True,
    )
    time_start = models.DateTimeField(
        verbose_name=_("parking start time"), db_index=True,
    )
    zone = models.IntegerField(verbose_name=_("zone number"), validators=[
        MinValueValidator(1), MaxValueValidator(3),
    ])

    def __str__(self):
        start = localtime(self.time_start).replace(tzinfo=None)
        end = localtime(self.time_end).time().replace(tzinfo=None)
        return "%s -> %s (%s)" % (start, end, self.registration_number)
