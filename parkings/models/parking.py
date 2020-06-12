from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import localtime, now
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from parkings.models.operator import Operator
from parkings.models.parking_area import ParkingArea
from parkings.models.zone import PaymentZone
from parkings.utils.sanitizing import sanitize_registration_number

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

    def ends_before(self, time):
        return self.exclude(time_end=None).filter(time_end__lte=time)

    def archive(self):
        for parking in self:
            parking.archive()

    def registration_number_like(self, registration_number):
        """
        Filter to parkings having registration number like the given value.

        :type registration_number: str
        :rtype: ParkingQuerySet
        """
        normalized_reg_num = Parking.normalize_reg_num(registration_number)
        return self.filter(normalized_reg_num=normalized_reg_num)


class AbstractParking(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    VALID = 'valid'
    NOT_VALID = 'not_valid'

    region = models.ForeignKey(
        Region, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("region"),
    )
    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.SET_NULL, verbose_name=_("parking area"), null=True,
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
        Operator, on_delete=models.PROTECT, verbose_name=_("operator")
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
        null=True,)
    zone = models.ForeignKey(
        PaymentZone, on_delete=models.PROTECT,
        verbose_name=_("PaymentZone"), null=True, blank=True)
    is_disc_parking = models.BooleanField(verbose_name=_("disc parking"), default=False)

    objects = ParkingQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        start = localtime(self.time_start).replace(tzinfo=None)

        if self.time_end is None:
            return "%s -> (%s)" % (start, self.registration_number)

        if self.time_start.date() == self.time_end.date():
            end = localtime(self.time_end).time().replace(tzinfo=None)
        else:
            end = localtime(self.time_end).replace(tzinfo=None)

        return "%s -> %s (%s)" % (start, end, self.registration_number)


class Parking(AbstractParking):
    class Meta:
        verbose_name = _("parking")
        verbose_name_plural = _("parkings")
        default_related_name = "parkings"

    def archive(self):
        archived_parking = self.make_archived_parking()
        with transaction.atomic():
            archived_parking.save()
            self.delete()
            return archived_parking

    def make_archived_parking(self):
        fields = [field.name for field in self._meta.fields]
        values = {field: getattr(self, field) for field in fields}
        return ArchivedParking(**values)

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
        return Region.objects.filter(geom__intersects=self.location, domain=self.domain).first()

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

        super().save(update_fields=update_fields, *args, **kwargs)

    @classmethod
    def normalize_reg_num(cls, registration_number):
        if not registration_number:
            return ''
        return registration_number.upper().replace('-', '').replace(' ', '')


class ArchivedParking(AbstractParking):
    created_at = models.DateTimeField(verbose_name=_("time created"))
    modified_at = models.DateTimeField(verbose_name=_("time modified"))
    archived_at = models.DateTimeField(auto_now_add=True, verbose_name=_("time archived"))
    sanitized_at = models.DateTimeField(verbose_name=_("time sanitized"), null=True, blank=True)

    class Meta:
        verbose_name = _("archived parking")
        verbose_name_plural = _("archived parkings")
        default_related_name = "archived_parkings"

    def __str__(self):
        return super().__str__() + " (archived)"

    def archive(self):
        return self

    def sanitize(self):
        self.registration_number = sanitize_registration_number(self.registration_number)
        self.normalized_reg_num = sanitize_registration_number(self.normalized_reg_num)
        self.sanitized_at = timezone.now()
        self.save(update_fields=['registration_number', 'normalized_reg_num', 'sanitized_at'])


def _try_cast_int(value):
    try:
        return int(value)
    except ValueError:
        return None
