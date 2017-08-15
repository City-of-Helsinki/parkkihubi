from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import localtime, now
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from parkings.models.operator import Operator
from parkings.models.parking_area import ParkingArea


class Parking(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    VALID = 'valid'
    NOT_VALID = 'not_valid'

    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.SET_NULL, verbose_name=_("parking area"), null=True, blank=True,
    )
    location = models.PointField(verbose_name=_("location"), null=True, blank=True)
    operator = models.ForeignKey(
        Operator, on_delete=models.PROTECT, verbose_name=_("operator"), related_name="parkings"
    )
    registration_number = models.CharField(max_length=20, db_index=True, verbose_name=_("registration number"))
    time_start = models.DateTimeField(
        verbose_name=_("parking start time"), db_index=True,
    )
    time_end = models.DateTimeField(
        verbose_name=_("parking end time"), db_index=True,
    )
    zone = models.IntegerField(verbose_name=_("zone number"), validators=[
        MinValueValidator(1), MaxValueValidator(3),
    ])

    class Meta:
        verbose_name = _("parking")
        verbose_name_plural = _("parkings")

    def __str__(self):
        start = localtime(self.time_start).replace(tzinfo=None)
        end = localtime(self.time_end).time().replace(tzinfo=None)
        return "%s -> %s (%s)" % (start, end, self.registration_number)

    def get_state(self):
        if self.time_start <= now() <= self.time_end:
            return Parking.VALID
        return Parking.NOT_VALID

    def get_closest_area(self, max_distance=50):
        if self.location:
            location = self.location
        else:
            return None

        closest_area = ParkingArea.objects.annotate(
            distance=Distance('geom', location),
        ).filter(distance__lte=max_distance).order_by('distance').first()
        return closest_area

    def save(self, *args, **kwargs):
        self.parking_area = self.get_closest_area()
        super(Parking, self).save(*args, **kwargs)
