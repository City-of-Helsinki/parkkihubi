from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import localtime, now
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from parkings.models.operator import Operator
from parkings.models.parking_area import ParkingArea

from .enforcement_domain import EnforcementDomain
from .parking_terminal import ParkingTerminal
from .region import Region

Q = models.Q


class ParkingQuerySet(models.QuerySet):
    def valid_at(self, time):
        """
        Filter to parkings which are valid at given time.

        :type time: datetime.datetime
        :rtype: ParkingQuerySet
        """
        return self.starts_before(time).ends_after(time)

    def starts_before(self, time):
        return self.filter(time_start__lte=time)

    def ends_after(self, time):
        return self.filter(Q(time_end__gte=time) | Q(time_end=None))

    def registration_number_like(self, registration_number):
        """
        Filter to parkings having registration number like the given value.

        :type registration_number: str
        :rtype: ParkingQuerySet
        """
        normalized_reg_num = Parking.normalize_reg_num(registration_number)
        return self.filter(normalized_reg_num=normalized_reg_num)


class Parking(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    VALID = 'valid'
    NOT_VALID = 'not_valid'

    region = models.ForeignKey(
        Region, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='parkings', verbose_name=_("region"),
    )
    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.SET_NULL, verbose_name=_("parking area"), related_name='parkings', null=True,
        blank=True,
    )
    terminal_number = models.CharField(
        max_length=50,  blank=True,
        verbose_name=_("terminal number"),
    )
    terminal = models.ForeignKey(
        ParkingTerminal, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("terminal"),
    )
    location = models.PointField(verbose_name=_("location"), null=True, blank=True)
    operator = models.ForeignKey(
        Operator, on_delete=models.PROTECT, verbose_name=_("operator"), related_name="parkings"
    )
    registration_number = models.CharField(max_length=20, db_index=True, verbose_name=_("registration number"))
    normalized_reg_num = models.CharField(
        max_length=20, db_index=True,
        verbose_name=_("normalized registration number"),
    )
    time_start = models.DateTimeField(
        verbose_name=_("parking start time"), db_index=True,
    )
    time_end = models.DateTimeField(
        verbose_name=_("parking end time"), db_index=True, null=True, blank=True,
    )
    domain = models.ForeignKey(
        EnforcementDomain, on_delete=models.PROTECT,
        related_name='parkings', null=True,)
    zone = models.IntegerField(
        verbose_name=_("zone number"),
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(3), ]
    )
    is_disc_parking = models.BooleanField(verbose_name=_("disc parking"), default=False)

    objects = ParkingQuerySet.as_manager()

    class Meta:
        verbose_name = _("parking")
        verbose_name_plural = _("parkings")

    def __str__(self):
        start = localtime(self.time_start).replace(tzinfo=None)

        if self.time_end is None:
            return "%s -> (%s)" % (start, self.registration_number)

        if self.time_start.date() == self.time_end.date():
            end = localtime(self.time_end).time().replace(tzinfo=None)
        else:
            end = localtime(self.time_end).replace(tzinfo=None)

        return "%s -> %s (%s)" % (start, end, self.registration_number)

    def get_state(self):
        current_timestamp = now()

        if self.time_start > current_timestamp:
            return Parking.NOT_VALID

        if self.time_end and self.time_end < current_timestamp:
            return Parking.NOT_VALID

        return Parking.VALID

    def get_region(self):
        if not self.location:
            return None
        return Region.objects.filter(geom__intersects=self.location).first()

    def get_closest_area(self, max_distance=50):
        if self.location:
            location = self.location
        else:
            return None

        closest_area = ParkingArea.objects.annotate(
            distance=Distance('geom', location),
        ).filter(distance__lte=max_distance).order_by('distance').first()
        return closest_area

    def save(self, update_fields=None, *args, **kwargs):
        if not self.domain_id:
            self.domain = EnforcementDomain.get_default_domain()

        if not self.terminal and self.terminal_number:
            self.terminal = ParkingTerminal.objects.filter(
                number=_try_cast_int(self.terminal_number)).first()

        if self.terminal and not self.location:
            self.location = self.terminal.location

        if update_fields is None or 'region' in update_fields:
            self.region = self.get_region()
        if update_fields is None or 'parking_area' in update_fields:
            self.parking_area = self.get_closest_area()

        if update_fields is None or 'normalized_reg_num' in update_fields:
            self.normalized_reg_num = (
                self.normalize_reg_num(self.registration_number))

        super(Parking, self).save(update_fields=update_fields, *args, **kwargs)

    @classmethod
    def normalize_reg_num(cls, registration_number):
        if not registration_number:
            return ''
        return registration_number.upper().replace('-', '').replace(' ', '')


def _try_cast_int(value):
    try:
        return int(value)
    except ValueError:
        return None
