from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .constants import GK25FIN_SRID
from .enforcement_domain import EnforcementDomain
from .mixins import TimestampedModelMixin


class PaymentZone(TimestampedModelMixin):
    domain = models.ForeignKey(
        EnforcementDomain, on_delete=models.PROTECT,
        related_name='payment_zones')
    code = models.CharField(max_length=10)
    number = models.IntegerField(verbose_name=_('zone number'))
    name = models.CharField(max_length=40, verbose_name=_('name'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))

    class Meta:
        unique_together = [('domain', 'code')]
        ordering = ('domain', 'code')

    def __str__(self):
        return self.name

    @property
    def casted_code(self):
        return int(self.code) if self.code.isdigit() else self.code
