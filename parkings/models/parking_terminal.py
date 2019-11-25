from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class ParkingTerminal(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    number = models.PositiveIntegerField(unique=True, verbose_name=_("number"))
    name = models.CharField(max_length=200, verbose_name=_("name"))
    location = gis_models.PointField(
        null=True, blank=True, verbose_name=_("location"))

    class Meta:
        verbose_name = _("parking terminal")
        verbose_name_plural = _("parking terminals")
        ordering = ('number',)

    @property
    def zone(self):
        # Avoid circular imports by importing this function here.
        from parkings.api.enforcement.check_parking import get_payment_zone
        return get_payment_zone(self.location)

    def __str__(self):
        return "{number}: {name}".format(name=self.name, number=self.number)
