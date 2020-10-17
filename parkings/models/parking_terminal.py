from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .enforcement_domain import EnforcementDomain
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class ParkingTerminal(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    domain = models.ForeignKey(EnforcementDomain, on_delete=models.PROTECT,
                               related_name='parking_terminals')
    number = models.CharField(max_length=200, unique=True, verbose_name=_("number"))
    name = models.CharField(max_length=200, verbose_name=_("name"))
    location = gis_models.PointField(
        null=True, blank=True, verbose_name=_("location"))

    class Meta:
        verbose_name = _("parking terminal")
        verbose_name_plural = _("parking terminals")
        ordering = ('number',)

    def __str__(self):
        return "{number}: {name}".format(name=self.name, number=self.number)

    def save(self, *args, **kwargs):
        if not self.domain_id:
            self.domain = EnforcementDomain.get_default_domain()
        super().save(*args, **kwargs)
