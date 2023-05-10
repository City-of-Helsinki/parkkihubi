from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import WGS84_SRID
from .mixins import AnonymizableRegNumQuerySet
from .parking import Parking


class ParkingCheckQuerySet(AnonymizableRegNumQuerySet, models.QuerySet):
    def created_before(self, time):
        return self.filter(created_at__lt=time)


class ParkingCheck(models.Model):
    """
    A performed check of allowance of a parking.

    An instance is stored for each checking action done via the
    check_parking endpoint.  Each instance records the query parameters
    and the results of the check.
    """
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_("time created"))
    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False,
        verbose_name=_("performer"),
        help_text=_("User who performed the check"))

    # Query parameters
    time = models.DateTimeField(verbose_name=_("time"))
    time_overridden = models.BooleanField(
        verbose_name=_("time was overridden"))
    registration_number = models.CharField(
        max_length=20, verbose_name=_("registration number"))
    location = gis_models.PointField(
        srid=WGS84_SRID, verbose_name=_("location"))

    # Results
    result = JSONField(
        blank=True, encoder=DjangoJSONEncoder, verbose_name=_("result"))
    allowed = models.BooleanField(verbose_name=_("parking was allowed"))
    found_parking = models.ForeignKey(
        Parking, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_("found parking"))

    objects = ParkingCheckQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at", "-id")
        verbose_name = _("parking check")
        verbose_name_plural = _("parking checks")

    def __str__(self):
        location_data = (self.result.get("location")
                         if isinstance(self.result, dict) else None) or {}
        return "[{t}] {time}{o} {coords} Z{zone}/{area} {regnum}: {ok}".format(
            t=self.created_at,
            time=self.time,
            o="*" if self.time_overridden else " ",
            coords=_format_coordinates(self.location),
            zone=location_data.get("payment_zone") or "-",
            area=location_data.get("permit_area") or "-",
            regnum=self.registration_number,
            ok="OK" if self.allowed else "x")


def _format_coordinates(location, prec=5):
    assert location.srid == WGS84_SRID
    longitude = location.coords[0]
    latitude = location.coords[1]
    e_or_w = "E" if longitude >= 0.0 else "W"
    n_or_s = "N" if latitude >= 0.0 else "S"
    return "{latitude:.{prec}f}{n_or_s} {longitude:.{prec}f}{e_or_w}".format(
        latitude=abs(latitude), longitude=abs(longitude),
        prec=prec, n_or_s=n_or_s, e_or_w=e_or_w)
